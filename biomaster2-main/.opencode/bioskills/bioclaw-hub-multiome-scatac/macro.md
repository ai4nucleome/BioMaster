# Bioclaw Hub Multiome Scatac

## Overview

This workflow processes paired or integrated single-cell RNA and ATAC multiome data. It performs modality-specific quality control, harmonizes features across modalities (peaks, gene activity, expression), integrates them into a joint latent space, interprets regulatory signals (motif accessibility, gene activity, expression patterns), and exports multimodal state summaries. Use this skill when the task involves scATAC, multiome RNA-ATAC, or multimodal single-cell integration requiring a joint view across modalities rather than separate analyses. Expected inputs: multiome object or paired modalities, ATAC fragments or peak matrix, cell metadata. Expected outputs: integrated embeddings, modality-aware clusters, motif or regulatory summaries.

## QC both modalities

Evaluate RNA and ATAC quality independently before joint integration. For RNA, filter cells by minimum gene count and genes by minimum cell count, compute QC metrics including mitochondrial fraction. For ATAC, compute fragment-level QC metrics such as total fragments, TSS enrichment, and fraction of reads in peaks (FRiP). Remove low-quality cells from both modalities based on modality-specific thresholds.

## Create harmonized features

Build peak, gene, or gene activity representations that are consistent across cells and modalities. For multiome data, compute gene activity scores from ATAC peaks by summing accessibility over gene bodies and promoter regions. Ensure the RNA expression matrix and the ATAC-derived gene activity matrix share a common gene index for downstream joint analysis.

## Integrate modalities

Use an approach suited to paired or unpaired multimodal data to learn a joint latent representation. For paired multiome data, scvi-tools MultiVI or totalVI can learn a shared embedding across RNA and ATAC modalities. Alternatively, use canonical correlation analysis (CCA) or weighted nearest neighbor (WNN) integration. The joint embedding captures both shared and modality-specific variation.

## Interpret regulatory signals

Relate motif accessibility, gene activity, and expression patterns cautiously. Perform motif enrichment in differentially accessible peaks between clusters. Correlate gene activity scores with RNA expression to identify regulatory relationships. Compute linkage between peak accessibility and nearby gene expression across cells to infer putative cis-regulatory interactions.

## Export multimodal state summaries

Save joint embeddings, modality-specific QC metrics, and regulatory annotations to disk. Write the integrated anndata object with all embeddings, cluster assignments, and metadata. Export key figures: UMAP colored by modality, cluster, and QC metrics. Save regulatory tables (motif enrichments, peak-to-gene links) as CSV for downstream interpretation.
