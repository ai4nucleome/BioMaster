# Bioskills Spatial Domains

## Overview

This workflow identifies spatial domains — anatomically coherent tissue regions — in spatial transcriptomics data by combining gene expression with physical spot/cell proximity. **Inputs:** an AnnData object with spatial coordinates in `adata.obsm['spatial']` and a processed expression matrix (typically after standard QC, normalization, and PCA). **Outputs:** categorical domain labels added to `adata.obs` (e.g. `spatial_leiden`, `combined_leiden`, `domain`), tissue-overlay plots, per-domain marker genes, and quantitative quality metrics (silhouette, ARI). **When to use:** when you need to segment Visium / Slide-seq / Stereo-seq tissue into biologically meaningful regions rather than expression-only clusters — for example delineating cortex layers, white/gray matter, or tumor/stroma boundaries. The workflow proceeds from a baseline expression-only Leiden clustering, through several spatially-aware detection strategies (Squidpy spatial graph, a combined expression+spatial graph, BayesSpace via R, and STAGATE graph-attention embeddings), to boundary refinement, quantitative evaluation and method comparison, and finally marker-gene-driven biological annotation.

## Setup & Baseline Clustering

Set up the Python environment and verify that installed library versions (squidpy, scanpy, numpy, pandas, scipy, scikit-learn, matplotlib) match the reference versions; if they differ, introspect the actual API rather than retrying. Build an expression-only neighbor graph and run Leiden clustering as a baseline that ignores spatial context, so that later spatial methods can be compared against it. Visualize the baseline clusters overlaid on the tissue. This baseline also serves as the `connectivities` graph reused by the combined-graph strategy in the next step.

## Spatial Domain Detection

Detect spatially coherent domains using one or more spatially-aware strategies; each stores results under a distinct key in `adata.obs` so they can be compared later. (a) Squidpy spatial graph + Leiden clusters spots by physical proximity to find contiguous tissue regions. (b) Combined graph merges L1-normalized expression and spatial connectivities as a weighted average, then clusters on the joint graph to integrate both expression similarity and spatial proximity. (c) BayesSpace, run in R and imported via rpy2, applies spatial smoothing for domain detection. (d) STAGATE trains a graph attention network to learn spatially-aware embeddings that are then clustered with Leiden. Choose the method that best fits the platform and resolution; the combined-graph and STAGATE approaches generally give the best balance of transcriptional and spatial coherence.

## Domain Refinement

Smooth noisy domain assignments to produce cleaner spatial boundaries. Using the spatial neighbor graph, iteratively reassign each spot to the most common label among its spatial neighbors (majority-vote smoothing) for a configurable number of iterations. This removes isolated single-spot misassignments and yields more contiguous regions. Compare original and smoothed labels side by side on the tissue to confirm the improvement.

## Evaluation & Comparison

Quantitatively assess domain quality and compare methods. Compute silhouette scores on both spatial coordinates and expression PCA to measure, respectively, the spatial contiguity and transcriptional coherence of the identified domains. Use the adjusted Rand index (ARI) to compare agreement across different clustering methods (e.g. expression-only vs spatial vs combined), which helps decide which strategy to carry forward to annotation.

## Marker Genes & Annotation

Identify marker genes that distinguish each spatial domain and assign biological labels. Run Wilcoxon rank-sum tests per domain to extract top differentially expressed genes and visualize the top marker per domain on the tissue. Then map cluster IDs to anatomical region names via a dictionary (informed by the marker genes and tissue biology) to produce annotated domain labels, and plot the annotated tissue for downstream interpretation.
