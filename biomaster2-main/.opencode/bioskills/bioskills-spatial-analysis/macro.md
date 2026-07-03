# Bioskills Spatial Analysis

## Overview

This workflow analyzes spatial cell-cell interactions in multiplexed imaging (IMC) data using squidpy. It expects a phenotyped AnnData object as input: spatial (x, y) coordinates must be stored in `adata.obsm['spatial']` and cell type labels in `adata.obs['cell_type']` (a categorical). The pipeline builds a spatial neighborhood graph from the coordinates, runs statistical tests for enrichment/depletion of cell-type pairs (neighborhood enrichment, co-occurrence, Ripley's L, interaction matrix, and a permutation-based p-value for specific pairs), characterizes local microenvironments via per-cell neighborhood composition vectors and interaction hotspots, identifies spatial domains with Leiden clustering on the spatial graph, and finally visualizes spatial patterns and exports the annotated object plus summary tables. Use this skill after cell phenotyping is complete and you want to ask which cell types interact spatially, where interactions concentrate, and how the tissue partitions into spatial domains. Outputs include an annotated `imc_spatial_analyzed.h5ad`, a `neighborhood_enrichment.csv` z-score matrix, and several PNG figures. Reference versions: anndata 0.10+, scanpy 1.10+, squidpy 1.3+, scipy 1.12+, matplotlib 3.8+; verify installed versions and adapt API calls if they differ.

## Build Spatial Graph

Load the phenotyped AnnData object and construct a spatial neighbor graph from the (x, y) coordinates stored in `obsm['spatial']`. This graph is the foundation for every downstream spatial analysis. Use Delaunay triangulation (`delaunay=True`) for general point patterns, or a fixed pixel radius (`radius=N`) when cells are roughly uniformly distributed and you want distance-bounded neighbors. The resulting connectivities are written to `adata.obsp['spatial_connectivities']` and the number of edges can be inspected to sanity-check graph density.

## Interaction Enrichment & Statistical Testing

Quantify whether cell-type pairs are spatially enriched or depleted relative to random expectation. Neighborhood enrichment computes a z-score per cell-type pair from permutation; co-occurrence measures pairwise association across distance bands; Ripley's L function tests for clustering versus dispersion as a function of radius (L(r) > r indicates clustering, L(r) < r dispersion, L(r) = r randomness); the interaction matrix summarizes total interactions per pair. Any specific pair of interest (e.g. CD8 T cell vs Tumor) can be formally tested by converting the permutation z-score into a two-sided p-value via the normal CDF.

## Neighborhood Composition & Hotspots

Characterize the local microenvironment around each cell by computing the fractional cell-type composition of its spatial neighbors. This is done by multiplying the spatial connectivity matrix by a one-hot encoding of cell types and row-normalizing, yielding per-cell neighborhood composition vectors stored back into `adata.obs` as `nhood_frac_<celltype>` columns. Additionally, locate interaction hotspots — regions where two cell types of interest (e.g. CD8 T cell and Tumor) are frequently found within a given radius — by querying a k-d tree built on one population for each cell of the other and counting neighbors within the radius.

## Spatial Clustering

Identify spatial domains by running Leiden community detection directly on the spatial connectivity graph (optionally combined with molecular information). Lower resolution yields fewer, larger domains; higher resolution yields finer partitions. The resulting cluster labels are stored under a new key (e.g. `spatial_cluster`) for downstream visualization and comparison with cell-type annotations.

## Visualization & Export

Visualize spatial patterns by plotting cells in physical space colored by cell type, marker expression, or spatial cluster. Highlight specific cell-type interactions by overlaying selected populations (e.g. CD8 T cell and Tumor) on a gray background of all cells. Finally, persist the annotated AnnData object to disk and export summary tables — such as the neighborhood enrichment z-score matrix — to CSV for downstream reporting.
