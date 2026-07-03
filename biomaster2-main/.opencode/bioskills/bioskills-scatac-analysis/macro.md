# Bioskills Scatac Analysis

## Overview

This workflow analyzes single-cell ATAC-seq (scATAC-seq) data to identify cell types and regulatory elements from chromatin accessibility. Starting from a 10X filtered peak-barcode matrix (HDF5) and per-cell metadata, optionally with a fragments.tsv.gz file, it performs scATAC-specific QC (TSS enrichment, nucleosome signal, fraction of reads in peaks, blacklist ratio), normalizes the peak matrix with TF-IDF, reduces dimensions via latent semantic indexing (LSI/SVD), clusters cells on a UMAP embedding, and annotates clusters using gene activity scores. Downstream stages call per-cluster peaks with MACS2, identify differentially accessible peaks, score transcription-factor motif activity with chromVAR, and optionally transfer cell-type labels from an scRNA-seq reference. The primary implementation uses Signac/Seurat in R; ArchR is provided as a memory-efficient alternative for large datasets, and chromVAR can also be run standalone. Use this skill when you have 10X scATAC-seq data and want to go from a raw peak-barcode matrix to annotated cell types with regulatory-element and motif analysis. Reference examples were tested with MACS2 2.2+ and scanpy 1.10+; verify installed versions match before running and adapt API calls if versions differ.

## Setup & Data Loading

Install Signac and its dependencies (EnsDb, chromVAR, motifmatchr, JASPAR, TFBSTools). Load the 10X filtered peak-barcode matrix and per-cell metadata, build a ChromatinAssay object with the fragment file and reference genome, wrap it in a Seurat object, and attach gene annotations from EnsDb (converted to UCSC seqlevel style). For large datasets, ArchR's createArrowFiles is the scalable alternative: it reads fragment files directly, applies TSS and fragment-count filters, and builds on-disk Arrow files that are then wrapped in an ArchRProject.

## QC & Filtering

Compute scATAC-specific QC metrics: nucleosome signal (ratio of mono- to di-nucleosome fragments), TSS enrichment, fraction of reads in peaks, and blacklist-region ratio. Visualize metric distributions with violin plots, then filter cells using thresholds on unique fragments, TSS enrichment, fraction in peaks, nucleosome signal, and blacklist ratio. ArchR provides an analogous QC via per-cell TSS enrichment and fragment counts, plus filterDoublets for computational doublet removal. Typical threshold ranges are provided as a reference table.

## Normalization & Dimensionality Reduction

Normalize the peak matrix with TF-IDF (term frequency-inverse document frequency), select top features, and perform latent semantic indexing (LSI via SVD) to obtain a low-dimensional embedding. Use DepthCor to identify LSI components that correlate with sequencing depth and exclude them from downstream analysis (commonly dropping component 1). ArchR performs the equivalent with iterative LSI on the TileMatrix, which repeats LSI with intermediate clustering to reduce depth-driven batch effects.

## Clustering & Cell Annotation

Build a UMAP embedding from the non-depth-correlated LSI components, construct a shared-nearest-neighbor graph, and cluster cells (Signac uses algorithm 3, the Leiden-style algorithm). Annotate clusters by computing gene activity scores from peak accessibility near gene bodies, adding them as an RNA assay, log-normalizing, and visualizing canonical marker genes (e.g. CD34, MS4A1, CD3D, CD14). ArchR clusters via addClusters, embeds with addUMAP, and identifies marker genes per cluster from the GeneScoreMatrix.

## Peak Calling & Differential Accessibility

Call peaks per cluster with MACS2 to produce a unified, reproducible peak set, then quantify that peak set across all cells with FeatureMatrix and store it as a new ChromatinAssay. Identify differentially accessible peaks between clusters using a logistic regression test that controls for sequencing depth (latent.vars = peak_region_fragments). ArchR achieves the equivalent by aggregating per-cluster coverages (addGroupCoverages) and calling a reproducible peak set (addReproduciblePeakSet), then adding a peak matrix.

## Motif Activity & Visualization

Add motif annotations from JASPAR, run chromVAR to compute per-cell transcription-factor motif deviation scores against a GC-matched background, and visualize motif activity (e.g. CTCF) on the UMAP. Identify differentially active motifs between clusters. Generate coverage plots over genomic regions or genes to inspect accessibility tracks per cluster. Optionally integrate with an scRNA-seq reference via transfer anchors (CCA reduction) to transfer cell-type labels onto the scATAC cells. chromVAR can also be run standalone on a peak-count SummarizedExperiment, and ArchR provides motif enrichment and deviation matrices via addMotifAnnotations and addDeviationsMatrix.
