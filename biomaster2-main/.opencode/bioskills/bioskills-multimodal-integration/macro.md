# Bioskills Multimodal Integration

## Overview

This workflow jointly analyzes multimodal single-cell data where multiple modalities are measured in the same cells — RNA + surface proteins via CITE-seq, or RNA + chromatin accessibility via 10X Multiome / SHARE-seq. It loads each modality into a separate assay of a Seurat object (R) or a MuData object (Python/muon), performs modality-specific QC and normalization (log-normalization for RNA, CLR for ADT proteins, TF-IDF + LSI for ATAC), computes a separate dimensionality reduction per modality, and then integrates them with Weighted Nearest Neighbors (WNN, Seurat) or Multi-Omics Factor Analysis (MOFA, muon). Cells are clustered and embedded on the joint graph, and results are interpreted through modality weights and per-assay marker tables.

Inputs: a 10X feature-barcode matrix containing both 'Gene Expression' and 'Antibody Capture' (CITE-seq) or 'Peaks' (Multiome) matrices, plus an ATAC fragments file for Multiome. Outputs: a Seurat/MuData object carrying a WNN graph (wsnn) or MOFA factors, a joint UMAP embedding, cluster assignments, and combined multi-modal marker tables. Use this skill when you have co-assayed multimodal data and want a single joint representation that leverages every modality, rather than analyzing each modality in isolation.

Version note: reference examples are tested with Seurat v5, Signac v1+, scanpy 1.10+, and muon. If a function signature differs, introspect the installed package (pip show / packageVersion) and adapt the call rather than retrying.

## Load Multimodal Data

Read the 10X output and split it into per-modality assays so each modality can be processed independently before integration. For CITE-seq, separate the 'Gene Expression' and 'Antibody Capture' matrices and register the ADT counts as a second assay on the Seurat object. For 10X Multiome, load RNA counts and ATAC peaks, then attach a ChromatinAssay carrying the fragments file and genome build. In Python, muon's read_10x_h5 returns a MuData object with one modality per slot (e.g. 'rna' and 'prot'). Cell barcodes must be consistent across modalities so they can be matched cell-by-cell downstream.

## Per-Modality QC and Normalization

Apply modality-appropriate QC and normalization to each assay independently. For RNA, compute the mitochondrial percentage, filter low-quality cells (e.g. nFeature_RNA > 200 and percent.mt < 20), then log-normalize, find variable features, and scale. For ADT proteins, use centered log-ratio (CLR) normalization across cells (margin = 2) and scale, since protein counts do not follow the same distribution as RNA. For ATAC, compute nucleosome signal and TSS enrichment as QC metrics, then apply TF-IDF normalization and select top features. Each modality is normalized on its own scale before any joint analysis.

## Per-Modality Dimensionality Reduction

Compute a separate linear embedding for each modality to feed into the joint integration step. Run PCA on the RNA assay using its variable features. Run PCA on the ADT assay using all protein features (proteins are few, so all are used). For ATAC, run singular value decomposition (LSI) on the TF-IDF-normalized matrix; the first LSI component is typically skipped downstream because it correlates with sequencing depth. The number of dimensions retained differs per modality (e.g. 30 PCs for RNA, 18 for ADT, LSI 2:30 for ATAC).

## Multimodal Integration

Build a joint representation that adaptively combines the per-modality embeddings from the previous step. In Seurat, FindMultiModalNeighbors constructs a Weighted Nearest Neighbor (WNN) graph that learns a per-cell weighting of each modality based on how informative each modality is for that cell's local neighborhood, producing a 'wsnn' graph and a 'weighted.nn' object. For CITE-seq the inputs are the RNA PCA and ADT PCA reductions; for Multiome they are the RNA PCA and ATAC LSI reductions (skipping LSI component 1). In muon, mu.tl.mofa fits a Multi-Omics Factor Analysis model that decomposes both modalities into shared latent factors. The output is a joint graph or factor space used downstream for clustering and embedding.

## Joint Clustering and Embedding

Cluster cells and project them into 2D using the joint graph or factor space produced by integration. In Seurat, run FindClusters on the wsnn graph (tune resolution, e.g. 0.5) and RunUMAP on the weighted.nn neighbor object to produce a 'wnn.umap' embedding. In muon, run mu.tl.umap on the MOFA factors. The resulting clusters reflect structure from both modalities simultaneously rather than from either modality alone, which is the main advantage of multimodal integration.

## Visualization and Marker Discovery

Visualize the joint embedding and interpret the integration result. Plot the WNN UMAP colored by cluster and by modality-specific feature expression (e.g. ADT markers like CD3/CD19/CD14). Inspect per-cell modality weights with violin plots to see which modality drives each cluster, and aggregate the raw weights by cluster for a summary. Find differentially expressed markers per cluster within each assay (RNA markers and ADT markers separately) and combine them into a single multi-modal marker table tagged by modality. Optionally compute RNA-protein correlations for genes whose protein product is also measured, to cross-validate modalities.
