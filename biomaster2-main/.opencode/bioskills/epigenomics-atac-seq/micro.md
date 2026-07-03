## Validate assay QC

_modules: qc, tss-enrichment, fragment-size, frip, version-check_

```bash
# Verify runtime versions first
macs3 --version          # expect 3.0+
samtools --version       # expect 1.18+
bamCoverage --version    # deepTools 3.5+

# QC gates (acceptance thresholds)
#   uniquely mapped reads : >= 20M preferred for strong bulk ATAC
#   TSS enrichment        : > 7 acceptable, > 10 strong; < 7 -> STOP, flag quality
#   FRiP                  : > 0.2 strong; < 0.1 weak, scrutinize
#   fragment periodicity : strong nucleosome ladder supports good library

# Compute TSS enrichment and fragment metrics (deepTools / pysam)
#   -> qc/tss_enrichment.tsv
#   -> qc/fragment_metrics.tsv
#   -> figures/tss_enrichment.pdf
#   -> figures/fragment_size_distribution.pdf
```

## Call peaks with ATAC-specific settings

_modules: peak-calling, macs3, bampe, tn5-shift, nomodel_

```bash
macs3 callpeak \
  -t atac.bam \
  -f BAMPE \
  -g hs \
  -n sample \
  --nomodel \
  --shift -100 \
  --extsize 200 \
  -q 0.01 \
  --outdir results/peaks

# Key parameters
#   -f         BAMPE        fragment-aware paired-end mode (required for PE ATAC)
#   --nomodel  on           standard for ATAC (skip shifting model building)
#   --shift    -100         common Tn5 offset convention
#   --extsize  200          common first-pass extension
#   -q         0.01         starting FDR threshold
#   -g         hs           genome size (hs for human; adjust per organism)

# Outputs
#   results/peaks/sample_peaks.narrowPeak
#   results/peaks/sample_summits.bed
```

## Build a consensus peak matrix

_modules: consensus-peaks, count-matrix, bedtools, featurecounts_

```bash
# 1. Merge per-sample peaks into a consensus set
#    e.g. bedtools merge on concatenated summits/narrowPeak intervals
#    -> results/peaks/consensus_peaks.bed

# 2. Count fragments per sample into consensus intervals
#    e.g. featureCounts or bedtools coverage / multiBamSummary
#    paired-end, fragment-centric counting
#    -> results/matrix/consensus_peak_counts.tsv  (peak x sample)

# Conventions
#   - use the same reference build for all samples (do NOT merge mixed builds)
#   - count fragments, not reads, for paired-end ATAC
```

## Test differential accessibility

_modules: differential-accessibility, deseq2, edger, statistics_

```bash
# Replicate-aware DA testing on the consensus count matrix
#   - input : results/matrix/consensus_peak_counts.tsv  (peak x sample)
#   - design: sample groups / contrasts
#   - report: effect size (log2FC) + adjusted p-value (FDR)
#   e.g. DESeq2 or edgeR on consensus peak counts
#   -> results/diff_accessibility.tsv

# Conventions
#   - require biological replicates; never treat single-replicate as differential
#   - report both log2FC and padj
```

## Run motif or footprint follow-up

_modules: motif, footprinting, chromvar, tobias, downstream_

```bash
# Motif / footprint follow-up (optional, quality-gated)
#   - run ONLY if TSS enrichment, FRiP, and read depth pass step-1 gates
#   - motif deviation  : e.g. chromVAR-style motif enrichment on consensus peaks
#   - footprinting      : e.g. TOBIAS / HINT-ATAC on high-quality, high-depth libraries
#   - do NOT footprint weak or low-depth libraries

# Optional supplements: deeptools, pysam
```
