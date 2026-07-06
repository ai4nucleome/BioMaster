# Bioskills Single Cell Atac

## Overview

A workflow for processing 10X single-cell ATAC-seq data from cellranger output into a clustered, annotated, and (optionally) integrated cell atlas. Inputs: cellranger-atac or cellranger-arc output (filtered_peak_bc_matrix.h5, fragments.tsv.gz, singlecell.csv) or raw fragment files. Outputs: a clustered/embedded object (Seurat object, ArchR project, or backed AnnData) carrying per-cell QC, a per-cluster pseudobulk peakset / consensus peakset, gene-activity-based cell-type annotations, and optionally a joint RNA+ATAC embedding for Multiome. Use this skill when you have 10X scATAC or Multiome data and need to go from cellranger output to annotated cell types. Choose the ecosystem by language and scale: Signac (R, Seurat, small-to-medium, best Multiome support), ArchR (R, memory-efficient Arrow files, large >100K cells, trajectories), or SnapATAC2 (Python, modern, very large datasets). Critical gotchas baked into the steps: skip LSI component 1 (a sequencing-depth artifact, not biology); per-cell QC thresholds are looser than bulk because individual cells carry far less signal; AMULET doublet detection requires >=5000 fragments/cell; MACS3 per-cluster peak calling requires >=200 cells/cluster. Verify package versions before use (Signac 1.13+, ArchR 1.0.2+, SnapATAC2 2.8+ uses pp.import_fragments).

## Ecosystem Selection & Data Loading

Choose the analysis ecosystem based on language preference, dataset size, and whether Multiome integration is needed. Signac+Seurat for R users and Multiome; ArchR for large (>100K cells) ATAC-only datasets and trajectory analysis; SnapATAC2 for Python-first labs and very large datasets. Load cellranger output (peak-by-cell matrix, fragments file, per-barcode metadata) and build the chromatin assay / Arrow files / backed AnnData with the matching genome annotation. Verify the chemistry first: cellranger-atac (single-modality) and cellranger-arc (Multiome, paired RNA+ATAC) produce different output structures and barcode universes, and mixing them fails silently. Match EnsDb/BSgenome builds to the reference genome (EnsDb.Hsapiens.v86 = GRCh38).

## Per-Cell QC & Doublet Detection

Compute per-cell QC metrics (TSS enrichment, nucleosome signal, FRiP / pct reads in peaks, blacklist ratio, mitochondrial fraction, fragment count) and apply looser-than-bulk per-cell thresholds, because individual cells carry orders of magnitude less signal than bulk and the population aggregate is what matters. Run doublet detection with AMULET (ATAC-specific collision-based; requires >=5000 fragments/cell, below which the binomial test lacks power) as the primary check, and ArchR addDoubletScores or scDblFinder as orthogonal verification; cells double-flagged by two tools are high-confidence doublets. Filter to passing cells before embedding.

## Dimensionality Reduction & Clustering

Build a cell-by-feature matrix (TileMatrix or top features), normalize via TF-IDF (Signac/ArchR) or use spectral embedding (SnapATAC2), then reduce dimensions and cluster. CRITICAL: in Signac the first LSI component correlates with sequencing depth, not biology, so it must be skipped in UMAP and clustering (use dims 2:30); including it produces a UMAP with a linear depth gradient. ArchR (iterative LSI) and SnapATAC2 (spectral) handle the depth component automatically. Cluster with Leiden at a chosen resolution.

## Per-Cluster Peak Calling

Aggregate fragments per cluster into pseudobulk and call peaks with MACS3 per cluster, then build an iterative-overlap consensus peakset across clusters to obtain a unified peak-by-cell matrix for differential accessibility and motif analysis. Use the TileMatrix for clustering (faster) but the PeakMatrix for downstream biology, because ATAC signal lives at peaks, not arbitrary bins. Require >=200 cells per cluster for reliable MACS3 calling (it needs >=1M reads in pseudobulk); pool small clusters into a 'rare' group or drop them and use the union of larger-cluster peaks as a fallback.

## Cell-Type Annotation

Derive a gene-activity matrix (gene scores from peak accessibility near gene bodies/TSS), normalize it, and use marker genes to annotate clusters. Cross-validate annotations across two ecosystems (e.g., Signac + ArchR clusters) for high-confidence calls and report agreement metrics. As QC covariates, score cell cycle (S-phase via a chromatin-adapted signature analogous to Seurat CellCycleScoring, then regress on TF-IDF residuals) and sex chromosomes (XIST locus accessibility vs chrY peak count identifies sex unambiguously; flag sample swaps).

## Multiome Integration (Optional)

For 10X Multiome (paired RNA + ATAC from the same cell, joined by a shared barcode), run per-modality embeddings (PCA on RNA, TF-IDF + SVD on ATAC skipping LSI-1), then compute Weighted Nearest Neighbors (WNN) to learn per-cell modality weights and project a joint UMAP. Watch for ATAC noise dominating the joint embedding: ATAC per-cell signal is much sparser than RNA, so equal modality weighting can swamp the joint space. Inspect per-modality weights and adjust if ATAC weights drive noise.

## Advanced Analyses & Reference Mapping

Optional downstream analyses. Use scArches via PEAKVI (in scvi-tools) to project a query scATAC dataset onto a pre-trained reference atlas by transfer learning without retraining the reference. Use chromBPNet per cluster for bias-corrected per-base profiles and cell-type-specific variant effect prediction, reserving it for the top 5-10 priority clusters (~24h GPU each) since running it per cluster on >20 cell types is computationally heavy. Reconcile results across tools: standardize on Leiden with the same resolution, take the intersection of doublet calls as high-confidence doublets, and ensure identical MACS3 parameters when comparing peak counts.
