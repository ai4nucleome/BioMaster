---
id: wf-0045
title: The single-cell transcriptomics differential expression gene analysis workflow
  includes the follo...
summary: 'The single-cell transcriptomics differential expression gene analysis workflow
  includes the following steps: Step 1: Data Loading and Initialization, reading the
  raw single-cell data file (kang.h5ad) using omicverse.r...'
keywords:
- rnaseq-de
- workflow
- The single-cell transcriptomics differential expression gene analysis workflow includes
  the follo
- 'The single-cell transcriptomics differential expression gene analysis workflow
  includes the following steps: Step 1: Data Loading and Initialization'
- reading the raw single-cell data file (kang.h5ad) using omicverse.read to generate
  an AnnData object containing the raw gene expression matrix and metadata
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
- performing PCA (50 principal components) with scanpy.tl.pca and nonlinear MDE reduction
  using ov.utils.mde
- yielding an AnnData object with dimension-reduced results
- 'Step 5: Clustering Analysis'
- applying Leiden algorithm via scanpy.tl.leiden and UMAP
- t-SNE visualization with scanpy.tl.umap based on dimension-reduced data
- outputting cell cluster labels and visualization plo
- Scanpy
path: .opencode/knowledge/workflows/wf-0045-the-single-cell-transcriptomics-differential-expression-gene-analysis-workflow-includes-the-follo.md
origin_source: workflow
origin_page: 47
source_entry_index: 37
source_subindex: 1
source_file: doc/Plan_Knowledge.json
status: active
canonical_plan_skill: plan-workflow
analysis_type: rnaseq-de
---

# The single-cell transcriptomics differential expression gene analysis workflow includes the follo...

## One-line description

The single-cell transcriptomics differential expression gene analysis workflow includes the following steps: Step 1: Data Loading and Initialization, reading the raw single-cell data file (kang.h5ad) using omicverse.r...

## Source

- Source file: `doc/Plan_Knowledge.json`
- Origin source: `workflow`
- Origin page: `47`
- Source entry index: `37`
- Source subindex: `1`
- Canonical skill: `plan-workflow`

## Inputs

Extract user-provided data paths, sample metadata, reference files, tool parameters, and execution permissions from the user request. Do not reuse source example paths without user confirmation.

## Steps

Use the original source excerpt below as the authoritative source-specific procedure. Convert prose or script-specific instructions into explicit, ordered plan or execution steps before use.

## Tool mapping

- Canonical skill: `plan-workflow`
- Registry ID: `wf-0045`
- Analysis/tool category: `rnaseq-de`

## Expected outputs

Derive expected outputs from the selected source excerpt and normalize them into user-specific output directories.

## Validation hints

Validate required inputs, generated outputs, logs, and format-specific assumptions before handing results to the next agent.

## Suggested use

Use this numbered workflow record as source-specific BioMaster knowledge. Core OpenCode skills should select this record through the registry, then normalize paths, sample names, and output directories before generating a plan or command.

## Original source excerpt

```text
The single-cell transcriptomics differential expression gene analysis workflow includes the following steps: Step 1: Data Loading and Initialization, reading the raw single-cell data file (kang.h5ad) using omicverse.read to generate an AnnData object containing the raw gene expression matrix and metadata; Step 2: Quality Control (QC), filtering low-quality cells based on mitochondrial gene percentage (≤20%), total UMIs (≥500), and detected genes using omicverse.pp.qc, outputting filtered high-quality data; Step 3: Normalization and Highly Variable Gene Selection, standardizing QC-processed data via scanpy.pp.normalize_total, scanpy.pp.log1p, and scanpy.pp.highly_variable_genes to obtain a normalized expression matrix and a list of highly variable genes (HVGs); Step 4: Dimensionality Reduction and Visualization, performing PCA (50 principal components) with scanpy.tl.pca and nonlinear MDE reduction using ov.utils.mde, yielding an AnnData object with dimension-reduced results; Step 5: Clustering Analysis, applying Leiden algorithm via scanpy.tl.leiden and UMAP/t-SNE visualization with scanpy.tl.umap based on dimension-reduced data, outputting cell cluster labels and visualization plots; Step 6: Whole-Cell Differential Expression Analysis, applying tools like Seurat.FindMarkers, DESeq2, MAST, or edgeR to compare group differences at the whole-cell level, inputting normalized expression matrices and grouping information, outputting a list of differentially expressed genes (DEGs) with log2FC, p-values, and adjusted p-values.
```

## Curation notes

- Keep this record as provenance-preserving knowledge.
- Do not copy example paths directly into user workflows.
- Combine this record with the canonical `workflow` skill before producing user-facing outputs.
