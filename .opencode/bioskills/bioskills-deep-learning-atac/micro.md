## Tool Selection and Environment Setup

_modules: tool-selection, environment-setup, version-check_

```bash
# Verify installed versions and CLI flags before use
pip show chrombpnet bpnet-lite tangermeme modisco-lite captum tensorflow kipoi
chrombpnet --version && chrombpnet --help
modisco --help 2>/dev/null | head -40

# Decision tree (apply by goal, do not execute as a script):
# - Score 100 GWAS SNPs for chromatin effects  -> pre-trained chromBPNet + tangermeme
# - Score 1 lead SNP at high resolution         -> chromBPNet + tangermeme + ISM saturation map
# - Discover TF motifs from a new cell type      -> chromBPNet train + DeepLIFT + TF-MoDISco-lite
# - Predict accessibility in unobserved cell type-> EnFormer (ENCODE types) or scBasset (sc states)
# - Bias-correct low-input ATAC before footprint -> chromBPNet bias model -> TOBIAS or corrected track
# - Cell-type-specific enhancer prediction       -> chromBPNet per cell type + ISM at candidate loci
# - Replace TOBIAS bias correction               -> chromBPNet corrected bigWig -> TOBIAS ScoreBigwig
```

## Data Preparation and Chromosome Splits

_modules: data-prep, chromosome-splits, qc_

```bash
# Inputs expected on disk:
#   atac.bam            (coordinate-sorted, deduplicated, indexed)
#   hg38.fa + hg38.fa.fai
#   hg38.chrom.sizes
#   peaks.narrowPeak    (pre-filtered: drop chrM, blacklist, empty entries)
#   nonpeaks.bed        (background regions)

# Generate train / valid / test chromosome splits -> JSON fold file
chrombpnet prep splits \
    -c hg38.chrom.sizes \
    -tcr chr1 chr3 chr6 \
    -vcr chr8 chr20 \
    -op splits/fold_0
# Train chromosomes are auto-inferred (whatever is not in -tcr/-vcr).
# NOTE: the `-tecr` flag does NOT exist; do not pass it.
```

## Bias Model Training

_modules: bias-model, tn5-bias, cnn-training_

```bash
# Train bias model from background regions
chrombpnet bias pipeline \
    -ibam atac.bam \
    -d ATAC \
    -g hg38.fa \
    -c hg38.chrom.sizes \
    -p peaks.narrowPeak \
    -n nonpeaks.bed \
    -fl splits/fold_0.json \
    -b 0.5 \
    -o bias_model/
# Output: bias_model/bias.h5
# -b 0.5 is the bias scaling factor (0.5-1.0 recommended).
# If training fails silently / bias.h5 missing: re-run with verbose, check BAM size.
# If OOM: --batch-size 64 or smaller, reduce --num-filters.
```

## Accessibility Model Training

_modules: accessibility-model, cnn-training, bias-correction_

```bash
# Train accessibility model with bias correction
chrombpnet pipeline \
    -ibam atac.bam \
    -d ATAC \
    -g hg38.fa \
    -c hg38.chrom.sizes \
    -p peaks.narrowPeak \
    -n nonpeaks.bed \
    -fl splits/fold_0.json \
    -b bias_model/bias.h5 \
    -o output/
# Output: output/chrombpnet_no_bias.h5 (bias-free model for variant scoring + contributions)
# ~24h on 1 A100, 80 GB RAM per cell type.
# If model collapses (constant predicted profile): increase epochs, verify peaks non-empty.
# If not converging: pre-filter chrM/blacklist from peaks (chromBPNet does not auto-filter).
```

## Variant Effect Prediction

_modules: variant-effect, ism, tangermeme, variant-scorer_

