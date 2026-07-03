## Signal Track Preparation

_modules: signal-tracks, normalization, bigwig_

```bash
# Generate ATAC and H3K27ac signal tracks (BAM -> bigWig) with RPGC normalization
bamCoverage --bam atac.bam --outFileName atac.bw --binSize 50 --normalizeUsing RPGC \
    --effectiveGenomeSize 2913022398 --numberOfProcessors 8

bamCoverage --bam h3k27ac.bam --outFileName h3k27ac.bw --binSize 50 --normalizeUsing RPGC \
    --effectiveGenomeSize 2913022398 --numberOfProcessors 8

# Optional quantile normalization when H3K27ac and ATAC depths differ
# (apply via ABC --qnorm with a reference file at the neighborhoods step)
```

## Candidate Enhancer Definition

_modules: peak-calling, enhancer-candidates, promoter-filter_

```bash
# Define enhancer candidates from MACS narrowPeak; filter to non-promoter regions
bedtools intersect -v -a atac_peaks.narrowPeak -b promoter_regions.bed > candidate_enhancers.bed
```

## ABC Scoring Pipeline

_modules: abc, activity, hi-c-contact, scoring_

```bash
# Run ABC neighborhoods (compute Activity per candidate)
# Script path: legacy ABC = src/run.neighborhoods.py; Snakemake-based modern = workflow/scripts/run.neighborhoods.py
python /path/ABC-Enhancer-Gene-Prediction/workflow/scripts/run.neighborhoods.py \
    --candidate_enhancer_regions candidate_enhancers.bed \
    --genes refseq_protein_coding.bed \
    --H3K27ac h3k27ac.bw \
    --DHS atac.bw \
    --chrom_sizes hg38.chrom.sizes \
    --ubiquitously_expressed_genes Genes.ubiquitously_expressed.txt \
    --cellType MyCellType \
    --outdir abc_out/

# Run ABC predictions (Activity * Contact, normalized over cis window)
python /path/ABC-Enhancer-Gene-Prediction/workflow/scripts/predict.py \
    --enhancers abc_out/EnhancerList.txt \
    --genes abc_out/GeneList.txt \
    --HiCdir hic_data/ \
    --hic_resolution 5000 \
    --score_column ABC.Score \
    --threshold 0.02 \
    --cellType MyCellType \
    --outdir abc_out/Predictions/

# Output: EnhancerPredictionsAllPutative.txt with per-pair ABC scores
# ABC.Score >= 0.02 = high-confidence (Fulco 2019); >= 0.04 = stricter precision cut
```

## ENCODE-rE2G Alternative

_modules: encode-re2g, logistic-regression, snakemake_

```bash
# Snakemake-based ENCODE-rE2G; clone the repo
git clone https://github.com/EngreitzLab/ENCODE_rE2G
cd ENCODE_rE2G

# Edit config.yaml with cell type, ATAC, H3K27ac paths
# Run with cell-type-matched logistic regression weights; use no-hic model when Hi-C unavailable
snakemake --use-conda --cores 16 \
    --config cell_type=K562 \
             atac_bw=atac.bw \
             h3k27ac_bw=h3k27ac.bw \
             hic_directory=hic_data/

# Output: scored_predictions.tsv.gz with per-pair scores and binarized predictions
# Pre-trained models: https://github.com/EngreitzLab/ENCODE_rE2G/tree/main/models
```

## Multi-Method Integration

_modules: integration, intersection, hichip_

```python
import pandas as pd

abc = pd.read_csv('abc_predictions.tsv', sep='\t')
re2g = pd.read_csv('encode_re2g.tsv.gz', sep='\t')
hichip = pd.read_csv('fithichip_loops.bedpe', sep='\t', header=None,
                     names=['chr1','s1','e1','chr2','s2','e2','name','score'])

# High-confidence intersection: ABC >= 0.02 AND ENCODE-rE2G >= 0.5
high_conf = abc[abc['ABC.Score'] >= 0.02].merge(
    re2g[re2g['re2g_score'] >= 0.5],
    on=['enhancer_id', 'gene'])

# Add HiChIP loop support flag for triple-method evidence
hichip_anchors = ...    # extract enhancer/gene pairs from HiChIP loops
high_conf['hichip_support'] = high_conf['enhancer_id'].isin(hichip_anchors)
```

## Experimental Validation

_modules: crispr, validation, flowfish_

```bash
# CRISPRi-FlowFISH validation workflow (Fulco 2019 gold-standard)
# 1. Design sgRNAs tiling each candidate enhancer
# 2. Transduce CRISPRi-expressing cells; FACS by gene expression
#    (FlowFISH for endogenous targets; reporter for ectopic)
# 3. Sequence sgRNAs in low- vs high-expression bins
# 4. Compute log2 enrichment per sgRNA; meta-test across sgRNAs per enhancer

# Significance threshold: 2-fold expression decrease (p < 0.05) confirms regulation

# Publication-grade benchmarking (ENCODE 4):
#   - Sensitivity/specificity vs published CRISPRi catalogs
#     (Fulco 2019 K562; Gasperini 2019; Schraivogel 2020 multi-cell-type)
#   - Effect-size correlation: predicted score vs observed expression effect
#   - Distance bias check: predictors must not over-rank close-distance pairs
```
