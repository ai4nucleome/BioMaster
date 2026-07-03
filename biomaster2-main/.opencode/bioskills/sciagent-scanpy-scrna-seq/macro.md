# Sciagent Scanpy Scrna Seq

## Overview

Scanpy is a scalable Python toolkit for analyzing single-cell RNA-seq data built on the AnnData format. This skill covers the end-to-end standard workflow: data loading, quality control, normalization, highly variable gene selection, scaling, dimensionality reduction (PCA, UMAP), Leiden clustering, marker gene identification, cell type annotation, and export. It also includes optional advanced analyses: batch correction with ComBat, trajectory inference with PAGA and diffusion pseudotime, differential expression between experimental conditions within a cell type, and publication-quality figure generation.

**Inputs:** Gene expression count matrix (cells x genes) in 10X Cell Ranger output (`filtered_feature_bc_matrix/`), `.h5ad`, `.h5`, `.csv`, or `.loom` format. Requires `scanpy>=1.10`, `leidenalg`, `igraph`, `anndata`; Python 3.9+; 16GB+ RAM recommended for >50k cells.

**Outputs:** Annotated AnnData object (`.h5ad`) with PCA/UMAP embeddings, cluster labels, raw counts layer, and cell type annotations; per-cell metadata CSV; marker gene table CSV; and publication-quality figures (QC violins/scatter, UMAP, dot plots, heatmaps, stacked violins).

**When to use:** Analyzing scRNA-seq count matrices; performing QC filtering (mitochondrial %, gene/cell counts); running dimensionality reduction (PCA, UMAP, t-SNE); identifying cell clusters via Leiden community detection; finding differentially expressed marker genes per cluster (Wilcoxon, t-test, logistic regression); annotating cell types from known marker panels; trajectory inference and pseudotime analysis (PAGA, diffusion pseudotime); generating publication-quality single-cell plots; comparing gene expression across conditions within cell types. Use **Seurat** (R/Bioconductor) instead for scRNA-seq analysis in an existing R workflow or when Seurat-specific assay types are required.

## Setup and Data Loading

Configure scanpy settings (verbosity, figure parameters) and read the count matrix into an AnnData object. Supports 10X Cell Ranger matrix directories, h5ad, h5, CSV, and loom formats via the appropriate reader. Gene names are made unique to avoid collisions. For multi-sample studies, concatenate AnnData objects with a batch key before downstream processing.

## Quality Control

Annotate mitochondrial, ribosomal, and hemoglobin gene groups; compute QC metrics (n_genes_by_counts, total_counts, pct_counts_mt); visualize distributions with violin and scatter plots; and filter low-quality cells and genes. Fixed thresholds (min_genes=200, min_cells=3, max_genes=5000 for doublet removal, pct_mt<20) should be adjusted by tissue type (5% mt for PBMCs, 20% for tumors). MAD-based filtering offers a data-driven alternative to fixed cutoffs.

## Normalization, Feature Selection, and Scaling

Preserve raw counts in a named layer for later differential expression. Normalize library sizes to a target sum (default 10,000), log-transform, and save the normalized data as .raw for visualization. Identify highly variable genes (typically 2000; use 3000-5000 for rare cell types) using the seurat_v3 flavor on raw counts, then subset to HVGs. Optionally regress out confounders (total_counts, pct_counts_mt) and scale to unit variance with extreme value clipping. Skip regress_out for large datasets (>100k cells) or when using scVI/Harmony integration.

## Dimensionality Reduction and Embedding

Compute PCA on the scaled HVG matrix and inspect the variance ratio elbow plot to select the number of PCs (typically 30-50; 40 is a safe default). Build a k-nearest neighbor graph (n_neighbors=15 balances local and global structure). Embed with UMAP for 2D visualization, coloring by QC metrics to sanity-check the embedding.

## Clustering

Run Leiden community detection at multiple resolutions (e.g., 0.3, 0.5, 0.8, 1.0, 1.2) and compare clusterings side-by-side on the UMAP. Select the final resolution based on biological plausibility and marker gene support — more clusters is not always better. Resolution controls granularity (higher values yield more clusters).

## Marker Gene Identification

Find differentially expressed genes per cluster using the Wilcoxon rank-sum test on raw counts (recommended for publications; t-test for exploratory, logreg for most discriminative genes). Visualize results with rank genes plots, dot plots, and heatmaps. Extract the full results table as a DataFrame and filter to significant markers (pvals_adj < 0.05) for downstream annotation. Remove clusters with fewer than 10 cells before DE to avoid errors.

## Cell Type Annotation and Export

Define canonical marker gene panels for expected cell types and inspect per-cluster expression with a dot plot. Map clusters to cell types based on marker expression and DE results, storing assignments in adata.obs. Visualize the annotated UMAP and save all outputs: the annotated AnnData object (with embeddings, labels, raw counts layer), per-cell metadata CSV, and marker gene table CSV.

## Advanced Analyses

Optional analyses for specific scenarios. (1) Batch correction with ComBat when multiple samples show visible batch effects on the UMAP — re-run PCA, neighbors, UMAP, and clustering after correction. (2) Trajectory inference with PAGA graph abstraction and diffusion pseudotime for developmental continua — set a root cell and visualize pseudotime on UMAP. (3) Differential expression between experimental conditions within a specific cell type using rank_genes_groups with a reference group. (4) Publication-quality figure generation with high-DPI settings, custom palettes, and multi-panel matplotlib layouts.
