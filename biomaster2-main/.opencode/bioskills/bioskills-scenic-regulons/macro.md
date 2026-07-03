# Bioskills Scenic Regulons

## Overview

The pySCENIC regulon pipeline infers transcription factor (TF) regulons from single-cell RNA-seq data through a three-stage strategy: co-expression-based GRN inference (GRNBoost2), cis-regulatory motif pruning (cisTarget), and per-cell regulon activity scoring (AUCell), followed by interpretation of cell-type-specific regulon activity.

**Inputs:** a filtered scRNA-seq expression matrix (typically a loom file), a species-specific TF list, cisTarget ranking databases (feather format), and motif-to-TF annotations.

**Outputs:** a list of pruned regulons (TF → target gene sets, saved as pickle), a cell-by-regulon AUC activity matrix (CSV/loom), and optional cell-type-specific summaries (Regulon Specificity Scores, binarized on/off activity, UMAP/heatmap projections).

**When to use:** when you want to identify master TFs driving cell states or identities, build gene regulatory networks from scRNA-seq, or compare regulon activity across cell types or conditions. Best run after standard scRNA-seq QC and clustering so cell-type labels are available for downstream interpretation.

**Pipeline at a glance:** (1) GRN inference with GRNBoost2 produces a TF-target adjacency table; (2) cisTarget prunes that table to motif-supported links, yielding regulons; (3) AUCell scores each regulon's activity per cell. Native Arboreto is broken with dask >= 2.0, so the bundled `arboreto_with_multiprocessing.py` script is the recommended GRN backend. pySCENIC is tested on Python 3.10 and should be installed in a dedicated conda environment.

## Environment Setup and Data Preparation

Prepare the runtime and inputs for the pySCENIC pipeline. Create a dedicated Python 3.10 conda environment with pySCENIC and loompy to avoid dependency conflicts. Download the cisTarget ranking databases (feather format) and the motif-to-TF annotation table for the relevant genome (e.g. hg38 human) from the cisTarget resources page. Prepare the input expression matrix in loom format and a species-appropriate TF list. Prefilter lowly expressed genes (e.g. genes in fewer than 3 cells or less than 1% of cells) and consider subsampling to 5000–10000 cells for the GRN step, since inferred regulons transfer well to the full dataset. Loom is the standard input format; convert from h5ad with loompy if needed.

## GRN Inference with GRNBoost2

Infer co-expression modules between TFs and putative target genes using GRNBoost2 via Arboreto. Because native Arboreto is broken with dask >= 2.0, the recommended approach is the bundled `arboreto_with_multiprocessing.py` script, which avoids dask compatibility issues entirely. The equivalent CLI is `pyscenic grn`. The output is an adjacency table (adj.tsv) of TF-target pairs with importance weights. This is the most computationally expensive step; parallelize with `--num_workers` and consider subsampling cells as noted in setup.

## Regulon Pruning with cisTarget

Filter the raw co-expression modules to retain only TF-target links supported by cis-regulatory motif enrichment near target gene promoters. Load the cisTarget ranking databases (feather) and motif annotations, run `prune2df` to test each TF's targets for upstream motif enrichment, then convert the pruned results into regulon objects with `df2regulons`. Save the resulting regulons (TF → target gene sets) to a pickle file for reuse. The equivalent CLI is `pyscenic ctx`, which takes the adjacency table, ranking database(s), motif annotations, and the expression matrix as inputs.

## AUCell Activity Scoring

Score the activity of each regulon in every individual cell to produce a cell-by-regulon activity matrix. AUCell ranks genes by expression within each cell and computes the area under the recovery curve for each regulon's gene set, yielding an AUC score that reflects regulon activity independent of expression magnitude. The `auc_threshold` parameter (default 0.05, i.e. the top 5% of ranked genes) controls sensitivity. The equivalent CLI is `pyscenic aucell`, which writes a loom file of AUC scores.

## Interpretation and Visualization

Interpret and visualize regulon activity to identify master TFs driving cell identities. Compute Regulon Specificity Scores (RSS) to find regulons enriched in specific cell types (requires cell-type labels), binarize AUC scores into on/off calls per cell using bimodal distribution fitting, and project regulon activity onto UMAP embeddings or heatmaps grouped by cell type. These summaries highlight the TFs that define each cell state and support downstream biological interpretation.
