# Bioclaw Scrna Preprocessing Clustering

## Overview

Turn raw or minimally processed scRNA-seq data into an analysis-ready AnnData object. Inputs: a 10x directory, .h5, .h5ad, or count matrix (plus optional cell metadata and species context for mitochondrial gene detection). Outputs: a QC-filtered, normalized object with highly variable genes, PCA/UMAP embeddings, Leiden clusters, and a saved results/processed.h5ad artifact for downstream annotation, DE, integration, or trajectory analysis. Use it whenever downstream tasks need a stable single-cell object rather than ad hoc plots. Keep raw counts recoverable, report thresholds explicitly, and review QC distributions before applying hard filters.

## Load And Validate

Read the input into an AnnData object and confirm it is oriented as cells-by-genes. Make gene names unique and record sample IDs and batch labels before any merging or filtering. If the input is already a processed h5ad, inspect adata.raw, existing embeddings, cluster columns, and QC columns before re-running preprocessing.

## Compute QC Metrics

Compute per-cell QC metrics (n_genes_by_counts, total_counts, pct_counts_mt, optional ribosomal/hemoglobin fractions) and plot their distributions before filtering. Thresholds vary by chemistry, tissue, and nucleus-vs-whole-cell assay, so always inspect distributions first.

## Filter Cells And Genes

Apply dataset-aware thresholds rather than a single universal cutoff. Good first-pass defaults: min_genes >= 200, max_genes <= 5000-8000 to drop likely doublets in droplet data, pct_counts_mt < 10-20% depending on tissue stress, and min_cells >= 3 for genes.

## Normalize And Select HVGs

Normalize to a fixed total, log-transform, and save raw counts before heavy transformations. Select 2000-4000 highly variable genes (3000 is a common default) and scale before PCA.

## Reduce Dimensions And Cluster

Run PCA on the HVGs, build a neighbor graph using 10-30 PCs and 10-30 neighbors as a starting range, compute UMAP for visualization, and run Leiden across a small resolution grid (e.g. 0.2, 0.5, 0.8, 1.0). Defaults: n_pcs=30, n_neighbors=15, first-pass resolution 0.5.

## Export Analysis-Ready Artifacts

Persist the processed object and supporting tables/figures for reuse: the processed h5ad, cluster assignments, a QC filter summary, and publication-ready QC and UMAP figures.
