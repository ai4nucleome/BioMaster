# Bioskills Scrnaseq Pipeline

## Overview

This pipeline analyzes single-cell RNA-seq data from 10X Genomics Cell Ranger output through to annotated cell types. It covers the complete workflow: data loading, quality control and filtering, doublet detection, normalization and feature selection, dimensionality reduction, clustering, marker gene discovery, and cell type annotation. Two parallel paths are provided — Seurat (R) as the primary path and scanpy (Python) as an alternative — so the same conceptual steps can be executed in either ecosystem.

**Inputs:** A `filtered_feature_bc_matrix` directory or `.h5` file produced by Cell Ranger.

**Outputs:** An annotated Seurat object (`.rds`) or AnnData object (`.h5ad`) with cluster assignments and cell type labels, plus marker gene tables and UMAP visualizations.

**When to use:** You have 10X scRNA-seq count data and need to go from raw counts to annotated cell populations. For multi-sample studies, run this pipeline per sample then integrate batches with scVI or Harmony before clustering. Reference versions: Cell Ranger 8.0+, scanpy 1.10+, Seurat 5+, numpy 1.26+. If code throws ImportError or AttributeError, introspect the installed package and adapt to the actual API.

## Data Loading & QC

Load the 10X Genomics Cell Ranger output (filtered_feature_bc_matrix) into a Seurat object (R) or AnnData object (Python). Compute quality-control metrics per cell including gene count (nFeature_RNA / n_genes_by_counts), UMI count (nCount_RNA / total_counts), mitochondrial read percentage, and ribosomal percentage. Visualize QC distributions with violin plots to identify outliers. Then filter out low-quality cells — those with very low gene counts (empty droplets), very high gene counts (potential doublets), or high mitochondrial content (dying or lysed cells) — and remove genes detected in too few cells. Typical thresholds: 200–5000 genes per cell, <20% mitochondrial reads, genes detected in at least 3 cells. Adjust thresholds based on tissue type and QC plot inspection.

## Doublet Detection

Detect and remove doublets — two cells captured in a single droplet — which can create artifactual intermediate clusters and distort downstream results. In R, convert the Seurat object to a SingleCellExperiment and run scDblFinder, which assigns each cell a doublet score and class (singlet/doublet). In Python, use scanpy's built-in scrublet wrapper. Remove predicted doublets before proceeding to normalization. This step is important even after QC filtering, as doublets often pass standard gene-count and mitochondrial thresholds.

## Normalization & Feature Selection

Normalize raw counts to correct for differences in sequencing depth between cells and to stabilize variance for downstream linear methods. In Seurat, SCTransform is the recommended approach; it regresses out percent.mt and produces a variance-stabilized expression matrix. Alternatively, use standard LogNormalize followed by FindVariableFeatures (2000 HVGs) and ScaleData. In scanpy, normalize_total to 1e4, apply log1p, select highly variable genes, and scale the matrix (capping extreme values). The output is a normalized, scaled expression matrix restricted to highly variable genes, ready for dimensionality reduction.

## Dimensionality Reduction & Clustering

Reduce the high-dimensional expression matrix to a lower-dimensional representation for visualization and graph-based clustering. First run PCA on the highly variable genes (30–50 components), then inspect an elbow plot to determine how many PCs capture the majority of variance. Embed cells in 2D with UMAP for visualization. Build a shared nearest-neighbor graph on the selected PCs and cluster cells using the Louvain or Leiden algorithm. In Seurat, use FindNeighbors followed by FindClusters at multiple resolutions (0.2–1.0) and select the resolution that yields visually separable, biologically meaningful clusters. In scanpy, use sc.pp.neighbors and sc.tl.leiden. Resolution 0.4–0.8 is a common starting range.

## Marker Gene Discovery

Identify genes that are differentially expressed in each cluster relative to all other clusters; these serve as candidate cell-type markers. In Seurat, set the identity to the chosen clustering resolution and run FindAllMarkers with only.pos = TRUE, min.pct = 0.25, and logfc.threshold = 0.25. In scanpy, use rank_genes_groups with the Wilcoxon rank-sum test. Extract the top markers per cluster (e.g., top 10 by log2FC) and visualize them with heatmaps or dot plots to reveal cluster-specific expression patterns that guide annotation. Save the full marker table for downstream reference.

## Cell Type Annotation

Assign biological cell types to each cluster based on marker gene expression, cross-referenced with canonical markers from the literature (e.g., CD3/CD4 for T cells, CD14 for monocytes, MS4A1/CD79A for B cells, NKG7 for NK cells). Map cluster identities to cell type labels and store the result as a new metadata column. Visualize the final annotated UMAP colored by cell type. Save the annotated object — an RDS file for Seurat or an h5ad file for scanpy. Automated reference-based tools such as SingleR or CellTypist can supplement manual annotation when canonical markers are ambiguous or the tissue is less well characterized.
