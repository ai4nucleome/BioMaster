# Bioskills Markers Annotation

## Overview

This workflow identifies cluster-specific marker genes via differential expression, visualizes their expression patterns, scores curated gene sets (including cell cycle phase), and assigns cell type labels to clusters.

**Inputs:** A clustered, normalized single-cell object — an `AnnData` (Scanpy) with a `leiden` (or similar) column in `adata.obs`, or a `Seurat` object with `Idents` set to cluster identities. Expression should be log-normalized.

**Outputs:** A ranked marker gene table (CSV), the object updated with module/cell-cycle scores and a `cell_type` metadata column, and diagnostic plots (dot plot, stacked violin, heatmap, UMAP colored by cell type and scores).

**When to use:** Run this skill *after* clustering and normalization, and *before* downstream comparative or trajectory analysis. It is the standard route from "I have clusters" to "I know what cell type each cluster is." Both Python (Scanpy) and R (Seurat) paths are provided; pick the one matching your object. Reference examples were tested with DESeq2 1.42+, pandas 2.2+, scanpy 1.10+ — verify installed versions and introspect APIs if signatures differ.

## Marker Detection

Run differential expression testing to find genes enriched in each cluster versus all others (or between two specific clusters). The default Wilcoxon rank-sum test is robust and parameter-free; alternatives include the t-test, logistic regression (Scanpy), and MAST or DESeq2 (Seurat). This step produces a ranked marker table per cluster that drives every downstream annotation decision. Always inspect the top-ranked genes per cluster before proceeding.

## Marker Filtering & Visualization

Filter the raw marker list by adjusted p-value, log-fold change, and in-group fraction to retain only confident, cluster-specific hits. Then visualize expression across clusters with dot plots, stacked violins, heatmaps, and matrix/feature plots. These plots reveal which markers cleanly separate clusters and provide the visual evidence needed for manual cell type annotation.

## Gene Set & Cell Cycle Scoring

Score each cell for the expression of curated gene sets (e.g., a T-cell signature) and assign cell cycle phases (S versus G2/M) using canonical gene lists. Module scores add a quantitative signal that complements discrete clustering, while cell cycle scoring separates proliferating from resting populations — both of which refine downstream annotation and interpretation.

## Cell Type Annotation

Map cluster identities to biological cell type labels using the top marker genes from earlier steps together with canonical reference markers (e.g., the PBMC marker table below). Store the labels in object metadata and visualize them on the embedding. Annotation is typically manual and iterative — guided by which known markers each cluster enriched.

## Export

Persist the marker table and annotated object to disk for sharing, reproducibility, and downstream analysis. Export both the full marker table and a per-cluster top-N summary so collaborators can review the evidence behind each annotation.
