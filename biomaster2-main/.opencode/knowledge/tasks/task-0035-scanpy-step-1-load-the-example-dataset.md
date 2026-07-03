---
id: task-0035
title: 'Scanpy:# Step 1: Load the example dataset'
summary: 'Scanpy:# Step 1: Load the example dataset adata = sc.datasets.pbmc3k() #
  Step 2: Preprocess the data sc.pp.filter_genes(adata, min_cells=3) sc.pp.normalize_total(adata)
  sc.pp.log1p(adata) sc.pp.highly_variable_genes(a...'
keywords:
- seurat
- Scanpy
- 'Scanpy:# Step 1: Load the example dataset'
- 'Scanpy:# Step 1: Load the example dataset

  adata = sc.datasets.pbmc3k()'
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

  sc.pp.neighbors(adata)'
- '# Step 4: Calculate neighborhood enrichment

  sc.tl.neighborhood_enrichment(adata'
- cluster_key="louvain")
- '# Step 5: Visualize the neighborhood enrichment results

  sc.pl.neighborhood_enrichment(adata'
- '# Step 6: Calculate Ripley’s K statistic

  sc.tl.ripley(adata'
- cluster_key="louvain"
- mode="K"
- 'max_dist=500)

  sc.pl.ripley(adata'
- mode="K")
- '# Step 7: Calculate ligand - receptor interactions

  sc.tl.ligrec(adata'
- n_perms=100
- clusters=["CD14+ Monocytes"
- '"CD4+ T cells"])

  sc.pl.ligrec(adata'
- source_groups="CD4+ T cells"
- target_groups=["CD14+ Monocytes"]
- pvalue_threshold=0.05
- swap_axes=True)
- '# Step 8: Calculate spatial autocorrelation

  sc.tl.spatial(adata)

  print(adata.uns["spatial"].head(10))'
- Seurat
path: .opencode/knowledge/tasks/task-0035-scanpy-step-1-load-the-example-dataset.md
origin_source: Scanpy
origin_page: 36
source_entry_index: 31
source_subindex: 1
source_file: doc/Task_Knowledge.json
status: active
canonical_exec_skill: exec-task
tool: seurat
---

# Scanpy:# Step 1: Load the example dataset

## One-line description

Scanpy:# Step 1: Load the example dataset adata = sc.datasets.pbmc3k() # Step 2: Preprocess the data sc.pp.filter_genes(adata, min_cells=3) sc.pp.normalize_total(adata) sc.pp.log1p(adata) sc.pp.highly_variable_genes(a...

## Source

- Source file: `doc/Task_Knowledge.json`
- Origin source: `Scanpy`
- Origin page: `36`
- Source entry index: `31`
- Source subindex: `1`
- Canonical skill: `exec-task`

## Inputs

Extract user-provided data paths, sample metadata, reference files, tool parameters, and execution permissions from the user request. Do not reuse source example paths without user confirmation.

## Steps

Use the original source excerpt below as the authoritative source-specific procedure. Convert prose or script-specific instructions into explicit, ordered plan or execution steps before use.

## Tool mapping

- Canonical skill: `exec-task`
- Registry ID: `task-0035`
- Analysis/tool category: `seurat`

## Expected outputs

Derive expected outputs from the selected source excerpt and normalize them into user-specific output directories.

## Validation hints

Validate required inputs, generated outputs, logs, and format-specific assumptions before handing results to the next agent.

## Suggested use

Use this numbered task record as source-specific BioMaster knowledge. Core OpenCode skills should select this record through the registry, then normalize paths, sample names, and output directories before generating a plan or command.

## Original source excerpt

```text
Scanpy:# Step 1: Load the example dataset
adata = sc.datasets.pbmc3k()

# Step 2: Preprocess the data
sc.pp.filter_genes(adata, min_cells=3)
sc.pp.normalize_total(adata)
sc.pp.log1p(adata)
sc.pp.highly_variable_genes(adata, flavor="seurat", n_top_genes=2000)
adata = adata[:, adata.var.highly_variable]

# Step 3: Calculate spatial neighbors
sc.pp.neighbors(adata)

# Step 4: Calculate neighborhood enrichment
sc.tl.neighborhood_enrichment(adata, cluster_key="louvain")

# Step 5: Visualize the neighborhood enrichment results
sc.pl.neighborhood_enrichment(adata, cluster_key="louvain")

# Step 6: Calculate Ripley’s K statistic
sc.tl.ripley(adata, cluster_key="louvain", mode="K", max_dist=500)
sc.pl.ripley(adata, cluster_key="louvain", mode="K")

# Step 7: Calculate ligand - receptor interactions
sc.tl.ligrec(adata, n_perms=100, cluster_key="louvain", clusters=["CD14+ Monocytes", "CD4+ T cells"])
sc.pl.ligrec(adata, cluster_key="louvain", source_groups="CD4+ T cells", target_groups=["CD14+ Monocytes"], pvalue_threshold=0.05, swap_axes=True)

# Step 8: Calculate spatial autocorrelation
sc.tl.spatial(adata)
print(adata.uns["spatial"].head(10))
```

## Curation notes

- Keep this record as provenance-preserving knowledge.
- Do not copy example paths directly into user workflows.
- Combine this record with the canonical `task` skill before producing user-facing outputs.