```bash
# Path A: standalone variant-scorer repo (NOT a chrombpnet subcommand)
git clone https://github.com/kundajelab/variant-scorer
python variant-scorer/src/variant_scoring.py \
    --model output/chrombpnet_no_bias.h5 \
    --list variants.tsv \
    --genome hg38.fa \
    --chrom_sizes hg38.chrom.sizes \
    --out_prefix variants_predicted
# Output: variants_predicted.variant_scores.tsv (per-SNP log2FC magnitudes)
# Verify exact flags with: python variant_scoring.py --help
```

```python
# Path B: tangermeme marginal substitution_effect for fast batch scoring
import numpy as np
from tangermeme.variant_effect import substitution_effect
from tangermeme.predict import predict

# Load pre-trained chromBPNet model (Keras .h5 or PyTorch state_dict).
# `load_chrombpnet_model` is a placeholder -- substitute the actual loader for the
# installed version (e.g. tf.keras.models.load_model + tangermeme adapter, or torch.load).
model = load_chrombpnet_model('output/chrombpnet_no_bias.h5')

# substitution_effect: per-SNP ref vs alt prediction across a sequence window.
# X shape (N, 4, L); substitutions is a sparse-COO tensor of shape (-1, 3) where each
# row is [example_idx, position, new_base_idx] (new_base_idx 0-3 for ACGT).
y_ref, y_alt = substitution_effect(model, X, substitutions)
log2fc = np.log2(y_alt.sum(axis=-1) / y_ref.sum(axis=-1))
# |log2fc| > 1 typical for strong-effect SNPs in regulatory regions.

# For motif marginalization (insert a candidate motif into background sequences):
# from tangermeme.marginalize import marginalize
# from tangermeme.utils import one_hot_encode
# y = marginalize(model, X, motif)  # motif: one-hot tensor (-1, 4, motif_length)
# NOTE: `marginal_predict` is NOT a real function name; verify with help(marginalize).
```

## Motif Discovery with DeepLIFT and TF-MoDISco

_modules: deeplift, shap, tfmodisco, motif-discovery_

```bash
# 1. Generate one-hot sequence + SHAP/DeepLIFT contribution arrays from chromBPNet.
#    chrombpnet contribs_bw writes hypothetical contributions; convert to numpy
#    via shap_to_modisco -> ohe.npz, shap.npz

# 2. Run TF-MoDISco-lite via its CLI
modisco motifs \
    -s ohe.npz \
    -a shap.npz \
    -n 2000 \
    -w 500 \
    -o modisco_results.h5
# -n 2000 caps seqlets per metacluster; -w 500 is the sliding-window length.

# 3. Generate HTML report with discovered motifs matched to known databases
modisco report \
    -i modisco_results.h5 \
    -o modisco_report/ \
    -m motifs_meme.txt \
    -s modisco_report/
# motifs_meme.txt = JASPAR or HOCOMOCO MEME-format database for annotation.
# If too many small clusters: tighten target_seqlet_fdr to 0.01, or increase flank_size.
# ~6h on 32 CPU cores for 1M peaks.
```

## Cross-Tool Validation and Reconciliation

_modules: validation, reconciliation, cross-tool_

```python
# Reconciliation checklist (apply as a review step, not a single script):
#
# 1. Variant effect: require agreement across TWO approaches before calling high-confidence.
#    - chromBPNet (1-2 kb context) + EnFormer/Borzoi (196 kb context)
#    - Single-tool calls -> report as exploratory only.
# 2. Motif discovery: cross-check TF-MoDISco clusters against JASPAR/HOCOMOCO.
#    - Divergent motifs may be composites/cooperative -- not necessarily wrong.
# 3. Bias correction: chromBPNet vs TOBIAS ATACorrect.
#    - chromBPNet more accurate but slower; TOBIAS publishable for standard use.
# 4. Peak vs variant disagreement:
#    - chromBPNet strong effect + no MACS peak -> latent regulatory potential;
#      trust for variant effect, NOT for peak calling.
# 5. Context-window disagreement (chromBPNet vs EnFormer at same locus):
#    - Both can be correct at different scales; report both with context size.
```
