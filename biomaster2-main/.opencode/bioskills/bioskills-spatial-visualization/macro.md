# Bioskills Spatial Visualization

## Overview

Visualize spatial transcriptomics data by overlaying gene expression, cluster assignments, continuous scores, and QC metrics onto tissue spatial coordinates, optionally on top of a registered histology image. Inputs: an AnnData object with spot coordinates in `adata.obsm['spatial']` and (optionally) tissue images plus scale factors in `adata.uns['spatial']`, along with any cluster labels (e.g. `leiden`) or spatial statistics already computed. Outputs: static matplotlib figures (PNG/PDF), interactive napari views, and composite multi-panel overviews. Use this workflow after loading spatial data and (optionally) running clustering or spatial-statistics steps, whenever you need to inspect biology in its tissue context — from a first QC overlay to publication-ready figures. Reference examples target matplotlib 3.8+, numpy 1.26+, scanpy 1.10+, squidpy 1.3+; if installed versions differ, introspect the actual API (`pip show <package>` then `help(module.function)`) and adapt rather than retrying on ImportError/AttributeError/TypeError.

## Setup & Basic Spatial Plot

Verify that installed package versions match the reference set (matplotlib 3.8+, numpy 1.26+, scanpy 1.10+, squidpy 1.3+) and import squidpy, scanpy, and matplotlib. Create a first spatial scatter plot that colors each spot by a metadata variable such as total_counts or a cluster label, using either squidpy's `spatial_scatter` or scanpy's `sc.pl.spatial`. Plot several variables side by side in a single call via a list and `ncols`.

## Tissue Image Overlay & Appearance

Overlay spots on the registered histology image using `img_key='hires'` and control image transparency with `alpha_img`; toggle the image off entirely with `img_key=None`. Customize the visual style — spot size, color palette, title, and frame — to produce clean, presentation-ready spatial plots.

## Gene Expression on Tissue

Visualize one or more genes overlaid on tissue coordinates with configurable colormaps and value ranges (`vmin`/`vmax`, including percentile caps like `'p99'`). Build custom multi-gene panels with manual colorbar control by drawing into explicit matplotlib axes. Render two-gene co-localization as a dual-channel RGB scatter by normalizing each gene to [0,1] and assigning it to the red and green channels.

## Multi-Sample Comparison & Annotation

Compare cluster or expression patterns across samples by subsetting the AnnData per sample and plotting each into a shared figure with consistent axes. Add text annotations labeling each cluster at its spatial centroid for readability. Crop or zoom into a tissue region by setting axis limits, remembering that the y-axis is inverted in image coordinates.

## Spatial Statistics Visualization

Render the outputs of spatial-statistics computations: map individual genes flagged by Moran's I onto the tissue, plot neighborhood-enrichment heatmaps between clusters with `sq.pl.nhood_enrichment`, and plot co-occurrence probability curves across spatial scales with `sq.pl.co_occurrence`.

## Interactive Exploration & Publication Figures

Explore data interactively in napari by loading the tissue image and scaled spot coordinates (using the hires scale factor) as separate layers. Export publication-quality static figures as both PDF and PNG with tight bounding boxes and frameless styling. Assemble composite multi-panel overviews combining spatial cluster/expression plots, QC overlays, UMAP, and violin plots into a single figure.
