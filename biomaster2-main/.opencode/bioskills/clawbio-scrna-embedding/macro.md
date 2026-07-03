# Clawbio Scrna Embedding

## Overview

This workflow produces a model-based latent embedding for single-cell RNA-seq data using scVI or scANVI, with optional batch-aware integration. It is the advanced entry point when a user explicitly asks for scVI-style latent integration, batch correction, or an `X_scvi` representation, rather than a generic Scanpy PCA clustering workflow.

**Inputs**: raw-count `.h5ad` (counts in `X` or a designated counts `layer`) or a 10x Matrix Market directory (`matrix.mtx` plus matching `barcodes.tsv` and `features.tsv`/`genes.tsv`). Processed or normalized matrices are rejected to avoid invalid biological inferences. A `--demo` mode loads a bundled example dataset.

**Outputs**: an `integrated.h5ad` containing `obsm["X_scvi"]`, log-normalized `X`, and raw counts in `layers["counts"]`; a UMAP figure on the latent space; a per-cell latent coordinate table; optional batch-mixing diagnostics when a batch key is supplied; and a reproducibility bundle (`commands.sh`, `environment.yml`, checksums). A `report.md` / `result.json` pair records the run and recommends the downstream `scrna-orchestrator --use-rep X_scvi` command.

**When to use**: when the request is specifically model-based latent embedding or batch integration with scvi-tools. Generic single-cell clustering or marker-gene requests should still go to `scrna-orchestrator`. The workflow is local-first (no remote model fetches, no patient data upload) and preserves reproducibility outputs.

## Input Validation & Loading

Validate and load the raw-count input. Accept a raw-count `.h5ad` (counts in `X` or a designated counts layer) or a 10x Matrix Market directory with matching barcodes and features files. Reject processed-like matrices (non-integer or implausibly large values) to avoid invalid biological inferences. Preserve the raw counts in `layers['counts']` for downstream scVI training. A `--demo` mode loads a bundled example dataset. The CLI accepts `--input <path> --output <report_dir>`, a 10x directory, or `--demo`; the ClawBio runner exposes the same via `python clawbio.py run scrna-embedding`.

## QC & Feature Selection

Apply basic quality-control thresholds and select features for the latent model. Compute per-cell metrics (`n_genes_by_counts`, `total_counts`, `pct_counts_mt`), filter cells by a minimum gene count, genes by a minimum cell count, and remove cells exceeding the mitochondrial fraction threshold. On a normalized log1p branch, select highly variable genes (Seurat flavor) to define the gene set used for scVI training. Default thresholds: `min_genes`, `min_cells`, `max_mt_pct`.

## Latent Model Training

Train the variational latent model on the raw-count HVG subset. Register the optional batch covariate via `setup_anndata`, then fit `scvi.model.SCVI`. When `--method scanvi` is requested together with a labels key and an unlabeled category, refine the model with `scvi.model.SCANVI` using the explicit labels. Export the resulting latent representation to `obsm['X_scvi']`.

## Latent Projection & UMAP

Build the downstream neighborhood graph and visualization in the learned latent space. Run neighbors with `use_rep='X_scvi'`, compute a UMAP embedding, and export per-cell latent coordinates to a CSV table. Generate a UMAP figure colored by the batch key when one is provided.

## Diagnostics, Export & Reporting

Compute lightweight batch-mixing diagnostics from the neighbor graph and batch labels (cross-batch neighbor fraction, neighbor entropy, batch silhouette) when a batch key is set. Save the integrated AnnData with `obsm['X_scvi']`, log-normalized `X`, and raw counts in `layers['counts']`. Emit the `report.md` / `result.json` contract, the reproducibility bundle (`commands.sh`, `environment.yml`, checksums), and the recommended downstream `scrna-orchestrator --use-rep X_scvi` command.
