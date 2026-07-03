# Bioskills Preprocessing

## Overview

This workflow preprocesses raw scRNA-seq count matrices into analysis-ready data for dimensionality reduction, clustering, and annotation. It takes a raw count matrix (e.g. a 10X `filtered_feature_bc_matrix/` directory loaded into an AnnData object or Seurat object) and produces a normalized, feature-selected, and scaled object with quality-control metadata attached.

The pipeline proceeds through five stages: (1) compute per-cell QC metrics such as gene/UMI counts and mitochondrial percentage and inspect their distributions; (2) filter out low-quality cells, doublets, dying cells, and rarely detected genes using thresholds tuned to the tissue; (3) normalize library sizes and log-transform the counts (or apply SCTransform in Seurat); (4) identify highly variable genes (HVGs) to use as features; and (5) scale the data to unit variance and optionally regress out confounders such as total counts or mitochondrial fraction.

Use this skill as the first step of any scRNA-seq analysis, before PCA, neighbor-graph construction, clustering, or marker discovery. Both Scanpy (Python) and Seurat (R) idioms are provided per step; pick the implementation matching your environment. Typical QC thresholds (min_genes 200-500, max_genes 2500-5000, max_mt 5-20%, min_cells 3-10) are tissue-dependent and should be adjusted based on the QC visualizations.

## QC Metrics and Visualization

Compute per-cell quality-control metrics so that low-quality cells can be identified and filtered downstream. For each cell this records the number of detected genes (n_genes_by_counts / nFeature_RNA), the total UMI count (total_counts / nCount_RNA), and the percentage of reads mapping to mitochondrial genes (pct_counts_mt / percent.mt), which is a proxy for cell damage. After computing the metrics, visualize their distributions with violin plots and pairwise scatter plots to choose sensible filtering thresholds for the tissue at hand. This step only annotates the object; no cells or genes are removed yet.

## Filtering

Remove low-quality cells, putative doublets, dying cells, and rarely detected genes based on the QC metrics computed in the previous step. Cells are typically filtered by a minimum and maximum gene count (to drop empty droplets and doublets) and a maximum mitochondrial percentage (to drop damaged cells); genes are filtered by a minimum number of expressing cells. Before discarding the raw counts, store a copy of the unnormalized object (e.g. adata.raw or a counts layer) so that differential-expression and visualization can use raw values later. Thresholds are tissue-dependent; the values below are common starting points.

## Normalization

Correct for differences in sequencing depth between cells so that counts are comparable, then log-transform the data to stabilize variance and bring the distribution closer to normal. In Scanpy this is done with library-size normalization to a target sum (commonly 1e4) followed by log1p. In Seurat the standard approach is LogNormalize with a scale factor of 10000; alternatively SCTransform performs variance-stabilizing normalization in a single step and is recommended for most modern workflows. The normalized (non-scaled) data is the basis for highly variable gene selection and is preserved for visualization and marker analysis.

## Highly Variable Gene Selection

Identify the most informative genes to use as features for downstream dimensionality reduction, reducing noise from housekeeping genes. In Scanpy use highly_variable_genes with a target number of top genes (commonly 2000) and an appropriate flavor; the seurat_v3 flavor operates on raw counts and should be given the counts layer. In Seurat use FindVariableFeatures with the vst selection method (SCTransform selects variable features automatically). After selection, visualize the HVGs and optionally subset the object to keep only HVGs for the subsequent scaling and PCA steps.

## Scaling and Confounder Regression

Scale the normalized expression values to zero mean and unit variance so that highly expressed genes do not dominate downstream PCA, clipping extreme values to a maximum (commonly 10) to limit the influence of outliers. Optionally regress out unwanted sources of variation such as total counts, mitochondrial percentage, or cell-cycle scores before or during scaling; this is done with regress_out in Scanpy or via the vars.to.regress argument of ScaleData / SCTransform in Seurat. After this step the object is ready for PCA, neighbor-graph construction, clustering, and annotation. If subsetting to HVGs, do so before scaling for efficiency.
