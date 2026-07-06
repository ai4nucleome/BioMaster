# Bioskills Phenotyping

## Overview

This workflow assigns cell types to segmented Imaging Mass Cytometry (IMC) single cells based on protein marker expression. It takes per-cell marker intensities — either from an existing h5ad AnnData file or from CSV tables of cell intensities plus cell metadata — and produces an annotated AnnData object carrying a `cell_type` label per cell, together with UMAP / heatmap / spatial visualizations and per-ROI cell-type frequency tables. Use this skill after cell segmentation has yielded single-cell intensity measurements; it supports three complementary phenotyping strategies so the user can choose based on marker panel and reference availability: (1) unsupervised Leiden clustering followed by marker-based annotation, (2) manual threshold gating on key markers, and (3) SOM-based (FlowSOM-style) or supervised reference-based classification. Final outputs are written to `imc_phenotyped.h5ad` and `cell_phenotypes.csv`. Reference examples were tested with FlowSOM 2.10+, anndata 0.10+, matplotlib 3.8+, numpy 1.26+, pandas 2.2+, scanpy 1.10+, and scikit-learn 1.4+; verify installed versions and adapt API calls if ImportErrors or TypeErrors arise.

## Data Loading & Transformation

Load single-cell IMC data either from an existing h5ad AnnData file or by constructing an AnnData object from CSV tables of per-cell marker intensities and cell metadata. Apply an arcsinh transformation with a cytometry-standard cofactor to stabilize variance, then z-score scale the expression matrix so it is ready for downstream clustering and classification.

## Unsupervised Clustering

Reduce dimensionality with PCA, build a k-nearest-neighbor graph, and run Leiden clustering to group cells into phenotypically distinct communities. Compute a UMAP embedding and plot the clusters so the user can inspect the unsupervised structure before annotation. This is the primary unsupervised phenotyping route.

## Cluster Annotation & Manual Gating

Identify marker genes defining each Leiden cluster with a Wilcoxon rank-genes test, inspect them on a heatmap, and assign biological cell types by mapping cluster IDs to known identities. As an alternative annotation route, apply a manual gating strategy that thresholds key markers (e.g. CD45, CD3, CD8, CD4) and assigns cell types through a hierarchical decision rule, storing both per-marker positivity flags and the final cell-type label in adata.obs.

## Alternative Phenotyping (SOM & Supervised)

Two complementary approaches when Leiden clustering is not the best fit. (a) FlowSOM-style phenotyping: train a self-organizing map on a selected set of phenotype markers, map each cell to its best-matching unit, and meta-cluster the SOM node weights with agglomerative clustering to obtain final cell-type clusters. (b) Supervised reference-based annotation: train a k-nearest-neighbor classifier on a labeled reference IMC dataset and predict cell types plus prediction-confidence probabilities for the query cells.

## Visualization, Frequencies & Export

Visualize the assigned phenotypes as a UMAP colored by cell type, a marker matrixplot grouped by cell type, and a spatial scatter showing cell-type localization within each ROI. Compute per-image cell-type frequency tables (counts and percentages) and plot stacked bar charts of composition. Finally, save the annotated AnnData object to h5ad and export a CSV of cell phenotypes with identifiers and centroid coordinates.
