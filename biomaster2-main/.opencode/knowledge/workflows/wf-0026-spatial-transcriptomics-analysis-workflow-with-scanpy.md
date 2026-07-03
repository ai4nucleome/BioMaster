---
id: wf-0026
title: Spatial Transcriptomics Analysis Workflow with Scanpy
summary: 'Spatial Transcriptomics Analysis Workflow with Scanpy **Step 1: Data Reading
  and Initial Setup** - **Description**: Import necessary libraries and read spatial
  transcriptomics data into an AnnData object. - **Input Re...'
keywords:
- scrnaseq-cluster
- workflow
- Spatial Transcriptomics Analysis Workflow with Scanpy
- '**Step 1: Data Reading and Initial Setup**

  - **Description**: Import necessary libraries and read spatial transcriptomics data
  into an AnnData object.

  - **Input Required**: Spatial transcriptomics dataset (e.g'
- '10x Genomics Visium data)

  - **Expected Output**: AnnData object containing gene expression matrix and spatial
  coordinates

  - **Tools Used**: Scanpy'
- pandas
- matplotlib
- '**Step 2: Quality Control and Metrics Calculation**

  - **Description**: Calculate quality metrics and visualize their distributions to
  guide filtering decisions.

  - **Input Required**: AnnData object with raw counts

  - **Expected Output**: AnnData object with calculated quality metrics (n_genes_by_counts'
- total_counts
- 'pct_counts_mt)

  - **Tools Used**: Scanpy (pp.calculate_qc_metrics)'
- '**Step 3: Cell and Gene Filtering**

  - **Description**: Filter out low-quality spots and rarely expressed genes based
  on quality metrics.

  - **Input Required**: AnnData object with quality metrics

  - **Expected Output**: Filtered AnnData object with high-quality spots and genes

  - **Tools Used**: Scanpy (pp.filter_cells'
- pp.filter_genes)
- '**Step 4: Normalization and'
- Scanpy
path: .opencode/knowledge/workflows/wf-0026-spatial-transcriptomics-analysis-workflow-with-scanpy.md
origin_source: workflow
origin_page: 28
source_entry_index: 18
source_subindex: 1
source_file: doc/Plan_Knowledge.json
status: active
canonical_plan_skill: plan-workflow
analysis_type: scrnaseq-cluster
---

# Spatial Transcriptomics Analysis Workflow with Scanpy

## One-line description

Spatial Transcriptomics Analysis Workflow with Scanpy **Step 1: Data Reading and Initial Setup** - **Description**: Import necessary libraries and read spatial transcriptomics data into an AnnData object. - **Input Re...

## Source

- Source file: `doc/Plan_Knowledge.json`
- Origin source: `workflow`
- Origin page: `28`
- Source entry index: `18`
- Source subindex: `1`
- Canonical skill: `plan-workflow`

## Inputs

Extract user-provided data paths, sample metadata, reference files, tool parameters, and execution permissions from the user request. Do not reuse source example paths without user confirmation.

## Steps

Use the original source excerpt below as the authoritative source-specific procedure. Convert prose or script-specific instructions into explicit, ordered plan or execution steps before use.

## Tool mapping

- Canonical skill: `plan-workflow`
- Registry ID: `wf-0026`
- Analysis/tool category: `scrnaseq-cluster`

## Expected outputs

Derive expected outputs from the selected source excerpt and normalize them into user-specific output directories.

## Validation hints

Validate required inputs, generated outputs, logs, and format-specific assumptions before handing results to the next agent.

## Suggested use

Use this numbered workflow record as source-specific BioMaster knowledge. Core OpenCode skills should select this record through the registry, then normalize paths, sample names, and output directories before generating a plan or command.

## Original source excerpt

```text
Spatial Transcriptomics Analysis Workflow with Scanpy

**Step 1: Data Reading and Initial Setup**
- **Description**: Import necessary libraries and read spatial transcriptomics data into an AnnData object.
- **Input Required**: Spatial transcriptomics dataset (e.g., 10x Genomics Visium data)
- **Expected Output**: AnnData object containing gene expression matrix and spatial coordinates
- **Tools Used**: Scanpy, pandas, matplotlib

---

**Step 2: Quality Control and Metrics Calculation**
- **Description**: Calculate quality metrics and visualize their distributions to guide filtering decisions.
- **Input Required**: AnnData object with raw counts
- **Expected Output**: AnnData object with calculated quality metrics (n_genes_by_counts, total_counts, pct_counts_mt)
- **Tools Used**: Scanpy (pp.calculate_qc_metrics)

---

**Step 3: Cell and Gene Filtering**
- **Description**: Filter out low-quality spots and rarely expressed genes based on quality metrics.
- **Input Required**: AnnData object with quality metrics
- **Expected Output**: Filtered AnnData object with high-quality spots and genes
- **Tools Used**: Scanpy (pp.filter_cells, pp.filter_genes)

---

**Step 4: Normalization and Feature Selection**
- **Description**: Normalize gene expression data and identify highly variable genes for downstream analysis.
- **Input Required**: Filtered AnnData object
- **Expected Output**: Normalized AnnData object with identified highly variable genes
- **Tools Used**: Scanpy (pp.normalize_total, pp.log1p, pp.highly_variable_genes)

---

**Step 5: Dimensionality Reduction and Clustering**
- **Description**: Perform PCA, compute nearest neighbors, run UMAP for visualization, and cluster spots based on transcriptional similarity.
- **Input Required**: Normalized AnnData object with highly variable genes
- **Expected Output**: AnnData object with PCA, UMAP embeddings, and cluster assignments
- **Tools Used**: Scanpy (pp.pca, pp.neighbors, tl.umap, tl.leiden)

---

**Step 6: Spatial Visualization**
- **Description**: Visualize quality metrics, cluster assignments, and gene expression in spatial coordinates.
- **Input Required**: AnnData object with cluster assignments
- **Expected Output**: Spatial plots showing the distribution of clusters and gene expression
- **Tools Used**: Scanpy (pl.spatial)

---

**Step 7: Marker Gene Identification and Analysis**
- **Description**: Identify marker genes for each cluster and visualize their expression patterns.
- **Input Required**: AnnData object with cluster assignments
- **Expected Output**: Ranked lists of marker genes for each cluster, heatmaps, and spatial plots of marker gene expression
- **Tools Used**: Scanpy (tl.rank_genes_groups, pl.rank_genes_groups_heatmap)

---

**Step 8: Spatial Gene Expression Pattern Analysis**
- **Description**: Identify genes with spatial expression patterns using specialized tools.
- **Input Required**: Normalized counts and spatial coordinates
- **Expected Output**: List of genes with significant spatial expression patterns
- **Tools Used**: SpatialDE, SPARK, or other spatial statistics tools
```

## Curation notes

- Keep this record as provenance-preserving knowledge.
- Do not copy example paths directly into user workflows.
- Combine this record with the canonical `workflow` skill before producing user-facing outputs.
