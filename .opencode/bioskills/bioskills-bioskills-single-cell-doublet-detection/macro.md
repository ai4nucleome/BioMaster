# Bioskills Bioskills Single Cell Doublet Detection

## Overview

This workflow detects and removes doublets (droplets containing two or more cells) from single-cell RNA-seq data. Doublets appear as artificial intermediate cell populations and must be removed before downstream analysis to avoid spurious clusters and marker genes. The workflow supports three complementary detection methods: Scrublet (Python, simulation-based, fast), DoubletFinder (R/Seurat, pANN-based with pK parameter optimization, accurate but slower), and scDblFinder (R/Bioconductor, gradient-boosted classifier, fast and high accuracy). Inputs: a filtered count matrix (10x MTX directory or count matrix) loaded into an AnnData (Python) or Seurat/SingleCellExperiment (R) object. Outputs: an annotated object with per-cell doublet scores and singlet/doublet classifications, plus a filtered singlet-only object ready for normalization and clustering. Use this workflow after initial cell calling and before normalization/clustering. The expected doublet rate scales with cells loaded (approximately 0.8% per 1,000 cells; formula: rate ≈ cells_loaded / 1000 × 0.008), and serves as the prior for all three methods.

## Data Loading & QC Preparation

Load the scRNA-seq count matrix into the analysis environment (Scanpy AnnData for Python, Seurat object or SingleCellExperiment for R). Compute basic QC metrics including mitochondrial gene percentage, which is used alongside doublet status for downstream filtering. Estimate the expected doublet rate based on the number of cells loaded using the approximation rate ≈ cells_loaded / 1000 × 0.008 (approximately 0.8% for 1,000 cells, 4% for 5,000 cells, 8% for 10,000 cells, 12% for 15,000 cells). This rate feeds into all detection methods as the prior for the expected number of doublets.

## Scrublet Detection (Python)

Run Scrublet to detect doublets by simulating artificial doublets from random pairs of cells, embedding real and simulated cells together, and scoring each cell based on its similarity to the simulated doublet neighborhood. Scrublet is fast and integrates natively with Scanpy/AnnData. Key parameters include expected_doublet_rate, min_counts, min_cells, min_gene_variability_pctl, n_prin_comps, and synthetic_doublet_umi_subsampling. The output is a per-cell doublet score and a binary predicted_doublet flag, stored in adata.obs for downstream filtering.

## DoubletFinder Detection (R)

Run DoubletFinder on a preprocessed and clustered Seurat object. The method requires optimizing the pK neighborhood parameter via a parameter sweep (paramSweep, summarizeSweep, find.pK), selecting the pK that maximizes the BCmetric. The expected number of doublets (nExp) is derived from the expected doublet rate. DoubletFinder computes artificial nearest neighbor proportions (pANN) and classifies cells as singlets or doublets. Supports both standard log-normalization and SCTransform workflows. This method is slower but accurate.

## scDblFinder Detection (R)

Run scDblFinder, which simulates doublets and trains a gradient-boosted classifier on real versus simulated profiles to score each cell. It is fast and reported to have excellent accuracy. Works directly on SingleCellExperiment objects and can be converted from Seurat objects. Supports multi-sample processing via the samples argument and tunable parameters including dbr (doublet rate), dbr.sd, nfeatures, dims, and k. Output includes scDblFinder.class (singlet or doublet) and scDblFinder.score.

## Visualization, Comparison & Thresholding

Visualize doublet scores to validate detection results. For Scrublet, plot the doublet score histogram to inspect the bimodal distribution and the automatic threshold. Embed cells via UMAP and color by doublet_score and predicted_doublet to check that flagged cells cluster together. Compare multiple methods (for example Scrublet versus scDblFinder) using cross-tabulation and side-by-side DimPlots. If the automatic threshold is unsatisfactory, set a manual threshold on the doublet score. Also inspect total counts by doublet status to identify potential homotypic doublets (same cell type, harder to detect, often exhibiting higher total counts).

## Filtering & Pipeline Integration

Remove predicted doublets from the dataset and integrate doublet detection into a complete preprocessing workflow. For Python/Scanpy, filter doublets before or alongside QC filtering (such as mitochondrial percentage), then proceed through normalization, HVG selection, PCA, neighbors, UMAP, and Leiden clustering. For R/Seurat, subset to singlets, apply QC filters, then re-run normalization, scaling, PCA, UMAP, neighbors, and clustering on the clean singlet set. Re-preprocessing after doublet removal is recommended so that downstream steps reflect only singlet profiles.
