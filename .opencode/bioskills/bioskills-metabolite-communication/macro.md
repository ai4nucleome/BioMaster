# Bioskills Metabolite Communication

## Overview

Infer metabolite-mediated cell-cell communication from single-cell RNA-seq data using MeboCost. MeboCost predicts which cell types secrete specific metabolites from enzyme expression, identifies metabolite-sensing receptors on receiver cells, and computes permutation-based communication scores between cell populations. Use this workflow when you have an annotated scRNA-seq AnnData and want to model metabolic crosstalk (e.g. amino acid, lipid, nucleotide, vitamin signaling) rather than classical protein ligand-receptor interactions.

Inputs: an AnnData object with log-normalized expression, gene symbols (not Ensembl IDs), and a cell type annotation column; optionally a condition column for differential analysis. Species must be 'human' or 'mouse'.

Outputs: a MeboCost object whose `commu_res` table holds scored sender-enzyme-metabolite-receptor-receiver interactions with p-values, plus summary tables and network/flow visualizations. The communication flow follows: Sender cell -> Enzyme -> Metabolite -> Receptor -> Receiver cell.

Typical stages: prepare and validate the AnnData, run permutation-based communication inference, extract and filter significant interactions (optionally by metabolite category), visualize the communication network and per-metabolite flow, and optionally compare communication across experimental conditions.

Version note: examples were tested with matplotlib 3.8+ and scanpy 1.10+. If code raises ImportError/AttributeError/TypeError, introspect the installed package (`pip show <package>` then `help(module.function)`) and adapt to the actual API rather than retrying.

## Prepare Data

Prepare and validate an AnnData object for MeboCost analysis. Confirm the expression matrix is log-normalized, ensure gene symbols (not Ensembl IDs) are used as the gene index, and filter out rare cell types with fewer than a minimum number of cells so that communication inference is statistically robust. Inputs: an annotated AnnData with a cell type column. Outputs: a filtered, log-normalized AnnData ready to be passed to MeboCost.

## Run Communication Analysis

Initialize a MeboCost object from the prepared AnnData and run permutation-based inference of metabolite secretion-sensing interactions. MeboCost predicts metabolite secretion from enzyme expression, identifies metabolite-sensing receptors, and computes communication scores between cell types with significance testing via permutations. More permutations give more accurate p-values but are slower; 1000 is standard, 100 is useful for quick exploration. Inputs: prepared AnnData, cell type column, species. Outputs: a MeboCost object with `commu_res` containing scored interactions and p-values.

## Analyze and Filter Results

Extract and summarize significant metabolite-mediated communications from the MeboCost results. Filter interactions by a p-value threshold, compute summary statistics (total and significant interactions, unique metabolites, unique sender and receiver cell types), and rank top metabolites and sender-receiver pairs. Optionally restrict results to a curated metabolite category (amino acids, lipids, nucleotides, vitamins, or other) using MeboCost's curated metabolite-receptor pair annotations. The communication flow follows: Sender cell -> Enzyme -> Metabolite -> Receptor -> Receiver cell.

## Visualization

Visualize the inferred metabolite communication. Generate a heatmap of interaction counts aggregated by sender-receiver cell type pairs to overview the global communication network, and inspect the per-metabolite communication flow, which prints each sender-enzyme-metabolite-receptor-receiver link with its communication score and p-value. These plots help identify dominant communicating cell type pairs and trace individual metabolite signaling axes.

## Compare Conditions

Compare metabolite-mediated communication across experimental conditions such as tumor vs normal, treatment vs control, or disease vs healthy. Run MeboCost inference separately on each condition subset using the same permutation settings and collect the per-condition communication result tables, so that differential interactions (significant in one condition but not another) can be identified downstream.
