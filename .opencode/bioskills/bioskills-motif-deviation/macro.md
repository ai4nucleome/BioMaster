# Bioskills Motif Deviation

## Overview

Compute per-sample or per-cell TF motif accessibility deviation z-scores with chromVAR, controlling for GC content and total accessibility via matched background peak sets. The workflow answers "which TF motifs explain accessibility variation across my samples or cells?" — complementary to per-site footprinting, which asks whether a specific motif site is bound.

Inputs: a peak count matrix (bulk samples or single-cell ATAC cells), a GRanges of peak coordinates, a reference BSgenome, and a motif PFM collection (JASPAR or CIS-BP). Outputs: a motif-x-sample (or motif-x-cell) z-score matrix, a per-motif variability ranking for unsupervised TF discovery, and optionally a list of differential motifs per condition or cluster.

Three execution paths are supported and share the same conceptual stages: standalone chromVAR on a SummarizedExperiment (bulk), Signac::RunChromVAR on a Seurat scATAC object, and ArchR::addDeviationsMatrix on an ArchR project. A final optional stage integrates the chromVAR z-scores with DecoupleR (ULM/MLM/consensus) for multi-method TF activity inference suitable for multi-omics integration. chromVAR requires a peak set at full ATAC scale (typically 50k–200k peaks), ≥1500 reads/sample (bulk) or ≥500 cells/cluster (single-cell), and genuine biological variation across the sample population; below these thresholds z-scores inflate or collapse to zero.

## Data Preparation

Assemble the input into a chromVAR-compatible container and apply quality filters. For the bulk path, build a SummarizedExperiment from a peak count matrix (rows = peaks, columns = samples) and a GRanges of peak coordinates, then add GC bias against the reference genome. Filter sparse samples (minimum read depth and fraction of reads in peaks) and unreliable peaks (non-overlapping, minimum count, present in a minimum fraction of samples). For the single-cell paths, ensure the Seurat ATAC assay or ArchR project already carries a finalized consensus/reproducible peak set and peak matrix before proceeding — motif annotations become stale if peaks change downstream. chromVAR needs a peak set at full ATAC scale (typically 50k–200k peaks) and at least 1500 reads/sample (bulk) or 500 cells/cluster (single-cell); below these thresholds z-scores inflate. If addGCBias errors about missing seqlengths, assign the genome's seqlengths to the GRanges first.

## Motif Matching

Acquire a position-frequency-matrix (PFM) collection and match each motif to the peak set. For JASPAR2024, a known TFBSTools incompatibility (issue #39) prevents getMatrixSet from dispatching on the JASPAR2024 package object directly; open the underlying SQLite handle and pass that instead (the older JASPAR2020 accepts the package object directly). Match motifs to peaks with motifmatchr at p.cutoff=5e-05. In the Signac path use AddMotifs on the Seurat object; in ArchR use addMotifAnnotations with the cisbp set (default, ~5000 motifs) or JASPAR2020 for a smaller curated set. Run this step only after the peak set is finalized — if peaks change downstream, motif annotations become stale and the deviation matrix will contain NAs or missing entries.

## Deviation Computation

Compute the chromVAR deviation z-scores — the core of the workflow. First sample matched background peaks (matched on GC content and total accessibility in a 25x25 bin grid; default 50 iterations, roughly 50 background peaks per foreground peak). Then computeDeviations returns, for each motif and sample/cell, a bias-corrected z-score: how many standard deviations above the matched-background expectation the motif's accessibility falls. Z-scores are signed (positive = more accessible than population average) and magnitudes of 2–5 are typical for biologically interesting motifs; >5 indicates a major driver of cell-state differences. computeVariability ranks motifs by across-sample variance for unsupervised TF discovery. The Signac wrapper RunChromVAR and the ArchR pair addBgdPeaks + addDeviationsMatrix perform the same computation with ecosystem-appropriate defaults. Keep niterations at the default; reducing below 30 inflates noise, increasing above 100 yields diminishing returns.

## Differential Motif Analysis

Identify TF motifs whose deviation z-scores differ between conditions (bulk) or between clusters (single-cell). For bulk, fit a limma linear model on the motif-x-sample z-score matrix with empirical Bayes moderation and pull motifs at BH-adjusted p < 0.05 — use the adj.P.Val column that topTable returns, not a non-existent FDR column; logFC is the difference in z-scores between groups. For Signac, call FindAllMarkers on the chromvar assay with mean.fxn=rowMeans and fc.name='avg_diff' — the default fold-change function is designed for log-counts and is meaningless on z-scores. For ArchR, call getMarkerFeatures on the MotifMatrix with useSeqnames='z'. Verify factor level order so the contrast sign is interpreted correctly (first level is the reference).

## Multi-Method TF Activity Integration

Optionally refine TF activity estimates by aggregating chromVAR z-scores across multiple inference methods with DecoupleR. DecoupleR runs ULM, MLM, and a consensus of several methods (viper, GSVA, etc.) on the motif-x-cell deviation matrix against a TF-target network such as CollecTRI. The consensus output is more robust than any single method to motif-database biases and is the recommended input for downstream multi-omics integration (e.g. SCENIC+). This step is complementary to, not a replacement for, the chromVAR z-scores; for high-stakes per-cell TF activity, consider also running a sequence-based model such as scBasset and reporting the intersection.
