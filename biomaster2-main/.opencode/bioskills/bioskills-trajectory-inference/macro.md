# Bioskills Trajectory Inference

## Overview

This workflow infers developmental trajectories and pseudotime ordering from single-cell data. It supports multiple complementary approaches: graph-based pseudotime (Monocle3, PAGA/diffusion pseudotime), lineage-based principal curves (Slingshot), and RNA velocity (scVelo/velocyto). Inputs are a clustered single-cell object (Seurat, SingleCellExperiment, or AnnData) with an embedding; for RNA velocity, spliced/unspliced count matrices from velocyto are also required. Outputs include pseudotime values per cell, lineage structure, branch points, and genes varying along the trajectory. Use this workflow after standard QC, normalization, and clustering to model continuous developmental processes, identify progenitor-to-differentiated transitions, and predict future cell states.

## Input Preparation & Preprocessing

Prepare the single-cell object and any auxiliary inputs required by the chosen trajectory method. Verify tool and version compatibility (Cell Ranger 8.0+, scanpy 1.10+, Monocle3, Slingshot, scVelo) before running, introspecting installed APIs if versions differ. For RNA velocity approaches, generate spliced/unspliced count matrices with velocyto from Cell Ranger or SmartSeq2 BAM files. Convert between object formats as needed: Seurat to cell_data_set for Monocle3, Seurat to SingleCellExperiment for Slingshot, and merge velocyto loom files into AnnData for scVelo.

## Dimensionality Reduction & Clustering

Ensure the object has a reduced-dimension embedding and cluster labels, which are prerequisites for all trajectory methods. For Monocle3, preprocess the cell_data_set with PCA and UMAP if not already done, then cluster cells. For Slingshot and PAGA, supply an existing UMAP embedding and cluster labels (e.g. from Seurat or scanpy Leiden clustering). Clustering defines the nodes that trajectory graphs connect.

## Trajectory Graph Construction

Build the structural graph that represents the trajectory. Monocle3 learns a principal graph through the data manifold with learn_graph. Slingshot constructs a minimum spanning tree over cluster centroids and fits smooth principal curves per lineage, optionally specifying start and end clusters. Scanpy PAGA abstracts the connectivity between clusters and can initialize a force-directed layout. Each method produces a graph or curve object that encodes lineage topology.

## Pseudotime Ordering & Root Selection

Assign each cell a pseudotime value by ordering cells along the trajectory graph from a defined root. For Monocle3, select the root principal graph node, either interactively or programmatically by finding the node closest to a known progenitor cluster, then call order_cells. For PAGA/scanpy, set iroot to a cell in the root cluster and compute diffusion pseudotime. For scVelo dynamical mode, latent_time provides a model-derived pseudotime. Slingshot returns per-lineage pseudotime matrices directly from the slingshot call.

## RNA Velocity Estimation

Estimate RNA velocity to predict the direction and speed of cell state transitions from spliced/unspliced transcript ratios. After filtering, normalizing, and computing moments, compute velocity with the stochastic model (fast) or the dynamical model (more accurate, recovers full kinetics). Build the velocity graph to connect cells by likely transitions, then visualize as a stream plot on the UMAP. Assess velocity confidence and length per cell.

## Branch Point & Gene Dynamics Analysis

Identify genes that vary along the trajectory and characterize branch points where lineages diverge. In Monocle3, use graph_test (Moran's I) to find genes with spatially autocorrelated expression along the principal graph, then plot expression over pseudotime. In scVelo, rank velocity genes by likelihood and inspect phase portraits. For formal branch analysis, fit generalized additive models with tradeSeq on Slingshot lineages and test for differential expression between branches.
