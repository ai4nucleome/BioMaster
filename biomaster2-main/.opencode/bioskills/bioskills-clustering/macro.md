# Bioskills Clustering

## Overview

Single-cell clustering workflow that takes a preprocessed (normalized, variable-feature-selected) single-cell object and produces cell clusters together with 2D embeddings for visualization.

Inputs: a preprocessed AnnData object (Scanpy, Python) or Seurat object (R) with normalized counts and a set of highly variable features already selected. Raw or unprocessed data must be run through a preprocessing skill first.

Outputs: the same object augmented with a PCA representation, a k-nearest-neighbor graph, cluster labels (Leiden or Louvain) stored in metadata, and 2D embeddings (UMAP and/or tSNE). Optional PAGA graph abstraction captures cluster-level topology.

When to use: after preprocessing, when the goal is to discover cell populations/groups, visualize them in 2D, and prepare the object for downstream marker-gene identification and cell-type annotation. The workflow is implemented in parallel for Scanpy (Python) and Seurat (R); pick the implementation matching your environment. Key tunables are the number of PCs retained, the neighbor count, and the clustering resolution, which together control cluster granularity.

## Dimensionality Reduction (PCA)

Run Principal Component Analysis on the highly variable features to compress the high-dimensional expression matrix into a small set of principal components. Inspect the variance explained by each PC (elbow plot, and optionally JackStraw in Seurat) to choose how many PCs to retain for downstream graph construction. Typical retention is 10-50 PCs depending on dataset complexity. This step produces the PCA embedding that all subsequent steps operate on.

## Neighbor Graph Construction

Build a k-nearest-neighbor (k-NN) graph on the PCA representation. Each cell is connected to its nearest neighbors in PC space, forming the graph that community-detection algorithms partition. The number of neighbors controls smoothness (higher = smoother graph) versus locality (lower = more local structure), and the number of PCs used should match the choice from the previous step.

## Clustering

Partition the neighbor graph into communities of cells using Leiden (recommended) or Louvain. The resolution parameter controls granularity: higher values yield more, smaller clusters and lower values yield fewer, larger clusters. Sweep several resolutions and compare cluster counts (and cluster hierarchy with clustree in Seurat) to select an appropriate granularity for the biological question. Cluster labels are written to object metadata.

## Embedding & Visualization

Compute a 2D embedding of the cells for visualization. UMAP is preferred for speed and preservation of global structure; tSNE is a slower alternative that emphasizes local structure. Plot the embedding colored by cluster identity and by marker gene expression to sanity-check cluster separation. Embedding coordinates can be exported to metadata for custom plotting.

## Graph Abstraction (PAGA)

Optional step that abstracts the single-cell graph to a cluster-level topology using PAGA (Scanpy). PAGA estimates the connectivity strength between clusters, which is useful for trajectory-like interpretation and for initializing UMAP from the abstracted graph so that the 2D embedding respects cluster-level relationships. This is most informative when clusters represent a developmental or transitional continuum.
