# Bioskills Spatial Deconvolution

## Overview

This workflow estimates cell-type composition within spatial transcriptomics spots (e.g. Visium) by leveraging an annotated scRNA-seq reference. It is essential for technologies where each spot captures multiple cells, since deconvolution recovers per-cell-type abundances that single-gene spatial plots cannot reveal.

Inputs: an annotated scRNA-seq reference AnnData (with a `cell_type` observation column) and a spatial AnnData (with raw counts and spatial coordinates in `obsm['spatial']`). Both must share a common set of gene features.

Outputs: per-spot cell-type abundance and proportion matrices added to the spatial AnnData's `obsm`, a dominant cell type per spot, spatial visualizations (heatmaps and optional per-spot pie charts), and exported CSV / h5ad files.

The primary path uses cell2location: first train a regression model on the scRNA-seq reference to learn cell-type signatures, then decompose each spatial spot into cell-type abundances with a Cell2location spatial model. Tangram (optimal-transport alignment of single cells to spots) and RCTD (run in R via spacexr) are provided as alternative deconvolution strategies. After deconvolution, results are extracted, validated against marker-gene expression, visualized across the tissue, and exported.

Use this skill when you need to translate spatial expression measurements into cell-type-level spatial maps. Reference examples were tested with anndata 0.10+, matplotlib 3.8+, numpy 1.26+, pandas 2.2+, and scanpy 1.10+; verify installed versions and adapt API calls if ImportErrors or TypeErrors arise.

## Data Loading & Gene Alignment

Load the annotated scRNA-seq reference and the spatial AnnData, then restrict both objects to the intersection of shared gene names so that downstream deconvolution models operate on a common feature space. The reference's cell_type column is cast to a categorical, which is required by the signature model. This step is the prerequisite for any deconvolution method and ensures reference and spatial data are comparable before model training.

## Reference Signature Training (cell2location)

Learn cell-type gene expression signatures from the annotated single-cell reference using cell2location's RegressionModel. Low-quality genes are filtered with cell2location's filter_genes helper, the reference AnnData is configured with the cell_type labels key, the regression model is trained, and per-cluster mean expression signatures are exported into the reference's varm under 'means_per_cluster_mu_fg'. These signatures are the input to the spatial deconvolution model.

## Spatial Deconvolution (cell2location)

Decompose each spatial spot into cell-type abundances using the trained reference signatures. The spatial AnnData is first aligned to the reference gene set, then a Cell2location spatial model is configured with the reference signature matrix, an expected number of cells per location (N_cells_per_location), and a detection alpha hyperparameter. After training on the spatial data, posterior abundance estimates are exported into the spatial AnnData.

## Alternative Deconvolution Methods

Use Tangram or RCTD as alternative deconvolution strategies when cell2location is unsuitable or for cross-method comparison. Tangram aligns single cells to spatial spots via optimal transport using a set of marker genes derived from the reference with rank_genes_groups; it returns a mapping AnnData and projected cell-type annotations in the spatial object's obsm. RCTD runs in R through the spacexr package (invoked via rpy2) and decomposes spots with a different statistical model; data are written to h5ad for R-side loading and results are read back as cell-type weights.

## Result Extraction & Quality Evaluation

Extract cell-type abundances from the model posterior, convert them to per-spot proportions, and assign a dominant cell type to each spot. Validate the deconvolution by correlating each cell type's estimated proportion with the mean expression of its canonical marker genes in the spatial data; high positive correlations indicate reliable estimates. When multiple methods have been run, store their proportion matrices in obsm and compare agreement via per-cell-type correlations.

## Visualization & Export

Visualize estimated cell-type proportions as spatial heatmaps across the tissue, with one panel per cell type using scanpy's spatial plotting. For a compact per-spot view, an optional pie-chart overlay draws wedges sized by each cell type's proportion at every spot coordinate. Finally, export the proportion matrix as a CSV table and save the annotated spatial AnnData as an h5ad file for downstream use.
