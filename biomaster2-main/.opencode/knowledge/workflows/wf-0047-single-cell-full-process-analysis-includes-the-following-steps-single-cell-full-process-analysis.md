---
id: wf-0047
title: Single-cell full-process analysis includes the following steps:Single cell
  full-process analysis...
summary: 'Single-cell full-process analysis includes the following steps:Single cell
  full-process analysis includes the following steps: Step 1: Data Reading and Initialization,
  reading .h5ad or 10x Genomics matrix.mtx files us...'
keywords:
- rnaseq-de
- workflow
- Single-cell full-process analysis includes the following steps:Single cell full-process
  analysis
- 'Single-cell full-process analysis includes the following steps:Single cell full-process
  analysis includes the following steps: Step 1: Data Reading and Initialization'
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
- t-SNE visualization with scanpy.tl.umap ba
- Scanpy
path: .opencode/knowledge/workflows/wf-0047-single-cell-full-process-analysis-includes-the-following-steps-single-cell-full-process-analysis.md
origin_source: workflow
origin_page: 49
source_entry_index: 39
source_subindex: 1
source_file: doc/Plan_Knowledge.json
status: active
canonical_plan_skill: plan-workflow
analysis_type: rnaseq-de
---

# Single-cell full-process analysis includes the following steps:Single cell full-process analysis...

## One-line description

Single-cell full-process analysis includes the following steps:Single cell full-process analysis includes the following steps: Step 1: Data Reading and Initialization, reading .h5ad or 10x Genomics matrix.mtx files us...

## Source

- Source file: `doc/Plan_Knowledge.json`
- Origin source: `workflow`
- Origin page: `49`
- Source entry index: `39`
- Source subindex: `1`
- Canonical skill: `plan-workflow`

## Inputs

Extract user-provided data paths, sample metadata, reference files, tool parameters, and execution permissions from the user request. Do not reuse source example paths without user confirmation.

## Steps

Use the original source excerpt below as the authoritative source-specific procedure. Convert prose or script-specific instructions into explicit, ordered plan or execution steps before use.

## Tool mapping

- Canonical skill: `plan-workflow`
- Registry ID: `wf-0047`
- Analysis/tool category: `rnaseq-de`

## Expected outputs

Derive expected outputs from the selected source excerpt and normalize them into user-specific output directories.

## Validation hints

Validate required inputs, generated outputs, logs, and format-specific assumptions before handing results to the next agent.

## Suggested use

Use this numbered workflow record as source-specific BioMaster knowledge. Core OpenCode skills should select this record through the registry, then normalize paths, sample names, and output directories before generating a plan or command.

## Original source excerpt

```text
Single-cell full-process analysis includes the following steps:Single cell full-process analysis includes the following steps: Step 1: Data Reading and Initialization, reading .h5ad or 10x Genomics matrix.mtx files using scanpy.read_10x_mtx or scanpy.read_h5ad to generate an AnnData object containing the raw gene expression matrix (rows=genes, columns=cells) and metadata; Step 2: Quality Control (QC), filtering low-quality cells based on mitochondrial gene percentage (≤20%), total UMIs (≥500), and detected genes using omicverse.pp.qc, outputting filtered high-quality data;Step 3: Normalization and Highly Variable Gene Selection, standardizing QC-processed data via scanpy.pp.normalize_total, scanpy.pp.log1p, and scanpy.pp.highly_variable_genes to obtain a normalized expression matrix and a list of highly variable genes (HVGs); Step 4: Dimensionality Reduction and Visualization, performing PCA dimensionality reduction using scanpy.tl.pca, constructing a KNN neighborhood graph with scanpy.pp.neighbor, yielding an AnnData object with dimension-reduced results; Step 5: Clustering Analysis, applying Leiden algorithm via scanpy.tl.leiden and UMAP/t-SNE visualization with scanpy.tl.umap based on dimension-reduced data, outputting cell cluster labels and visualization plots; Step 6: Whole-Cell Differential Expression Analysis, applying tools to compare group differences at the whole-cell level, inputting normalized expression matrices and grouping information, outputting a table of differentially expressed genes (DEGs) with with colums of log2FC, p-values, and adjusted p-values, and respectively rename the columns to logFC, pvals, and adj_pvals; Step 7: Result Filtering, filtering marker genes based on significance thresholds adj_pvals, logFC, output all high-confidence marker gene lists with adj_pvals < 0.05 and logFC > 1, or output top n marker genes; Step 8 Cell Type Annotation Analysis:Inputs include a high-confidence marker gene list (.csv with logFC and adj_pval fields) and a raw AnnData object (containing a normalized expression matrix and cluster labels). using python tools like scanoy, celltypistand and pandas to do further annotation this step outputs biologically annotated cell subpopulation labels (e.g., adata.obs['cell_type']) and output verification umap plots using plot(.png files);  Step 9 Pseudotime trajectory analysis, input the Annotated AnnData (with cell_type column) and subpopulation labels (e.g., leiden_clusters), then use scanpy tool to deal with it. sc.tl.diffmap(adata), sc.pl.diffmap(adata, color='leiden_clusters'), Output: UMAP plot overlaid with Diffusion Map trajectory(.png); Step 10 Purity Analysis (Subpopulation Homogeneity Evaluation), This module evaluates subpopulation homogeneity using an annotated AnnData object (containing cell types and Leiden cluster labels). Inputs include the preprocessed expression matrix and cluster annotations. Tools involve the Gini coefficient to measure gene expression dispersion (genes with Gini >0.7 indicate high heterogeneity) and Wilcoxon tests to quantify high-dispersion gene proportions per cluster. Outputs are a cluster purity table (e.g., cluster_purity.csv); Step 11 Functional Heterogeneity Analysis, Inputs include the filtered AnnData object and predefined gene sets . Tools include Wilcoxon tests to select cluster-specific markers and diffusion pseudotime analysis to infer differentiation trajectories. Outputs are a marker gene list (cluster_markers.csv); Step 12 Regulatory Network Analysis, Inputs include the annotated AnnData object and TF-target databases. Tools use Decoupler for TF activity scoring and correlation analysis (|r|>0.3) to build networks. Outputs are a TF activity matrix (tf_activity.csv)
```

## Curation notes

- Keep this record as provenance-preserving knowledge.
- Do not copy example paths directly into user workflows.
- Combine this record with the canonical `workflow` skill before producing user-facing outputs.
