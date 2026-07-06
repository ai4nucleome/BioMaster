# Bioskills Coexpression Networks

## Overview

This workflow builds weighted gene co-expression networks from RNA-seq expression data to discover modules of co-regulated genes, relate those modules to sample traits, and identify hub genes. The canonical implementation uses the R WGCNA package: it takes a normalized expression matrix (genes x samples) plus optional sample traits as input and produces module assignments, module eigengenes, module-trait correlations, hub gene rankings, and Cytoscape-ready network files as output. Use this skill when you have normalized bulk RNA-seq (a minimum of 15-20 samples is recommended, with 15 as the absolute floor for stable correlation) or, for single-cell data, aggregated metacells via hdWGCNA, and you want to move from a gene-by-sample matrix to interpretable co-expression modules and candidate hub genes. The workflow proceeds through input preparation, soft-thresholding power selection, network construction and module detection, module-trait relationship analysis, hub gene identification, and Cytoscape export. Alternative automated implementations (CEMiTool, PyWGCNA) and the single-cell hdWGCNA variant are covered in the final step. Reference versions tested: WGCNA 1.72+, CEMiTool 1.26+; if installed versions differ, verify parameters via packageVersion() and the function help before running.

## Input Preparation

Load the normalized expression matrix and reshape it to WGCNA's convention (samples as rows, genes as columns). Filter out low-variance genes that would add noise and slow computation, typically keeping the most variable genes (a common target is the top 5000-10000 most variable genes). Inspect a sample clustering dendrogram to flag outlier samples that should be removed before network construction. This step establishes the clean expression input required for all downstream network analysis.

## Soft-Thresholding Power Selection

Choose the soft-thresholding power that makes the network approximate a scale-free topology. Sweep candidate powers, then inspect the scale-independence and mean-connectivity plots. Select the lowest power achieving an R-squared of at least 0.85 (0.80-0.90 acceptable); if none reaches 0.85, use the power where R-squared plateaus. This power is used to raise the correlation matrix to a weighted adjacency in the next step.

## Network Construction and Module Detection

Build the weighted co-expression network and detect modules in one call using blockwiseModules. The function computes the adjacency and Topological Overlap Matrix (TOM), performs hierarchical clustering, and assigns genes to modules; modules whose eigengenes are highly correlated are merged at mergeCutHeight (0.25 merges modules with greater than 75% eigengene correlation). A minimum module size of 30 genes is recommended, as smaller modules are often noise. Inspect the resulting module sizes and the gene dendrogram with module colors to verify sensible clustering before proceeding.

## Module-Trait Relationships

Summarize each module by its eigengene (the first principal component of the module's expression) and correlate eigengenes with sample traits to find modules associated with phenotypes of interest. Visualize the correlations and their p-values as a labeled heatmap to prioritize modules for downstream hub-gene analysis.

## Hub Gene Identification

Within a module of interest, identify hub genes by combining three signals: module membership (correlation of each gene's expression with the module eigengene), gene significance (correlation with the trait of interest), and intramodular connectivity (kWithin). Select genes exceeding both the module-membership and gene-significance cutoffs, then rank them by kWithin to surface the most central candidates.

## Network Export for Cytoscape

Export a chosen module as an edge/node list for interactive visualization in Cytoscape. Recompute the TOM restricted to the module's genes, threshold weak connections to keep the graph tractable, and write Cytoscape-compatible edge and node files that can be imported directly for layout and styling.

## Alternative Implementations

For users who want automation or work in single-cell contexts, three alternatives replace parts of the manual WGCNA workflow. CEMiTool (R) automates soft-threshold selection, module detection, and ORA enrichment in a single call. hdWGCNA (R/Seurat) adapts WGCNA to single-cell data by building metacells (groups of 25-50 cells) to overcome sparsity before running the standard network pipeline and projecting modules onto a UMAP. PyWGCNA (Python) provides a Python API mirroring the WGCNA workflow. Choose based on data modality and language preference.
