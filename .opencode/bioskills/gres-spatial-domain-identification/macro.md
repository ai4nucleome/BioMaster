# Gres Spatial Domain Identification

## Overview

GreS (Semantic-Guided Spatial Representation Learning) is a framework for spatial domain identification in spatial transcriptomics. It augments sparse, noisy expression measurements with gene-level semantic priors: curated NCBI Gene functional descriptions encoded with text-embedding-3-large, refined through a NicheNet gene regulatory network (GRN), and aggregated into spot-level semantic descriptors weighted by each spot's expression profile. GreS constructs complementary neighborhood graphs over spots — a spatial graph from physical coordinates and a feature/semantic graph from functional similarity — encodes them with parallel graph convolutional (GCN) branches, and uses the spot-level semantic descriptors to adaptively gate and fuse the view-specific embeddings. The fused representation is trained end-to-end with a zero-inflated negative binomial (ZINB) reconstruction objective plus spatial neighborhood regularization and cross-view decorrelation, then partitioned with k-means to yield spatial domains.

Inputs: 10x Visium or Stereo-seq data — raw gene expression counts, spatial coordinates, and (optionally) per-spot ground-truth annotations. Outputs: an AnnData object with predicted cluster labels in `obs['idx']` and a spatial cluster plot PNG. Use GreS when expression signals are sparse or weakly discriminative and gene functional semantics can add discriminative power across layered brain tissue, embryonic development, or heterogeneous tumor microenvironments. The pipeline runs in three executable stages — data preprocessing, semantic embedding generation, and training/clustering — preceded by a one-time installation and resource download.

## Installation & Resource Setup

Set up the GreS Python environment and download the required pretrained gene semantic resources. GreS depends on Python 3.9+ and PyTorch 1.13+. The semantic branch relies on pretrained gene embeddings and a vocabulary that must be fetched from the project's Hugging Face repository and placed in a fixed directory before any preprocessing or training can run. This is a one-time setup step.

## Data Preparation

Organize raw spatial transcriptomics data into the directory layout GreS expects. Each dataset is identified by a `dataset_id` and placed under `data/raw_h5ad/<dataset_id>/`. For 10x Visium samples this folder must contain the filtered feature-barcode matrix H5 file, the spatial metadata folder, and a metadata.tsv with per-spot annotations. Alternatively, a pre-built .h5ad carrying raw counts in `adata.X`, spatial coordinates in `adata.obsm['spatial']`, and a label column in `adata.obs` is accepted.

## Data Preprocessing

Build a graph-augmented AnnData from the raw data using the preprocessing script. This step runs the standardized Scanpy pipeline described in the paper: filter genes expressed in fewer than 100 spots, select the top 3000 highly variable genes via the Seurat v3 dispersion method, normalize counts to 1e4 per spot, log-transform, scale to zero mean and unit variance with values clipped at 10, and construct the spatial neighborhood graph from coordinates. Raw integer counts are retained to supervise the ZINB reconstruction loss. The resulting `data.h5ad` is written for downstream steps.

## Generate Semantic Embeddings

Construct per-spot semantic descriptors that encode gene functional context. This step loads the pretrained gene semantic embeddings and vocabulary, restricts them to the genes present in the dataset, refines them via gene regulatory network propagation using the NicheNet prior (with propagation weight alpha_grn = 0.2), and aggregates the refined gene semantics into spot-level descriptors weighted by each spot's expression profile. Genes without curated descriptions receive zero vectors. The resulting spot semantic embeddings are saved as .npy files consumed during training.

## Training & Clustering

Train the GreS model end-to-end and identify spatial domains. The model encodes the complementary spot graphs with parallel GCN branches (hidden dimension 256, output dimension 128), fuses them under semantic guidance, and optimizes a weighted loss combining ZINB reconstruction (lambda_zinb = 1.0), spatial neighborhood regularization (lambda_reg = 0.1), and cross-view decorrelation (lambda_dicr = 0.1) using the Adam optimizer. After convergence, the learned spot embeddings are extracted and partitioned with k-means into the requested number of spatial domains. Hyperparameters are read from a config file under `config/`.

## Output & Evaluation

Inspect and evaluate the identified spatial domains. Results are written to `data/results/<dataset_id>/` as an AnnData with predicted cluster labels in `obs['idx']` and a spatial cluster plot PNG. When ground-truth annotations are available, clustering quality can be quantified with ARI, NMI, ACC, and FMI. The learned embeddings can be visualized with UMAP to inspect domain separation, and marker genes or Gene Ontology enrichment can be used to biologically interpret the domains.
