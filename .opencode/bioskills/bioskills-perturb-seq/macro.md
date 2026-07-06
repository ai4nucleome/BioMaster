# Bioskills Perturb Seq

## Overview

This workflow links CRISPR guide RNA assignments to single-cell transcriptional phenotypes in pooled CRISPR screens with single-cell readout (Perturb-seq, CROP-seq, ECCITE-seq), enabling identification of gene function from perturbation effects.

**Inputs:** A filtered feature-barcode expression matrix (h5ad or 10x) plus CRISPR Guide Capture output (e.g., Cell Ranger `protospacer_calls_per_cell.csv`) mapping cell barcodes to guide identities and target genes.

**Outputs:** An annotated AnnData/Seurat object with guide metadata, per-perturbation differential expression tables, perturbation signature matrices, perturbation-level embeddings and clusters, Mixscape perturbation-status classifications (perturbed vs escaped), and pathway enrichment results.

**When to use:** Pooled CRISPR screens with single-cell transcriptomic readout where the goal is to quantify transcriptional phenotypes per perturbation, classify successfully perturbed cells, group functionally related perturbations, and interpret affected pathways.

The workflow supports two execution paths: Python (pertpy/scanpy/decoupler) for DE, signatures, embeddings, and enrichment, and R (Seurat v5 Mixscape) for perturbed-vs-escaped cell classification. Reference versions: MAGeCK 0.5+, pandas 2.2+, pertpy 0.7+, scanpy 1.10+. Before running, verify installed package versions match and introspect APIs if ImportErrors or TypeErrors arise.

## Guide Assignment & Annotation

Load the single-cell expression matrix and link each cell to its CRISPR guide and target gene. Parse the Cell Ranger CRISPR Guide Capture protospacer calls, clean cell barcodes by stripping the trailing suffix, retain only single-guide cells, and merge guide metadata into the AnnData object. Mark non-targeting guide cells as controls via an `is_control` flag. The result is an annotated AnnData with `guide_id`, `target_gene`, and `is_control` columns in `obs`, ready for QC and perturbation analysis.

## Guide Quality Control

Assess and filter guide representation to ensure robust downstream statistics. Quantify cells per guide and guides per target, drop guides below a minimum cell threshold (default 100 cells), and inspect guide bias via violin plots of quality metrics grouped by target gene. Decide how to handle multi-guide (MOI > 1) cells: remove them, restrict to same-target combinations, or retain for combinatorial analysis. Reference QC thresholds: cells per guide (>200 good, 100-200 acceptable, <100 poor); guide detection rate (>90% good, 80-90% acceptable, <80% poor); non-targeting cell fraction (5-15% good, 15-25% acceptable, >25% poor); Mixscape KO fraction (>50% good, 30-50% acceptable, <30% poor).

## Perturbation Differential Expression & Signatures

Quantify transcriptional effects per perturbation versus non-targeting controls using pertpy. Aggregate cells to pseudobulk by target gene and run differential expression (DESeq2, edgeR, or Wilcoxon) with a minimum cell count filter, then filter significant genes by adjusted p-value. Separately, compute per-perturbation effect-size signatures via PerturbationSignature against the non-targeting control to obtain a perturbation signature matrix. Outputs are a DE results table (with log2FoldChange and padj) and a signature matrix summarizing each perturbation's transcriptional footprint.

## Perturbation Embedding & Clustering

Project perturbations into a phenotype-level embedding (mean-based by default) and cluster them to identify functionally related perturbations. Visualize the structure with a perturbation heatmap grouped by perturbation cluster. This step reveals modules of genes with shared phenotypic effects and is useful for functional grouping of hits from the screen.

## Mixscape Classification (Seurat v5)

Classify each cell as successfully perturbed (knockout) or escaped using Seurat v5 Mixscape. After standard Seurat preprocessing (normalize, find variable features, scale, PCA, UMAP), CalcPerturbSig computes per-cell perturbation signatures against non-targeting controls using PCA-projected differences with k-nearest neighbors. RunMixscape then fits a mixture model to separate knockout-responsive cells from escapees, requiring a minimum number of DE genes and multiple iterations. Requires a Seurat object with perturbation metadata in the `gene` column and non-targeting class labeled `NT`.

## Visualization & Pathway Enrichment

Visualize Mixscape results and interpret perturbation effects via pathway enrichment. Generate UMAPs colored by mixscape class, violin plots of perturbation scores per gene, heatmaps of DE genes for each perturbation versus non-targeting controls, and LDA projections that maximally separate perturbed from control cells. Then run over-representation analysis (ORA) on DE results against MSigDB gene sets with decoupler to identify affected pathways and visualize top hits per perturbation.
