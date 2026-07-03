---
id: task-0053
title: Single-cell full-process analysis with top marker genes includes Data Reading
  and Initialization,...
summary: Single-cell full-process analysis with top marker genes includes Data Reading
  and Initialization, Quality Control (QC), Normalization and Highly Variable Gene
  Selection, Dimensionality Reduction and Visualization, Clu...
keywords:
- scanpy
- Single cell full-process analysis with top marker genes
- Single-cell full-process analysis with top marker genes includes Data Reading and
  Initialization
- Quality Control (QC)
- Normalization and Highly Variable Gene Selection
- Dimensionality Reduction and Visualization
- Clustering Analysis
- Whole-Cell Differential Expression Analysis
- Result Filtering and Top Marker Gene Extraction
- Cell Type Annotation & Functional Enrichment Analysis
- Purity Analysis
- Functional Heterogeneity Analysis
- 'Regulatory Network Analysis includes the following steps: Step 1: Data Reading
  and Initialization'
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
- and scanpy.pp.highly_variable_genes to obtain a normalized expression matrix
- Scanpy
path: .opencode/knowledge/tasks/task-0053-single-cell-full-process-analysis-with-top-marker-genes-includes-data-reading-and-initialization.md
origin_source: Single cell full-process analysis with top marker genes
origin_page: 54
source_entry_index: 49
source_subindex: 1
source_file: doc/Task_Knowledge.json
status: active
canonical_exec_skill: exec-conda
tool: scanpy
---

# Single-cell full-process analysis with top marker genes includes Data Reading and Initialization,...

## One-line description

Single-cell full-process analysis with top marker genes includes Data Reading and Initialization, Quality Control (QC), Normalization and Highly Variable Gene Selection, Dimensionality Reduction and Visualization, Clu...

## Source

- Source file: `doc/Task_Knowledge.json`
- Origin source: `Single cell full-process analysis with top marker genes`
- Origin page: `54`
- Source entry index: `49`
- Source subindex: `1`
- Canonical skill: `exec-conda`

## Inputs

Extract user-provided data paths, sample metadata, reference files, tool parameters, and execution permissions from the user request. Do not reuse source example paths without user confirmation.

## Steps

Use the original source excerpt below as the authoritative source-specific procedure. Convert prose or script-specific instructions into explicit, ordered plan or execution steps before use.

## Tool mapping

- Canonical skill: `exec-conda`
- Registry ID: `task-0053`
- Analysis/tool category: `scanpy`

## Expected outputs

Derive expected outputs from the selected source excerpt and normalize them into user-specific output directories.

## Validation hints

Validate required inputs, generated outputs, logs, and format-specific assumptions before handing results to the next agent.

## Suggested use

Use this numbered task record as source-specific BioMaster knowledge. Core OpenCode skills should select this record through the registry, then normalize paths, sample names, and output directories before generating a plan or command.

## Original source excerpt

