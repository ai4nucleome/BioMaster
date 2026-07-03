---
id: wf-0046
title: 'The single-cell data marker gene identification workflow includes the following
  steps: Step 1: Da...'
summary: 'The single-cell data marker gene identification workflow includes the following
  steps: Step 1: Data Reading and Initialization, reading .h5ad or 10x Genomics matrix.mtx
  files using scanpy.read_10x_mtx or scanpy.read_h...'
keywords:
- rnaseq-de
- workflow
- 'The single-cell data marker gene identification workflow includes the following
  steps: Step 1: Da'
- 'The single-cell data marker gene identification workflow includes the following
  steps: Step 1: Data Reading and Initialization'
- reading .h5ad or 10x Genomics matrix.mtx files using scanpy.read_10x_mtx or scanpy.read_h5ad
  to generate an AnnData object containing the raw gene expression matrix (rows=genes
- columns=cells) and metadata
- 'Step 2: Quality Control (QC)'
- filtering low-quality cells based on mitochondrial gene percentage (≤20%)
- total UMIs (≥500)
- and detected genes using omicverse.pp.qc
- outputting filtered high-quality data
- 'Step 3: Normalization and Highly Variable Gene Selection'
- standardizing QC-processed data via scanpy.pp.normalize_total
- scanpy.pp.log1p
- and scanpy.pp.highly_variable_genes to obtain a normalized expression matrix and
  a list of highly variable genes (HVGs)
- 'Step 4: Dimensionality Reduction and Visualization'
- performing PCA dimensionality reduction using scanpy.tl.pca
- constructing a KNN neighborhood graph with scanpy.pp.neighbor
- yielding an AnnData object with dimension-reduced results
- 'Step 5: Clustering Analysis'
- applying Leiden algorithm via scanpy.tl.leiden and UMAP
- t-SNE visualization with scanpy.tl.umap based on dimension-reduced data
- outputtin
- Scanpy
path: .opencode/knowledge/workflows/wf-0046-the-single-cell-data-marker-gene-identification-workflow-includes-the-following-steps-step-1-da.md
origin_source: workflow
origin_page: 48
source_entry_index: 38
source_subindex: 1
source_file: doc/Plan_Knowledge.json
status: active
canonical_plan_skill: plan-workflow
analysis_type: rnaseq-de
---

# The single-cell data marker gene identification workflow includes the following steps: Step 1: Da...

## One-line description

The single-cell data marker gene identification workflow includes the following steps: Step 1: Data Reading and Initialization, reading .h5ad or 10x Genomics matrix.mtx files using scanpy.read_10x_mtx or scanpy.read_h...

## Source

- Source file: `doc/Plan_Knowledge.json`
- Origin source: `workflow`
- Origin page: `48`
- Source entry index: `38`
- Source subindex: `1`
- Canonical skill: `plan-workflow`

## Inputs

Extract user-provided data paths, sample metadata, reference files, tool parameters, and execution permissions from the user request. Do not reuse source example paths without user confirmation.

## Steps

Use the original source excerpt below as the authoritative source-specific procedure. Convert prose or script-specific instructions into explicit, ordered plan or execution steps before use.

## Tool mapping

- Canonical skill: `plan-workflow`
- Registry ID: `wf-0046`
- Analysis/tool category: `rnaseq-de`

## Expected outputs

Derive expected outputs from the selected source excerpt and normalize them into user-specific output directories.

## Validation hints

Validate required inputs, generated outputs, logs, and format-specific assumptions before handing results to the next agent.

## Suggested use

Use this numbered workflow record as source-specific BioMaster knowledge. Core OpenCode skills should select this record through the registry, then normalize paths, sample names, and output directories before generating a plan or command.

## Original source excerpt

```text
The single-cell data marker gene identification workflow includes the following steps: Step 1: Data Reading and Initialization, reading .h5ad or 10x Genomics matrix.mtx files using scanpy.read_10x_mtx or scanpy.read_h5ad to generate an AnnData object containing the raw gene expression matrix (rows=genes, columns=cells) and metadata; Step 2: Quality Control (QC), filtering low-quality cells based on mitochondrial gene percentage (≤20%), total UMIs (≥500), and detected genes using omicverse.pp.qc, outputting filtered high-quality data;Step 3: Normalization and Highly Variable Gene Selection, standardizing QC-processed data via scanpy.pp.normalize_total, scanpy.pp.log1p, and scanpy.pp.highly_variable_genes to obtain a normalized expression matrix and a list of highly variable genes (HVGs); Step 4: Dimensionality Reduction and Visualization, performing PCA dimensionality reduction using scanpy.tl.pca, constructing a KNN neighborhood graph with scanpy.pp.neighbor, yielding an AnnData object with dimension-reduced results; Step 5: Clustering Analysis, applying Leiden algorithm via scanpy.tl.leiden and UMAP/t-SNE visualization with scanpy.tl.umap based on dimension-reduced data, outputting cell cluster labels and visualization plots; Step 6: Whole-Cell Differential Expression Analysis, applying tools to compare group differences at the whole-cell level, inputting normalized expression matrices and grouping information, outputting a table of differentially expressed genes (DEGs) with with colums of log2FC, p-values, and adjusted p-values, and respectively rename the columns to logFC, pvals, and adj_pvals; Step 7: Result Filtering, filtering marker genes based on significance thresholds adj_pvals, logFC, output all high-confidence marker gene lists with adj_pvals < 0.05 and logFC > 1
```

## Curation notes

- Keep this record as provenance-preserving knowledge.
- Do not copy example paths directly into user workflows.
- Combine this record with the canonical `workflow` skill before producing user-facing outputs.
