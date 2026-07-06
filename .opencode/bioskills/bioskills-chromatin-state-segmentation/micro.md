## Preparation & Binarization

_modules: binarization, input-preparation, chip-seq_

```bash
# Build cellMarkFileTable: cell_type<TAB>mark<TAB>file<TAB>(optional control)
cat > cellMarkFileTable.txt << EOF
GM12878	H3K4me3	gm12878_h3k4me3.bam	gm12878_input.bam
GM12878	H3K27me3	gm12878_h3k27me3.bam	gm12878_input.bam
GM12878	H3K27ac	gm12878_h3k27ac.bam	gm12878_input.bam
GM12878	H3K4me1	gm12878_h3k4me1.bam	gm12878_input.bam
GM12878	H3K36me3	gm12878_h3k36me3.bam	gm12878_input.bam
EOF

# Index BAMs first (BinarizeBam is very slow without indexes)
samtools index gm12878_h3k4me3.bam

# Binarize BAMs into 200 bp bins; emission = whether mark exceeds Poisson threshold.
# Use sonicated input as control (NOT IgG) for histone marks.
java -mx16G -jar ChromHMM.jar BinarizeBam \
    -b 200 \
    chromsizes_hg38.txt \
    bam_dir/ \
    cellMarkFileTable.txt \
    binarized_output/
```

Key parameters: `-b 200` bin size (reduce to 100 or 50 for sharper boundaries at higher memory cost); `chromsizes_hg38.txt` chromosome sizes; `bam_dir/` directory of aligned BAMs; `cellMarkFileTable.txt` the panel table; `binarized_output/` destination for per-chromosome `_binary.txt` files.

## Model Learning

_modules: hmm, learnmodel, state-count-selection_

```bash
# Train HMM with N states; common choices: 15, 18, 25
#   15 states: Ernst & Kellis 2011 / Roadmap canonical (5 core marks)
#   18 states: extends with bivalent states, fine enhancer subtypes (5-7 marks)
#   25 states: Roadmap extended; cross-cell-type compatibility (6+ marks)
#   8-10 states: initial exploration / small mark panel (3-5 marks)
java -mx16G -jar ChromHMM.jar LearnModel \
    -p 8 \
    binarized_output/ \
    model_15state/ \
    15 \
    hg38
```

Outputs in `model_15state/`: `model_15state.txt` (emission + transition matrices), `emissions_15.png`, `transitions_15.png`, per-chromosome `_segments.bed` (state assignments). LearnModel automatically runs OverlapEnrichment + NeighborhoodEnrichment if anchor files are provided alongside. Practical guidance: train at N=15, 18, 25; compare emission matrices; choose the smallest N where biology is interpretable.

## State Interpretation

_modules: emission-matrix, state-annotation, roadmap-states_

```text
# Roadmap 15-state canonical assignments
# (map by emission similarity, NOT by state number — independently trained
#  models do not share label ordering with Roadmap):
#   1_TssA      Active TSS            (high H3K4me3, H3K27ac)
#   2_TssAFlnk  Flanking TSS          (H3K4me3, H3K27ac, lower)
#   3_TxFlnk    Transcript flanking
#   4_Tx        Strong transcription  (H3K36me3, H3K79me2 if available)
#   5_TxWk      Weak transcription
#   6_EnhG      Enhancer in gene body (H3K4me1, H3K27ac)
#   7_Enh       Generic enhancer      (H3K4me1, H3K27ac)
#   8_ZNF/Rpts  Zinc-finger / repeats
#   9_Het       Heterochromatin       (H3K9me3)
#   10_TssBiv   Bivalent TSS          (H3K4me3 + H3K27me3)
#   11_BivFlnk  Bivalent flanking
#   12_EnhBiv   Bivalent enhancer     (H3K4me1 + H3K27me3)
#   13_ReprPC   Polycomb-repressed    (H3K27me3)
#   14_ReprPCWk Weak Polycomb
#   15_Quies    Quiescent             (no signal)
```

Inspect `emissions_15.png`: confirm states separate into distinct categories. Redundant emission profiles at high N => over-segmentation (reduce N). To compare against Roadmap/full-stack references, match states by emission similarity, not by index.

## Functional Enrichment

