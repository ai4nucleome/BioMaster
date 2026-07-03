# Bioclaw Hub Spatial Transcriptomics

## Overview

This workflow processes spatial transcriptomics data from raw or minimally processed inputs through to publication-ready spatial maps. It covers validation of spatial assets (coordinates, images, barcode alignment), expression preprocessing that preserves spatial structure, domain detection, deconvolution with optional single-cell references, neighborhood and communication analysis, and high-quality spatial visualization. Use this workflow when the dataset includes spatial coordinates, histology images, or spot-level expression data, and the goal is to identify spatial domains, estimate cell-type proportions, analyze tissue neighborhoods, or generate spatially aware visualizations. Expected inputs are spatial expression data with coordinates or histology images and an optional single-cell reference. Expected outputs include spatial domain labels, deconvolution tables, neighborhood interaction results, and spatial maps with legends and scale bars.

## Validate Spatial Assets

Confirm that coordinate systems, image registration, and barcode alignment are consistent and correct. Check that spatial coordinates match the expression matrix dimensions, that histology images (if present) are properly registered to spot positions, and that barcodes between expression data and spatial metadata align without mismatches.

## Preprocess Expression and Spatial Structure

Normalize expression counts while preserving spatial coordinates and neighborhood information. Filter low-quality spots, perform library-size normalization, log-transform, and identify highly variable genes. Build a spatial neighbor graph that incorporates physical distances between spots, enabling downstream spatial analyses.

## Domain Detection

Identify spatial domains — contiguous regions of coordinated gene expression — using clustering on the spatial neighbor graph. Apply graph-based clustering (e.g. Leiden) on the spatial adjacency structure to segment the tissue into transcriptionally distinct spatial domains. Optionally run spatial autocorrelation methods to identify genes that define each domain.

## Deconvolution

Estimate cell-type proportions per spot using an optional single-cell reference. Apply spatial deconvolution methods (e.g. cell2location, RCTD, or spatial regression) to decompose each spot's expression into cell-type contributions. When no single-cell reference is available, use unsupervised methods or marker-based scoring to approximate cell-type enrichment.

## Neighborhood and Communication Analysis

Analyze spatial proximity relationships between domains or cell types. Compute neighborhood enrichment to identify which domains/cell types co-occur more or less than expected by chance. Optionally run ligand-receptor interaction analysis to infer cell-cell communication constrained by spatial proximity.

## Visualize Spatial Biology

Generate publication-ready spatial maps that preserve physical context, legends, and scale bars. Plot spatial domains, cell-type scores, gene expression, and other metadata overlaid on tissue coordinates. Create multi-panel figures with consistent color schemes, readable legends, and scale indicators.

## Export Interpretable Artifacts

Save spatial labels, coordinates, deconvolution tables, and figure-ready outputs to organized directories. Export the annotated AnnData object with all metadata and embeddings for downstream reuse. Write domain assignments, cell-type proportions, and neighborhood results as CSV tables.
