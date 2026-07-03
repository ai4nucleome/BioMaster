# Bioskills Single Cell Doublet Detection

## Overview

This workflow detects and removes doublets (droplets containing two or more cells) from single-cell RNA-seq data. Doublets appear as artificial intermediate cell populations and must be removed before downstream analysis. The workflow supports three complementary methods — Scrublet (Python), DoubletFinder (R/Seurat), and scDblFinder (R/Bioconductor) — each simulating artificial doublets and scoring cells by their similarity to them. Inputs: a filtered count matrix (e.g., 10x MTX output) or an existing AnnData / Seurat / SingleCellExperiment object. Outputs: per-cell doublet scores and singlet/doublet classifications, plus a filtered object containing only singlets. Use this workflow after initial cell calling and before normalization, HVG selection, and clustering. The expected doublet rate scales with cells loaded (roughly 0.8% per 1,000 cells). Reference examples were tested with matplotlib 3.8+, numpy 1.26+, and scanpy 1.10+; verify installed versions and adapt API calls if versions differ.

## Data Loading & QC Preparation

Load the filtered count matrix (e.g., 10x MTX output) into an AnnData (Python/Scanpy) or Seurat (R) object and compute QC metrics including mitochondrial gene percentage. Determine the expected doublet rate from the number of cells loaded — the rate scales roughly as 0.8% per 1,000 cells. This preparation is shared across all doublet detection methods and should be completed before scoring.

## Scrublet Detection (Python)

Use Scrublet to detect doublets by simulating artificial doublets from random cell pairs, embedding real and simulated cells together, and scoring each cell by its similarity to simulated doublets. The expected doublet rate and simulation parameters (minimum counts, minimum cells, gene variability percentile, number of PCs, UMI subsampling) can be adjusted. A manual score threshold can be applied instead of the automatic classifier call.

## DoubletFinder Detection (R)

Use DoubletFinder (R/Seurat) to detect doublets via pANN-based classification. The workflow requires preprocessing and clustering first, then a parameter sweep to optimize the pK neighborhood parameter, followed by computing artificial nearest neighbor proportions and classifying cells as singlets or doublets. An SCTransform-based preprocessing variant is supported, and the expected doublet count can be adjusted by cells loaded.

## scDblFinder Detection (R)

Use scDblFinder (R/Bioconductor) for fast, accurate doublet detection via a gradient-boosted classifier trained on real versus simulated doublet profiles. It accepts a SingleCellExperiment object directly or can be converted from a Seurat object, supports per-sample processing for multi-sample experiments, and exposes parameters for the doublet rate, feature count, dimensions, and neighborhood size.

## Visualization & Doublet Filtering

Visualize doublet detection results to inspect quality — plot score histograms, UMAP embeddings colored by doublet score and classification, and violin plots of total counts stratified by doublet call. Then filter out predicted doublets to retain singlets. Distinguish heterotypic doublets (two different cell types, easier to detect via intermediate expression) from homotypic doublets (same cell type, harder to detect, often showing higher total counts).

## Method Comparison & Pipeline Integration

Compare doublet calls across multiple methods to build consensus and assess agreement, then integrate doublet detection into a complete preprocessing pipeline. In the Scanpy pipeline, run Scrublet before QC filtering then proceed to normalization, HVG selection, and clustering. In the Seurat pipeline, preprocess and cluster, run DoubletFinder, filter singlets and low-quality cells, then re-preprocess the clean object. Method choice balances speed and accuracy: Scrublet and scDblFinder are fast, DoubletFinder is slower; scDblFinder generally offers the best accuracy.
