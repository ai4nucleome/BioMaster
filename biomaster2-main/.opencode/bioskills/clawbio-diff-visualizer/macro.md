# Clawbio Diff Visualizer

## Overview

The Differential Visualizer repackages completed bulk RNA-seq differential expression and single-cell marker/contrast outputs into publication-style figures and self-contained, reproducible reports. It auto-detects upstream outputs from `rnaseq-de` or `scrna-orchestrator` (or accepts direct DE/marker tables), validates required columns, renders the appropriate figure set, and writes a shareable report bundle.

**Inputs**: a DE/marker table (CSV/TSV) or an upstream output directory; optionally bulk counts + metadata, or an AnnData (`.h5ad`) file for scRNA enhancement. Required columns vary by input type — bulk DE needs `gene`, `log2FoldChange`, plus `padj` or `pvalue`; scRNA contrast needs `names` and `scores`; within-cluster contrast needs `cluster`, `comparison_id`, `group1`, `group2`, `names`, `scores`; cluster markers need `cluster`, `names`, `scores`.

**Outputs**: `report.md`, `report.html`, `result.json`, a `figures/` bundle (volcano, MA, top-gene bars, heatmaps, contrast volcanoes, marker bars, dotplots, UMAP panels as applicable), summary `tables/`, and `reproducibility/` artifacts (`commands.sh`, `environment.yml`, `checksums.sha256`).

**When to use**: downstream of any bulk DE or scRNA marker/contrast analysis when richer figures and a shareable report are needed. No DE statistics are recomputed — only lightweight visual ranking and summary logic is applied. The skill is local-first and degrades gracefully when `anndata`/`scanpy` context is unavailable.

## Input Detection & Validation

Identify whether the input is bulk RNA-seq or scRNA, and whether it is an upstream output directory or a direct result table. For directories, look for known upstream files: `tables/de_results.csv` for rnaseq-de outputs; `contrastive_markers_full.csv`, `within_cluster_contrastive_markers_full.csv`, or `markers_top.csv` for scrna-orchestrator outputs. For direct tables, infer the type from the column schema. Validate that all required columns are present for the detected type and reject ambiguous or unsupported inputs with clear guidance about what columns are expected. This stage gates everything downstream — a misclassified or malformed input must fail fast with an actionable message.

## Bulk Differential Visualization

Render bulk RNA-seq differential figures from a validated DE table. Produce a volcano plot of log2 fold change versus significance, and a top-genes bar chart of the most strongly changing genes. When an MA plot is supported by the data, render it as well. When optional counts and metadata are supplied, additionally render a top-genes heatmap to show expression patterns across samples. No DE statistics are recomputed — only lightweight visual ranking and summary logic is applied to the already-computed table.

## scRNA Marker Visualization

Render scRNA marker and contrast figures. For dataset-level contrast tables, produce contrast volcanoes and marker ranking bars. For within-cluster contrast tables, produce within-cluster comparison panels keyed by cluster and comparison. For cluster marker tables, produce marker ranking bars. When an AnnData file is supplied and the grouping axis is unambiguous, additionally render marker dotplots, marker heatmaps, and UMAP feature panels. All enhanced plots degrade gracefully if `anndata` or `scanpy` context is unavailable, falling back to table-only figures.

## Report & Reproducibility

Assemble the final report bundle from the rendered figures and summary tables. Write a human-readable `report.md` and a self-contained `report.html`, a machine-readable `result.json`, summary tables (`top_genes.csv`, `significant_genes.csv`, `top_markers.csv`, `top_markers_by_cluster.csv` as applicable), and reproducibility artifacts (`commands.sh`, `environment.yml`, `checksums.sha256`). All reports include the ClawBio medical/research disclaimer. This stage runs automatically at the end of every invocation.
