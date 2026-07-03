---
id: task-0034
title: 'Squidpy:# Step 1: Load the example dataset'
summary: 'Squidpy:# Step 1: Load the example dataset adata = sq.datasets.slideseqv2()
  # Step 2: Preprocess the data sc.pp.filter_genes(adata, min_cells=3) sc.pp.normalize_total(adata)
  sc.pp.log1p(adata) sc.pp.highly_variable_ge...'
keywords:
- seurat
- Squidpy
- 'Squidpy:# Step 1: Load the example dataset'
- 'Squidpy:# Step 1: Load the example dataset

  adata = sq.datasets.slideseqv2()'
- '# Step 2: Preprocess the data

  sc.pp.filter_genes(adata'
- 'min_cells=3)

  sc.pp.normalize_total(adata)

  sc.pp.log1p(adata)

  sc.pp.highly_variable_genes(adata'
- flavor="seurat"
- 'n_top_genes=2000)

  adata = adata['
- adata.var.highly_variable]
- '# Step 3: Calculate spatial neighbors

  sq.gr.spatial_neighbors(adata)'
- '# Step 4: Calculate neighborhood enrichment

  sq.gr.nhood_enrichment(adata'
- cluster_key="cluster")
- '# Step 5: Visualize the neighborhood enrichment results

  sq.pl.nhood_enrichment(adata'
- '# Step 6: Calculate Ripley’s K statistic

  sq.gr.ripley(adata'
- cluster_key="cluster"
- mode="K"
- 'max_dist=500)

  sq.pl.ripley(adata'
- mode="K")
- '# Step 7: Calculate ligand - receptor interactions

  sq.gr.ligrec(adata'
- n_perms=100
- clusters=["Polydendrocytes"
- '"Oligodendrocytes"])

  sq.pl.ligrec(adata'
- source_groups="Oligodendrocytes"
- target_groups=["Polydendrocytes"]
- pvalue_threshold=0.05
- swap_axes=True)
- '# Step 8: Calculate spatial autocorrelation

  sq.gr.spatial_autocorr(adata'
- 'mode="moran")

  print(adata.uns["moranI"].head(10))'
- Seurat
path: .opencode/knowledge/tasks/task-0034-squidpy-step-1-load-the-example-dataset.md
origin_source: Squidpy
origin_page: 35
source_entry_index: 30
source_subindex: 1
source_file: doc/Task_Knowledge.json
status: active
canonical_exec_skill: exec-task
tool: seurat
---

# Squidpy:# Step 1: Load the example dataset

## One-line description

Squidpy:# Step 1: Load the example dataset adata = sq.datasets.slideseqv2() # Step 2: Preprocess the data sc.pp.filter_genes(adata, min_cells=3) sc.pp.normalize_total(adata) sc.pp.log1p(adata) sc.pp.highly_variable_ge...

## Source

- Source file: `doc/Task_Knowledge.json`
- Origin source: `Squidpy`
- Origin page: `35`
- Source entry index: `30`
- Source subindex: `1`
- Canonical skill: `exec-task`

## Inputs

Extract user-provided data paths, sample metadata, reference files, tool parameters, and execution permissions from the user request. Do not reuse source example paths without user confirmation.

## Steps

Use the original source excerpt below as the authoritative source-specific procedure. Convert prose or script-specific instructions into explicit, ordered plan or execution steps before use.

## Tool mapping

- Canonical skill: `exec-task`
- Registry ID: `task-0034`
- Analysis/tool category: `seurat`

## Expected outputs

Derive expected outputs from the selected source excerpt and normalize them into user-specific output directories.

## Validation hints

Validate required inputs, generated outputs, logs, and format-specific assumptions before handing results to the next agent.

## Suggested use

Use this numbered task record as source-specific BioMaster knowledge. Core OpenCode skills should select this record through the registry, then normalize paths, sample names, and output directories before generating a plan or command.

## Original source excerpt

```text
Squidpy:# Step 1: Load the example dataset
adata = sq.datasets.slideseqv2()

# Step 2: Preprocess the data
sc.pp.filter_genes(adata, min_cells=3)
sc.pp.normalize_total(adata)
sc.pp.log1p(adata)
sc.pp.highly_variable_genes(adata, flavor="seurat", n_top_genes=2000)
adata = adata[:, adata.var.highly_variable]

# Step 3: Calculate spatial neighbors
sq.gr.spatial_neighbors(adata)

# Step 4: Calculate neighborhood enrichment
sq.gr.nhood_enrichment(adata, cluster_key="cluster")

# Step 5: Visualize the neighborhood enrichment results
sq.pl.nhood_enrichment(adata, cluster_key="cluster")

# Step 6: Calculate Ripley’s K statistic
sq.gr.ripley(adata, cluster_key="cluster", mode="K", max_dist=500)
sq.pl.ripley(adata, cluster_key="cluster", mode="K")

# Step 7: Calculate ligand - receptor interactions
sq.gr.ligrec(adata, n_perms=100, cluster_key="cluster", clusters=["Polydendrocytes", "Oligodendrocytes"])
sq.pl.ligrec(adata, cluster_key="cluster", source_groups="Oligodendrocytes", target_groups=["Polydendrocytes"], pvalue_threshold=0.05, swap_axes=True)

# Step 8: Calculate spatial autocorrelation
sq.gr.spatial_autocorr(adata, mode="moran")
print(adata.uns["moranI"].head(10))
```

## Curation notes

- Keep this record as provenance-preserving knowledge.
- Do not copy example paths directly into user workflows.
- Combine this record with the canonical `task` skill before producing user-facing outputs.