_modules: enrichment, overlap-enrichment, neighborhood-enrichment_

```bash
# OverlapEnrichment: enrichment of each state for external feature sets (BED anchors)
java -mx16G -jar ChromHMM.jar OverlapEnrichment \
    model_15state/GM12878_15_segments.bed \
    /path/to/anchor_files/ \
    enrichment_output/GM12878 \
    -labels

# NeighborhoodEnrichment: enrichment relative to anchor positions (e.g., TSS)
java -mx16G -jar ChromHMM.jar NeighborhoodEnrichment \
    model_15state/GM12878_15_segments.bed \
    /path/to/tss_anchors.txt \
    enrichment_output/GM12878_TSS \
    -labels
```

Anchor files: BED files of features (CGIs, repeats, conserved elements) for OverlapEnrichment; position files for NeighborhoodEnrichment. The `-labels` flag adds human-readable state labels to output.

## Alternative Segmentation Approaches

_modules: segway, episegmix, full-stack, epilogos, ideas_

```bash
# --- Segway: continuous-signal DBN segmentation (bigWig input) ---
segway train \
    --num-labels 25 \
    --num-instances 3 \
    --resolution 100 \
    chromsizes_hg38.bed \
    h3k4me3.bw h3k27ac.bw h3k4me1.bw h3k36me3.bw h3k27me3.bw \
    --traindir traindir/

segway posterior --traindir traindir/ --identifydir identifydir/ \
    chromsizes_hg38.bed \
    h3k4me3.bw h3k27ac.bw h3k4me1.bw h3k36me3.bw h3k27me3.bw
# Output: identifydir/segway.bed

# --- Full-stack ChromHMM (Vu & Ernst 2022): apply precomputed 100-state model ---
# Precomputed model: github.com/ernstlab/full_stack_ChromHMM_annotations
java -mx16G -jar ChromHMM.jar MakeSegmentation \
    full_stack_model_100states.txt \
    binarized_sample/ \
    full_stack_output/

# --- EpiLogos: visualize existing segmentations across biosamples ---
# Web: https://epilogos.altius.org/   Local: github.com/meuleman/epilogos

# --- EpiSegMix (2024): flexible read-count HMM with duration modeling ---
# --- IDEAS: cell-type-aware joint segmentation across cell types ---
```

Trade-off notes: Segway uses continuous bigWig (more information per region) but has more complex training than ChromHMM. Full-stack MakeSegmentation requires the exact same marks/ordering as the precomputed model. EpiLogos is visualization only, not a segmentation method.

## Troubleshooting & Validation

_modules: troubleshooting, failure-modes, validation_

```text
# --- Failure modes & fixes ---
# 200 bp bins too coarse for sharp boundaries:
#   => re-binarize at -b 100 or -b 50; retrain model (more memory/time)
# Binarization discards signal magnitude (can't distinguish low vs high):
#   => use Segway (continuous) or EpiSegMix (flexible distributions)
# Wrong state count (redundant states at high N; lumped biology at low N):
#   => train at N=15,18,25; inspect emission similarity; pick smallest interpretable N
# Mark panel mismatch applying precomputed model:
#   => match exact marks & ordering, OR retrain on available panel
# IgG control instead of input:
#   => use sonicated input for histone mark ChIP binarization
# Cross-cell-type state label inconsistency:
#   => joint segmentation on concatenated data, OR apply one precomputed model to all

# --- Common runtime errors ---
# java.lang.OutOfMemoryError        => java -mx32G -jar ChromHMM.jar ...
# BinarizeBam very slow             => samtools index all BAMs first
# All states have similar emissions => need >=5 marks for 15-state model
# Empty segments for a chromosome   => add to chromsizes or use -chrom flag
# State labels don't match Roadmap  => use precomputed model OR map by emission similarity
# ChromHMM "no signal in marks"     => all bins 0; check signal & control normalization

# --- Reconciliation ---
# ChromHMM vs Segway differ          => both valid; inspect emissions; match resolution needs
# Wild variation between replicates  => increase mark panel; reduce state count
# Active TSS overlaps polycomb       => bivalent biology (expected in ESC-like cells); use N=18
# Heterochromatin state too large    => expected; H3K9me3 is genome-wide
```
