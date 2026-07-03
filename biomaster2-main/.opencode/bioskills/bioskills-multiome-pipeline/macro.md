# Bioskills Multiome Pipeline

## Overview

A complete workflow for analyzing 10X Multiome (joint scRNA + scATAC) data with Seurat and Signac. It loads the joint RNA and ATAC matrices from Cell Ranger ARC output into a single Seurat object carrying a ChromatinAssay, applies modality-specific quality control and dimensionality reduction (SCTransform + PCA for RNA; TF-IDF + LSI for ATAC), integrates the two modalities with weighted nearest neighbors (WNN), clusters cells on the joint graph, identifies RNA and differentially accessible ATAC markers, and links peaks to genes for cis-regulatory interpretation.

Inputs: a 10X Multiome `filtered_feature_bc_matrix.h5` (containing `Gene Expression` and `Peaks` count matrices for the same barcodes), an ATAC fragments file (`atac_fragments.tsv.gz`), and an EnsDb annotation package matching the reference genome (e.g. EnsDb.Hsapiens.v86). For gene-peak linkage a matching BSgenome package is also required.

Outputs: an integrated Seurat object (saved as `.rds`) with a WNN UMAP embedding, joint clusters, per-modality marker tables, and gene-peak links, plus UMAP/QC/marker plots.

When to use: when you have paired per-cell RNA and ATAC from the same cells (10X Multiome) and want a joint, modality-aware analysis rather than treating RNA and ATAC separately. Reference examples were tested with ggplot2 3.5+; before running, verify installed Seurat/Signac/ggplot2 versions match the patterns below (e.g. `packageVersion('<pkg>')`), and if a function raises ImportError/AttributeError/TypeError, introspect the installed package and adapt the call to the actual API rather than retrying blindly.

## Load Multiome Data

Read the joint 10X Multiome HDF5 matrix, which contains both a Gene Expression and a Peaks count matrix for the same barcodes. Build a base Seurat object from the RNA counts, then construct a Signac ChromatinAssay from the ATAC peak matrix using the chr:start-end coordinate separator, attach the ATAC fragments file, and register gene annotations from EnsDb. The result is a single Seurat object carrying both modalities with shared cell barcodes.

## RNA Quality Control and Processing

Compute RNA QC metrics (mitochondrial percentage) and filter cells by total RNA counts and mitochondrial fraction. Normalize the RNA assay with SCTransform and run PCA on the variable features to obtain a transcriptomic embedding for downstream integration.

## ATAC Quality Control and Processing

Compute ATAC-specific QC metrics (nucleosome signal and TSS enrichment) and filter cells by ATAC fragment count, TSS enrichment, and nucleosome periodicity. Normalize the ATAC peak matrix with TF-IDF, select top features, and run truncated SVD (LSI). Inspect LSI components with DepthCor because the first LSI component often correlates with sequencing depth and is typically excluded from integration.

## Weighted Nearest Neighbors Integration

Build a joint weighted-nearest-neighbors graph that combines the RNA PCA and ATAC LSI embeddings, letting each cell's neighborhood be informed by the modality that best describes it. Compute a UMAP from the WNN graph and cluster cells on the shared nearest-neighbor graph (wsnn). Skip the depth-correlated first LSI component by starting ATAC dimensions at 2.

## Visualization and Markers

Compare modality-specific embeddings (RNA PCA, ATAC LSI) against the joint WNN UMAP, and inspect per-cell modality weights across clusters. Identify RNA markers per cluster with FindAllMarkers on the SCT assay, and identify differentially accessible ATAC peaks using a logistic regression test that regresses out total ATAC counts as a latent variable.

## Gene-Peak Linkage

Link ATAC peaks to putative target genes by correlating peak accessibility with gene expression, using the SCT expression assay and the ATAC peak assay. Compute region statistics against the reference genome to support linkage, then visualize peak-gene coverage around example marker genes with CoveragePlot.
