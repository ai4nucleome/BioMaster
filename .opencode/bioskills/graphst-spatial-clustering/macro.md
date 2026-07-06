# Graphst Spatial Clustering

## Overview

GraphST is a graph self-supervised contrastive learning method for spatially informed clustering of spatial transcriptomics (ST) data. It jointly models gene expression and spatial proximity by building a spot-to-spot spatial neighbor graph, then trains a graph neural network (GNN) with a contrastive learning objective to learn a low-dimensional embedding for every spot. The learned embeddings are clustered (via mclust, Leiden, or Louvain) and optionally refined with spatial label smoothing to produce spatial domains — groups of spots that are both transcriptionally similar and spatially contiguous.

This skill covers the full single-sample clustering workflow for 10X Visium, Stereo-seq, or Slide-seq data: environment setup, data loading and preprocessing, graph construction and representation learning, spatial clustering with refinement, and visualization/evaluation.

Inputs: an AnnData object with spot/barcode coordinates stored in `adata.obsm['spatial']` (e.g. produced automatically by `sc.read_visium`). Outputs: learned spot embeddings in `adata.obsm['emb']` and spatial-domain labels in `adata.obs['domain']`.

Use this skill when you need to identify spatial domains / tissue regions from ST data. It does NOT cover multi-sample integration or scRNA-seq deconvolution (separate GraphST tasks). Key tunables: number of clusters, clustering method, whether to apply spatial refinement, and the GNN training hyperparameters (epochs, learning rate, loss weights alpha/beta).

## Installation & Environment Setup

Set up the GraphST runtime. GraphST requires Python 3.8 with PyTorch (>=1.8, GPU recommended), the scanpy/anndata scientific stack, the POT (python-opttransport) package used internally for distance matrices, and — because the default clustering method is mclust — an R installation with the mclust package reachable through rpy2. GraphST itself is installed via pip (or from source). This step prepares a reproducible conda environment with all of these dependencies.

## Data Loading & Preprocessing

Load the ST data into an AnnData object and ensure the spatial coordinates GraphST depends on are present. For 10X Visium, `sc.read_visium` reads the filtered feature-barcode matrix together with the tissue image and automatically populates `adata.obsm['spatial']`. For Stereo-seq or Slide-seq, build the AnnData manually and store barcode/spot coordinates as an (n_spots, 2) array in `adata.obsm['spatial']`. Basic QC (mitochondrial gene filtering, low-quality spot removal) can be applied first. GraphST's own preprocessing — selection of 3000 highly variable genes (seurat_v3 flavor), total-count normalization to 1e4, log1p, and scaling — runs automatically inside the GraphST constructor when `highly_variable` is not already present, so it does not need to be called manually.

## Graph Construction & Representation Learning

Instantiate and train the GraphST model. The constructor automatically builds the spatial neighbor graph from `adata.obsm['spatial']` (a fixed-radius k-nearest-neighbor graph with n_neighbors=3 for Visium, or a KNN graph for Stereo-seq/Slide-seq), adds contrastive-learning labels, and extracts the feature matrix. Calling `.train()` optimizes a GNN with a reconstruction loss (weighted by alpha) and a contrastive loss (weighted by beta) for the configured number of epochs, then writes the learned spot embeddings into `adata.obsm['emb']`. Use a GPU when available; the embedding dimension (dim_output, default 64) and training length (epochs, default 600) are the main knobs for representation quality.

## Spatial Clustering & Refinement

Cluster the learned embeddings into spatial domains using the `clustering` helper from `GraphST.utils`. It first reduces `adata.obsm['emb']` to 20 PCs (`adata.obsm['emb_pca']`), then applies the chosen method: mclust (default, requires R+mclust), Leiden, or Louvain. For Leiden/Louvain the resolution is automatically searched (between `start` and `end` with the given `increment`) until the target `n_clusters` is reached. Optionally enable `refinement`, which smooths each spot's label by majority vote over its `radius` nearest spatial neighbors, producing more spatially coherent domains. Final labels are written to `adata.obs['domain']`.

## Visualization & Evaluation

Visualize the resulting spatial domains and, when ground-truth region annotations are available, quantify clustering quality. Spatial domain labels are plotted over the tissue image with `sc.pl.spatial`; a UMAP of the learned embedding shows how well domains separate in representation space. If the dataset ships with manual annotations (e.g. layer labels for Visium brain sections), compute the Adjusted Rand Index (ARI) between `adata.obs['domain']` and the ground truth to benchmark the clustering.
