# Bioskills Multiomics Grn

## Overview

The Multiomics GRN Inference workflow builds enhancer-driven gene regulatory networks (eRegulons) from paired single-cell RNA-seq and ATAC-seq (10x Multiome) data. It links transcription factors to their enhancers and downstream target genes by integrating gene expression with chromatin accessibility, going beyond RNA-only SCENIC regulons.

The primary path uses the SCENIC+ pipeline. scRNA-seq is loaded from the CellRanger ARC filtered matrix and filtered; scATAC-seq peaks are called with MACS3 and summarized via cisTopic LDA topic modeling; SCENIC+ then assembles TF-enhancer-gene triplets through motif enrichment, region-to-gene linking, TF-to-region linking, and eRegulon construction. eRegulons are then summarized (activating vs repressive), scored for per-cell activity (AUC), and visualized as dotplots and network plots. An alternative R-based path using FigR is provided for users who want TF-gene regulation without topic modeling.

Inputs: CellRanger ARC `filtered_feature_bc_matrix.h5`, ATAC `fragments.tsv.gz` (BEDPE), a genome blacklist BED (e.g. hg38-blacklist.v2.bed), a TF list file (e.g. `allTFs_hg38.txt`). Outputs: eRegulon metadata tables, per-cell eRegulon AUC matrices (region- and gene-based), and PDF figures (dotplot, network plots); optionally loom and UCSC track exports.

Use this skill when you have paired multiome data and want enhancer-resolved regulatory networks. Resource needs scale with cell count: ~16 GB RAM / 2-4 h for 5K cells, ~64 GB / 8-12 h for 20K cells, 128 GB+ / 24+ h for 50K+ cells (subsample or use HPC). Reference versions tested: Cell Ranger 8.0+, MACS3 3.0+, matplotlib 3.8+, pandas 2.2+, scanpy 1.10+; verify installed versions and adapt API calls if they differ.

## Input Preparation

Load the paired multiome data from CellRanger ARC output. Read the RNA matrix into an AnnData object with scanpy, make variable names unique, and apply basic cell/gene filtering (at least 200 genes per cell, at least 3 cells per gene). Locate the ATAC fragments file (BEDPE format) that will feed downstream peak calling and cisTopic object creation. This step establishes the two inputs (RNA AnnData plus the ATAC fragments path) required by the rest of the pipeline.

## Peak Calling & Topic Modeling

Define the accessible region universe by calling peaks from the ATAC fragments file with MACS3 in BEDPE mode (shift -75, extend 150, no model, keep all duplicates, hs genome). Build a cisTopic object from the fragments and the called peaks against a genome blacklist, then run Latent Dirichlet Allocation topic modeling across a range of topic counts (e.g. 10, 20, 30, 40, 50). Select the best model by coherence/perplexity using evaluate_models and attach it to the cisTopic object. The resulting topics summarize cis-regulatory programs and feed SCENIC+ region-to-gene linking.

## SCENIC+ eRegulon Inference

Construct a SCENICPLUS object from the preprocessed RNA AnnData and the cisTopic object, then run the complete SCENIC+ pipeline. The pipeline performs motif enrichment to identify candidate transcription factors, links accessible regions to target genes (region-to-gene), connects TFs to their enhancer targets (TF-to-region), and assembles these into eRegulons (TF-enhancer-gene triplets). Key parameters include the upstream/downstream search window around the TSS (default 1 kb to 150 kb), the species and assembly, and a TF list file. Optionally compute TF-eGRN correlations, DEGs/DARs, and export to loom and UCSC track formats.

## eRegulon Interpretation & Scoring

Parse the eRegulon metadata table to summarize the number of regions and target genes per transcription factor, ranking TFs by target gene count. Separate activating eRegulons (name suffix containing '(+)') from repressive ones (suffix containing '(-)') based on the correlation between TF expression and target activity. Score eRegulon activity per cell using region-based and gene-based enrichment (analogous to AUCell), producing AUC matrices that quantify how active each eRegulon is in each cell.

## Visualization

Visualize eRegulon activity and structure. Use a heatmap dotplot to show eRegulon activity (gene-based size, region-based color) grouped by cell type, and plot individual eRegulon networks for specific TFs of interest (e.g. PAX5). Save figures as PDF for downstream interpretation and publication.

## FigR Alternative (R)

An alternative R-based workflow using FigR that infers TF-gene regulatory interactions from paired scRNA+scATAC without topic modeling. From a Seurat object with RNA and ATAC assays (built with Signac), first compute peak-gene correlations with runGenePeakcorr (significance threshold p.cut=0.05), then infer TF-gene regulation scores with runFigR using DORC (degree of regulatory co-accessibility) scores derived from the peak-gene links. Rank the resulting TF-gene links by absolute score to identify top regulators. Use this path when topic modeling is undesirable or unavailable.
