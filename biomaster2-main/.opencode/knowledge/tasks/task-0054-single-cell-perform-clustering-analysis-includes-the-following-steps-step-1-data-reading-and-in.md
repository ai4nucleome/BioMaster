---
id: task-0054
title: 'Single-cell perform clustering analysis includes the following steps: Step
  1: Data Reading and In...'
summary: 'Single-cell perform clustering analysis includes the following steps: Step
  1: Data Reading and Initialization, reading .h5ad or 10x Genomics matrix.mtx files
  using scanpy.read_10x_mtx or scanpy.read_h5ad to generate a...'
keywords:
- scanpy
- Single-cell perform clustering analysis
- 'Single-cell perform clustering analysis includes the following steps: Step 1: Data
  Reading and In'
- 'Single-cell perform clustering analysis includes the following steps: Step 1: Data
  Reading and Initialization'
- reading .h5ad or 10x Genomics matrix.mtx files using scanpy.read_10x_mtx or scanpy.read_h5ad
  to generate an AnnData object containing the raw gene expression matrix (rows=genes
- columns=cells) and metadata
- 'Step 2: Quality Control (QC)'
- filtering low-quality cells based on mitochondrial gene percentage (≤20%)
- total UMIs (≥500)
- and detected genes using scanpy.pp.calculate_qc_metrics
- scanpy.pp.filter_cells
- outputting filtered high-quality data
- 'Step 3: Normalization and Highly Variable Gene Selection'
- standardizing QC-processed data via scanpy.pp.normalize_total
- scanpy.pp.log1p
- and scanpy.pp.highly_variable_genes to obtain a normalized expression matrix and
  a list of highly variable genes (HVGs)
- 'Step 4: Dimensionality Reduction and Visualization'
- performing PCA dimensionality reduction using scanpy.tl.pca
- constructing a KNN neighborhood graph with scanpy.pp.neighbors
- output an AnnData object with dimension-reduced results
- 'Step 5: Clustering Analysis'
- applying Leiden algorithm via scanpy.tl.leiden and UMAP
- t-SNE visualization with scanpy.tl.umap based on dimension-re
- Scanpy
path: .opencode/knowledge/tasks/task-0054-single-cell-perform-clustering-analysis-includes-the-following-steps-step-1-data-reading-and-in.md
origin_source: Single-cell perform clustering analysis
origin_page: 55
source_entry_index: 50
source_subindex: 1
source_file: doc/Task_Knowledge.json
status: active
canonical_exec_skill: exec-task
tool: scanpy
---

# Single-cell perform clustering analysis includes the following steps: Step 1: Data Reading and In...

## One-line description

Single-cell perform clustering analysis includes the following steps: Step 1: Data Reading and Initialization, reading .h5ad or 10x Genomics matrix.mtx files using scanpy.read_10x_mtx or scanpy.read_h5ad to generate a...

## Source

- Source file: `doc/Task_Knowledge.json`
- Origin source: `Single-cell perform clustering analysis`
- Origin page: `55`
- Source entry index: `50`
- Source subindex: `1`
- Canonical skill: `exec-task`

## Inputs

Extract user-provided data paths, sample metadata, reference files, tool parameters, and execution permissions from the user request. Do not reuse source example paths without user confirmation.

## Steps

Use the original source excerpt below as the authoritative source-specific procedure. Convert prose or script-specific instructions into explicit, ordered plan or execution steps before use.

## Tool mapping

- Canonical skill: `exec-task`
- Registry ID: `task-0054`
- Analysis/tool category: `scanpy`

## Expected outputs

Derive expected outputs from the selected source excerpt and normalize them into user-specific output directories.

## Validation hints

Validate required inputs, generated outputs, logs, and format-specific assumptions before handing results to the next agent.

## Suggested use

Use this numbered task record as source-specific BioMaster knowledge. Core OpenCode skills should select this record through the registry, then normalize paths, sample names, and output directories before generating a plan or command.

## Original source excerpt

```text
Single-cell perform clustering analysis includes the following steps: Step 1: Data Reading and Initialization, reading .h5ad or 10x Genomics matrix.mtx files using scanpy.read_10x_mtx or scanpy.read_h5ad to generate an AnnData object containing the raw gene expression matrix (rows=genes, columns=cells) and metadata; Step 2: Quality Control (QC), filtering low-quality cells based on mitochondrial gene percentage (≤20%), total UMIs (≥500), and detected genes using scanpy.pp.calculate_qc_metrics, scanpy.pp.filter_cells, outputting filtered high-quality data;Step 3: Normalization and Highly Variable Gene Selection, standardizing QC-processed data via scanpy.pp.normalize_total, scanpy.pp.log1p, and scanpy.pp.highly_variable_genes to obtain a normalized expression matrix and a list of highly variable genes (HVGs); Step 4: Dimensionality Reduction and Visualization, performing PCA dimensionality reduction using scanpy.tl.pca, constructing a KNN neighborhood graph with scanpy.pp.neighbors, output an AnnData object with dimension-reduced results; Step 5: Clustering Analysis, applying Leiden algorithm via scanpy.tl.leiden and UMAP/t-SNE visualization with scanpy.tl.umap based on dimension-reduced data, sc.tl.leiden(adata, resolution=), sc.pl.umap(adata, color='leiden', show=False, save='cluster_plots.png'), adata.write('./output/019/adata_clustered.h5ad'), outputting cell cluster labels and visualization plots (.png);
```

## Curation notes

- Keep this record as provenance-preserving knowledge.
- Do not copy example paths directly into user workflows.
- Combine this record with the canonical `task` skill before producing user-facing outputs.
