# Bioskills Scirpy Analysis

## Overview

This workflow integrates single-cell immune receptor (TCR/BCR) VDJ annotations with scRNA-seq gene expression data using scirpy, enabling joint analysis of clonal expansion and cell state. It takes as input an existing scRNA-seq AnnData object (e.g. from a prior clustering/annotation workflow) together with 10x filtered_contig_annotations.csv or AIRR-format rearrangement files, and produces an annotated AnnData with clonotype identities, expansion categories, diversity metrics, V(D)J gene usage summaries, and gene-expression markers of expanded clones. Use this skill when you have paired scRNA-seq + VDJ data and want to characterize clonal architecture, compare repertoires across samples/conditions, or link clonotypes to transcriptional states. Typical outputs include clonotype tables (CSV), AIRR-format exports for tools like VDJtools, and UMAP/marker plots colored by clonal expansion. Reference versions: MiXCR 4.6+, VDJtools 1.2.1+, scanpy 1.10+; verify installed versions before running and adapt API calls if ImportErrors or TypeErrors arise.

## Data Loading & Chain QC

Import single-cell VDJ annotations from 10x filtered_contig_annotations.csv or AIRR-format rearrangement files and attach receptor metadata to an existing scRNA-seq AnnData object. Then run scirpy chain QC to categorize each cell by its receptor chain pairing status (e.g. multichain/doublet, orphan, extra, ambiguous) and visualize the distribution of chain-pairing categories across receptor subtypes. This step establishes which cells carry valid immune receptors and flags low-quality or doublet-like cells for downstream filtering.

## Clonotype Definition

Compute CDR3 sequence distances between immune receptors and assign cells to clonotypes based on shared CDR3 amino-acid identity. Cells with identical receptor configurations (considering all receptor arms and the primary VDJ/VJ chain) are grouped into a single clonotype, recorded in adata.obs['clone_id']. This is the foundational grouping used by all subsequent clonal analyses.

## Clonal Expansion Analysis

Quantify how many cells belong to each clonotype and categorize them by expansion size (singleton, 2, 3-10, >10). Expanded clonotypes indicate antigen-driven proliferation and can be visualized stratified by cell type to reveal which transcriptional states harbor expanded clones.

## Repertoire Diversity & Comparison

Compute repertoire overlap (e.g. Jaccard) and alpha-diversity metrics per sample or condition to quantify how similar repertoires are across groups and how diverse each repertoire is. Visualize clonotype sharing between conditions via group abundance plots and a repertoire overlap heatmap to identify shared or condition-specific clonotypes.

## V(D)J Gene Usage

Summarize and visualize V(D)J gene segment usage and CDR3 length distributions (spectratypes) across cell types or conditions. These plots reveal biases in V/J gene usage and CDR3 length that may indicate antigen-driven selection or shared antigen specificity.

## Gene Expression Integration

Link clonotype/expansion information to transcriptional state by subsetting to cells with detected immune receptors and identifying marker genes differentially expressed between expanded and non-expanded clones. Visualize UMAP embeddings colored by cell type and clonal expansion to connect clonal identity with gene-expression-defined cell states.

## Export for Downstream Analysis

Export clonotype summary tables (clone id, CDR3 amino-acid sequences, V/J gene calls) as CSV and write the full receptor annotations in AIRR format for interoperability with downstream tools such as VDJtools. These exports preserve the clonotype-to-cell mapping and receptor sequences for external analysis or sharing.