```text
Single-cell full-process analysis with top marker genes includes Data Reading and Initialization, Quality Control (QC), Normalization and Highly Variable Gene Selection, Dimensionality Reduction and Visualization, Clustering Analysis, Whole-Cell Differential Expression Analysis, Result Filtering and Top Marker Gene Extraction, Cell Type Annotation & Functional Enrichment Analysis, Purity Analysis, Functional Heterogeneity Analysis, Regulatory Network Analysis includes the following steps: Step 1: Data Reading and Initialization, reading .h5ad or 10x Genomics matrix.mtx files using scanpy.read_10x_mtx or scanpy.read_h5ad to generate an AnnData object containing the raw gene expression matrix (rows=genes, columns=cells) and metadata; Step 2: Quality Control (QC), filtering low-quality cells based on mitochondrial gene percentage (≤20%), total UMIs (≥500), and detected genes using scanpy.pp.calculate_qc_metrics, scanpy.pp.filter_cells, outputting filtered high-quality data;Step 3: Normalization and Highly Variable Gene Selection, standardizing QC-processed data via scanpy.pp.normalize_total, scanpy.pp.log1p, and scanpy.pp.highly_variable_genes to obtain a normalized expression matrix and a list of highly variable genes (HVGs); Step 4: Dimensionality Reduction and Visualization, performing PCA dimensionality reduction using scanpy.tl.pca, constructing a KNN neighborhood graph with scanpy.pp.neighbors, output an AnnData object with dimension-reduced results; Step 5: Clustering Analysis, applying Leiden algorithm via scanpy.tl.leiden and UMAP/t-SNE visualization with scanpy.tl.umap based on dimension-reduced data, outputting cell cluster labels and visualization plots (.png); Step 6: Whole-Cell Differential Expression Analysis, applying tools to compare group differences at the whole-cell level, inputting normalized expression matrices and grouping information, using Scanpy's rank_genes_groups, sc.tl.rank_genes_groups(adata, groupby='leiden', method='t-test'),Extract the differential expression results, outputting a table of differentially expressed genes (DEGs) with with colums of log2FC, p-values, and adjusted p-values, and respectively rename the columns to logFC, pvals, and adj_pvals, df.rename(columns={'pvals_adj':'adj_pvals','logfoldchanges':'logFC'}, inplace=True); Step 7: Result Filtering, filtering marker genes based on significance thresholds adj_pvals, logFC, output high-confidence marker gene lists with adj_pvals < 0.05 and logFC > 1; Step 8 Cell Type Annotation, input high-confidence marker gene list (.csv with logFC and adj_pval fields) and a raw AnnData object (containing a normalized expression matrix and cluster labels). import scanpy as sc, import pandas as pd, import celltypist, from celltypist import models, load the clustered .h5ad and csv data. for example, adata = sc.read_h5ad(.h5ad), marker_genes = pd.read_csv('.csv', header=0) , usually the gene name is the second column of the csv file; then Automated annotation (based on CellTypist): models.download_models(), predictions = celltypist.annotate(adata, model=), adata = predictions.to_adata(), then verification by UMAP annotation overlay sc.pl.umap(adata, color=['cell_type', 'leiden'], legend_loc='on data', frameon=False), output adata.write('annotated_singlecellexpress.h5ad') and umap plot files; step 9 Pseudotime trajectory analysis, input the Annotated AnnData (with cell_type column) and subpopulation labels (e.g., leiden_clusters), then use scanpy tool to deal with it. sc.tl.diffmap(adata), sc.pl.diffmap(adata, color='leiden_clusters'), Output: UMAP plot overlaid with Diffusion Map trajectory(.png); step 10 Purity Analysis (Subpopulation Homogeneity Evaluation), import scanpy as sc, import numpy as np, from scipy.stats import gini, Calculate the Gini coefficient of each subpopulation (measuring gene expression dispersion), adata.var['gini_index'] = adata.to_df().apply(gini, axis=0), output gini_scores.csv, Filter genes with Gini > 0.7 and mark them as highly heterogeneous genes, cluster_gini = adata.obs.groupby('leiden_clusters').apply(lambda x: (x[:, adata.var['gini_index']>0.7].mean(axis=1))), cluster_gini.to_csv('cluster_purity.csv'), output cluster_purity.csv; step 11 Functional Heterogeneity Analysis, Differential gene screening Use the built-in method of Scanpy to quickly screen subpopulation marker genes, sc.tl.rank_genes_groups(adata, groupby='leiden_clusters', method='wilcoxon'),markers = sc.get.rank_genes_groups_df(adata, group=None), markers.to_csv('cluster_markers.csv'); step 12 Regulatory Network Analysis, Goal Predict core transcription factors (TF). first make sure the python version is 3.10.16, if not then conda install python==3.10.16, and then prepare proper version of pakage pip install scanpy==1.9.0 numba==0.56.4 numpy==1.23.5 anndata==0.8.0, TF activity score Quick scoring using a precompiled TF target gene database (such as DoRothEA), import decoupler as dc, net = dc.get_dorothea(organism='human', levels=['A','B']) , Infer TF activity using a multivariate linear model, dc.run_mlm(adata,dorothea_net, source='source', target='target', use_raw=False), do not put the key_added in dc.run_mlm ! Extract TF activity matrix, tf_activity_df = pd.DataFrame(adata.obsm['X_diffmap'],index=adata.obs.index), tf_activity_df.to_csv(), import pandas as pd, Correlate TF activity with gene expression, genes_expr_df = adata.to_df(), big_df = pd.concat([tf_activity_df, genes_expr_df], axis=1), corr_matrix = big_df.corr().loc[tf_activity_df.columns, genes_expr_df.columns], Save the regulatory network (TF-gene correlation) to CSV, corr_matrix.to_csv(), Output: tf_activity.csv (TF activity matrix for each cell), tf_gene_corr.csv (TF-gene correlation, |r|>0.3 is considered associated)
```

## Curation notes

- Keep this record as provenance-preserving knowledge.
- Do not copy example paths directly into user workflows.
- Combine this record with the canonical `task` skill before producing user-facing outputs.
