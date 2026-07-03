# Bioskills Cell Communication

## Overview

This workflow infers and quantifies cell-cell communication from scRNA-seq data using three complementary frameworks. CellChat (R) builds probabilistic ligand-receptor signaling networks between cell types and supports condition comparison. NicheNet (R) predicts which ligands from sender cells drive target gene expression in receiver cells. LIANA (Python) provides a consensus rank aggregation across multiple methods and scales to multi-sample designs via tensor decomposition.

**Inputs:** A labeled scRNA-seq object (Seurat in R, or AnnData in Python) with cell type annotations, optionally carrying condition and sample metadata. For NicheNet, precomputed ligand-target, ligand-receptor, and weighted-network RDS files are required.

**Outputs:** Inferred ligand-receptor interactions, pathway-level communication networks, signaling role assignments (dominant senders/receivers), prioritized ligands with their target genes, comparative plots across conditions, and (for LIANA) tensor factor loadings summarizing shared and sample-specific signaling programs.

**When to use:** After cell type annotation is complete and you want to model intercellular signaling, identify key signaling pathways and their cellular sources/targets, prioritize upstream ligands for a gene program of interest, or compare communication between experimental conditions or across samples.

**Version note:** Reference examples were tested with ggplot2 3.5+ and scanpy 1.10+. Before running, verify installed package versions match (Python: `pip show <package>` then inspect signatures; R: `packageVersion('<pkg>')` then `?function`). If code raises ImportError, AttributeError, or TypeError, introspect the installed package and adapt the call to the actual API rather than retrying.

## Setup & Database Loading

Prepare the input single-cell object and load the curated ligand-receptor reference databases required by each framework. For CellChat, attach a CellChatDB (human or mouse) and optionally subset it to a signaling category such as Secreted Signaling. For NicheNet, load the ligand-target matrix, ligand-receptor network, and weighted networks from precomputed RDS files. For LIANA, ensure the AnnData object carries cell type labels and that the consensus resource is available. This step establishes the data and reference resources that all downstream inference depends on.

## CellChat Communication Inference

Build the core CellChat communication model. Starting from the prepared CellChat object, subset the expression data, identify overexpressed genes and overexpressed interactions, compute communication probability using the trimean method, filter out low-confidence interactions (e.g. those supported by too few cells), infer pathway-level communication probabilities, and aggregate into a network of interaction counts and weights. This produces the probability matrix and aggregated network that all subsequent CellChat visualization and pathway analysis depend on.

## CellChat Visualization & Pathway Analysis

Turn the inferred communication networks into interpretable biological insights. Generate circle network plots of interaction counts and weights, heatmaps of intercellular interactions, pathway-specific aggregate and chord diagrams, and bubble plots of ligand-receptor pairs. Then compute centrality scores to assign signaling roles to each cell group, identify dominant sender and receiver populations via scatter plots and role heatmaps, and rank pathways by their overall contribution. This step characterizes both the topology of communication and the functional roles of each cell type.

## CellChat Condition Comparison

Compare communication networks across experimental conditions (e.g. control versus treatment). Build and fully process a separate CellChat object for each condition using the same inference pipeline as the single-condition workflow, merge them into one comparative object with named labels, then visualize differential interactions and compare pathway contributions between conditions. This reveals condition-specific signaling gains, losses, and shifts.

## NicheNet Ligand Activity Analysis

Predict which ligands expressed by sender cell types drive the gene expression program observed in receiver cells, and visualize the prioritized ligand-target and ligand-receptor links. Define sender and receiver cell types, extract expressed genes from each, build a gene set of interest from differential expression in the receiver (e.g. activated vs naive T cells), define background genes, intersect expressed ligands and receptors with the ligand-receptor network to obtain potential ligands, and compute ligand activities via Pearson correlation between predicted and observed target effects. Then build ligand-target and ligand-receptor heatmaps and a dot plot of ligand expression across cell types. NicheNet complements CellChat by linking upstream ligands to downstream target genes.

## LIANA Analysis & Tensor Decomposition

Run a method-agnostic consensus ranking of cell-cell communication on an AnnData object, filter significant interactions, and visualize them as dot plots. For multi-sample or multi-condition datasets, build a communication tensor from the inferred ligand-receptor scores and decompose it into a small number of factors that capture shared and sample-specific signaling programs, then visualize the factor loadings. LIANA provides cross-validation of interactions across methods and scales to complex experimental designs that single-sample tools cannot handle directly.
