# Bioskills Clustering Phenotyping

## Overview

This workflow discovers cell populations in high-dimensional flow or mass cytometry data by unsupervised clustering, then annotates clusters as cell types and quantifies their abundance across samples. Inputs: a flowSet (or FCS files) plus a marker panel (classifying markers as 'type' vs 'state') and sample metadata. Outputs: a SingleCellExperiment (SCE) object carrying cluster and cell-type assignments, dimensionality-reduction embeddings, per-sample abundance tables, and exported CSV/RDS artifacts. Use this workflow when you want to phenotype cytometry data without predefined gates, e.g. for exploratory population discovery and comparative abundance analysis across conditions. The pipeline is built around the R CATALYST package, with FlowSOM and Phenograph as alternative clustering engines, and batchelor for optional batch correction. Reference versions: FlowSOM 2.10+, CATALYST compatible with scanpy 1.10+ era SingleCellExperiment. Before running, verify installed package versions with packageVersion() and adapt parameter names to the actual API if an ImportError/AttributeError/TypeError occurs.

## Data Preparation

Convert a flowSet into a SingleCellExperiment (SCE) using CATALYST's prepData, applying an arcsinh transformation with a cofactor (typically 5 for mass cytometry). Associate the marker panel, which classifies each marker as 'type' (used for clustering) or 'state' (used for downstream characterization), together with sample metadata. This step produces the normalized SCE that all subsequent clustering, visualization, and annotation operate on.

## Clustering

Cluster cells into populations using unsupervised methods on the 'type' markers. The primary path is CATALYST's cluster() wrapper around FlowSOM, which builds a self-organizing map grid and consolidates it into a configurable number of metaclusters (controlled by maxK). Phenograph is offered as a graph-based alternative that builds a k-nearest-neighbor graph and partitions it with Louvain community detection. The result is a set of cluster/metacluster IDs stored on the SCE and accessible via cluster_ids(); a standalone FlowSOM call on a single flowFrame is also shown for cases where the full SCE pipeline is not used.

## Dimensionality Reduction & Visualization

Project cells into 2D with UMAP or tSNE on the type markers using CATALYST's runDR wrapper, then visualize the embeddings colored by cluster, cell type, or metadata variables such as batch or condition. These plots are the primary way to sanity-check clustering quality and to spot batch effects or sample-driven structure before annotation.

## Cluster Annotation & Merging

Assign biological labels to clusters by inspecting median marker expression. Use plotExprHeatmap to compare marker profiles across metaclusters and the NRS / delta-area plot to choose an appropriate K before committing to a resolution. Manually map cluster IDs to cell type names and store the result as a new column on the SCE. When clustering is too granular, use mergeClusters with a mapping table to consolidate similar clusters into biologically meaningful populations.

## Abundance & Marker Expression Analysis

Quantify how each cell population is distributed across samples and conditions, and summarize marker expression per cluster. Compute per-sample cluster proportions by cross-tabulating cluster IDs against sample IDs, then visualize grouped abundances with plotAbundances. Inspect per-cluster median expression with plotClusterExprs and pseudo-bulk expression faceted by cluster with plotPbExprs. These summaries support comparative analysis between conditions.

## Export & Batch Integration

Persist results for downstream use and sharing by writing cluster assignments and cell metadata to CSV and serializing the full annotated SCE as an RDS file. If batch effects are visible on the UMAP (e.g. samples separating by batch rather than biology), optionally correct them with batchelor's fastMNN before or after clustering and re-inspect the embedding to confirm the effect is reduced.
