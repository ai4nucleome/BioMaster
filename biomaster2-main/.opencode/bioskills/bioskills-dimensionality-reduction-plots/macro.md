# Bioskills Dimensionality Reduction Plots

## Overview

This workflow produces publication-quality 2D dimensionality-reduction plots (PCA, t-SNE, UMAP, PHATE) from a normalized expression matrix or single-cell object. Inputs: a feature-by-sample expression matrix (bulk RNA-seq) or an AnnData/Seurat object with normalized counts, plus optional metadata (condition, batch, cluster labels, pseudotime) for coloring. Outputs: 2D scatter plots with axes labeled (variance explained for PCA), a screeplot and loadings plot for PCA, and saved vector/raster figures at publication DPI. Use this skill when you need to visualize sample relationships, diagnose batch effects, display cluster assignments, or show continuous trajectories — and when you must communicate the limits of 2D embeddings. Foundational guidance: 2D embeddings of single-cell data lose >95% of high-dimensional geometry (Chari & Pachter 2023) — local neighborhoods are preserved by construction, but distances between distant cells, density estimates, and global topology are NOT. Choose the method by the question: PCA for variance/loadings and batch diagnostics, UMAP for cluster overviews, t-SNE (Kobak-Berens defaults) for crisp cluster boundaries, PHATE for continuous transitions. Always set a random seed, report all hyperparameters in the caption and methods, and validate trajectory claims against high-dimensional data (RNA velocity, diffusion pseudotime, PHATE) rather than inferring them from UMAP layout.

## Method Selection & Input Preparation

Decide which projection method fits the biological question: PCA for variance explained, loadings, and batch diagnostics; UMAP for broad cluster overviews; t-SNE (Kobak-Berens defaults) for crisp cluster boundaries; PHATE for continuous trajectories or branching. Prepare the input matrix so PCA captures biological variation rather than library-size effects — variance-stabilize bulk counts (DESeq2 vst/rlog) or log-normalize and scale single-cell data. Verify installed package versions (scanpy 1.10+, anndata 0.10+, umap-learn 0.5+, openTSNE 1.0+, phate 1.0+) and introspect the actual API before running if versions differ, rather than retrying on ImportError/AttributeError.

## PCA — Variance & Loadings

Run PCA on the transposed, scaled expression matrix. PCA is deterministic and uniquely interpretable via loadings — use it for bulk sample QC, batch-effect diagnostics (if PC1/PC2 separate batches, batch is the dominant variance), and identifying variance-driving genes. Always label axes with variance-explained percentages; a PCA plot without 'PC1 (45%)' is unreadable, and if PC1 is only ~5% apparent clusters may be noise. Pair the biplot with a screeplot (components 1-10) and a loadings plot to support interpretation. If PC1 perfectly correlates with library size, the data was not scaled or normalized correctly. Loadings are PCA-specific and must never be projected onto UMAP/t-SNE coordinates.

## t-SNE — Kobak-Berens Defaults

Run t-SNE with modern Kobak-Berens 2019 defaults that recover global structure lost by vanilla t-SNE: initialize with PCA (not random), use a high learning rate scaled as n/12, and apply early exaggeration. Perplexity is the local-vs-global trade-off — 30-50 is standard for >1000 points; for small datasets use max(5, n/30) since perplexity > n/3 fails and shatters the plot. Use t-SNE when crisp cluster separation matters more than global distances. Set a random seed for reproducibility. Note that Rtsne does not natively support PCA initialization; supply an external init via Y_init= if needed.

## UMAP — Modern Defaults

Run UMAP for broad cluster overviews — faster than t-SNE and with better global preservation than default t-SNE. n_neighbors (15-50) controls the local-vs-global balance: small values fragment locally, large values homogenize clusters. min_dist (0.1-0.5) controls cluster tightness in the rendering, NOT which cells cluster together. Always set random_state for reproducibility (UMAP is stochastic). In scanpy, run UMAP after sc.tl.pca and sc.pp.neighbors (n_neighbors 15-30, n_pcs 30-50). Be aware of the scanpy save trap: save= writes to sc.settings.figdir (default ./figures/) with a 'umap' prefix, producing figures/umap<suffix> rather than the path you specify.

## PHATE — Continuous Trajectories

Run PHATE when the biology is continuous — embryonic development, differentiation, or any transition state. PHATE preserves branching and transition geometry that UMAP collapses ('blobifies') into discrete clusters. For discrete cell types, UMAP remains preferable. Tune knn and decay; let t auto-select diffusion power. Color the embedding by pseudotime to reveal trajectory structure. Validate any trajectory claim against high-dimensional methods (RNA velocity, diffusion pseudotime) rather than reading it off the 2D layout alone.

## Plotting, Saving & Reproducibility

Finalize figures for publication and reproducibility. Set DPI to 300+ — the scanpy default dpi_save=150 is below Nature/Cell requirements and will be rejected at submission. Control save paths explicitly: either set sc.settings.figdir and use a descriptive save suffix (resulting in figdir/umap_<suffix>), or use matplotlib.savefig after sc.pl.umap(show=False) for full path control. Report all hyperparameters (perplexity, n_neighbors, min_dist, n_pcs, random_state) in the caption and methods. State the embedding's interpretation limit: local neighborhoods are preserved; distances between clusters, point densities, and cluster shapes are NOT meaningful (Chari-Pachter 2023). Do not interpret UMAP/t-SNE cluster shape as biology, and do not infer trajectories from inter-cluster gaps without high-dimensional validation.
