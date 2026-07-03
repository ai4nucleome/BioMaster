---
id: task-0032
title: 'import scanpy as sc; import nichepca as npc; # Run nichePCA on raw counts
  with default normalizat...'
summary: 'import scanpy as sc; import nichepca as npc; # Run nichePCA on raw counts
  with default normalization pipeline (norm -> log1p -> agg -> pca); npc.wf.nichepca(adata,
  knn=25); # Use nichePCA result for neighbor graph and...'
keywords:
- scanpy
- NichePCA_tutorial
- import scanpy as sc
- import nichepca as npc
- '# Run nichePCA on raw counts with default normalizat'
- '# Run nichePCA on raw counts with default normalization pipeline (norm -> log1p
  -> agg -> pca)'
- npc.wf.nichepca(adata
- knn=25)
- '# Use nichePCA result for neighbor graph and Leiden clustering'
- sc.pp.neighbors(adata
- use_rep="X_npca")
- sc.tl.leiden(adata
- resolution=0.5)
- '# If analyzing multiple samples'
- specify the sample key
- knn=25
- sample_key="sample")
- '# If cell type labels exist'
- run nichePCA using cell-type defined niches
- obs_key='cell_type')
- '# Customize the normalization pipeline'
- e.g
- skip median normalization
- pipeline=["log1p"
- '"agg"'
- '"pca"])'
- '# Apply PCA before aggregation step'
- pipeline=["norm"
- '"log1p"'
- '"pca"'
- '"agg"])'
- '# Run nichePCA without PCA step'
- '# Higher knn values (e.g'
- 25) work well in brain data
- lower knn values (e.g
- 10) suit kidney data
- '# Install the latest version via GitHub'
- pip install git+https
- github.com
- imsb-uke
- nichepca.git@main
- '# Example: testing Leiden clustering with multiple resolutions'
- import numpy as np
- import
- Scanpy
path: .opencode/knowledge/tasks/task-0032-import-scanpy-as-sc-import-nichepca-as-npc-run-nichepca-on-raw-counts-with-default-normalizat.md
origin_source: NichePCA_tutorial
origin_page: 33
source_entry_index: 28
source_subindex: 1
source_file: doc/Task_Knowledge.json
status: active
canonical_exec_skill: exec-task
tool: scanpy
---

# import scanpy as sc; import nichepca as npc; # Run nichePCA on raw counts with default normalizat...

## One-line description

import scanpy as sc; import nichepca as npc; # Run nichePCA on raw counts with default normalization pipeline (norm -> log1p -> agg -> pca); npc.wf.nichepca(adata, knn=25); # Use nichePCA result for neighbor graph and...

## Source

- Source file: `doc/Task_Knowledge.json`
- Origin source: `NichePCA_tutorial`
- Origin page: `33`
- Source entry index: `28`
- Source subindex: `1`
- Canonical skill: `exec-task`

## Inputs

Extract user-provided data paths, sample metadata, reference files, tool parameters, and execution permissions from the user request. Do not reuse source example paths without user confirmation.

## Steps

Use the original source excerpt below as the authoritative source-specific procedure. Convert prose or script-specific instructions into explicit, ordered plan or execution steps before use.

## Tool mapping

- Canonical skill: `exec-task`
- Registry ID: `task-0032`
- Analysis/tool category: `scanpy`

## Expected outputs

Derive expected outputs from the selected source excerpt and normalize them into user-specific output directories.

## Validation hints

Validate required inputs, generated outputs, logs, and format-specific assumptions before handing results to the next agent.

## Suggested use

Use this numbered task record as source-specific BioMaster knowledge. Core OpenCode skills should select this record through the registry, then normalize paths, sample names, and output directories before generating a plan or command.

## Original source excerpt

```text
import scanpy as sc; import nichepca as npc; # Run nichePCA on raw counts with default normalization pipeline (norm -> log1p -> agg -> pca); npc.wf.nichepca(adata, knn=25); # Use nichePCA result for neighbor graph and Leiden clustering; sc.pp.neighbors(adata, use_rep="X_npca"); sc.tl.leiden(adata, resolution=0.5); # If analyzing multiple samples, specify the sample key; npc.wf.nichepca(adata, knn=25, sample_key="sample"); # If cell type labels exist, run nichePCA using cell-type defined niches; npc.wf.nichepca(adata, knn=25, obs_key='cell_type'); # Customize the normalization pipeline, e.g., skip median normalization; npc.wf.nichepca(adata, knn=25, pipeline=["log1p", "agg", "pca"]); # Apply PCA before aggregation step; npc.wf.nichepca(adata, knn=25, pipeline=["norm", "log1p", "pca", "agg"]); # Run nichePCA without PCA step; npc.wf.nichepca(adata, knn=25, pipeline=["norm", "log1p", "agg"]); # Higher knn values (e.g., 25) work well in brain data; lower knn values (e.g., 10) suit kidney data; # Install the latest version via GitHub; pip install git+https://github.com/imsb-uke/nichepca.git@main; # Example: testing Leiden clustering with multiple resolutions; import numpy as np; import pandas as pd; import scanpy as sc; from utils import generate_dummy_adata; import nichepca as npc; def test_leiden_multires(): adata = generate_dummy_adata(); sc.pp.normalize_total(adata); sc.pp.log1p(adata); sc.pp.pca(adata); sc.pp.neighbors(adata, use_rep="X_pca"); resolutions = np.linspace(0.1, 1.0, 2); results_parallel = npc.cl.leiden_multires(adata, resolutions, parallel=True, n_jobs=2); results_sequential = npc.cl.leiden_multires(adata, resolutions, parallel=False); assert isinstance(results_parallel, pd.DataFrame); assert results_parallel.shape == (adata.shape[0], len(resolutions)); assert results_parallel.equals(results_sequential); npc.cl.leiden_multires(adata, resolutions, parallel=False, return_leiden=False); assert f"leiden_{resolutions[0]}" in adata.obs.columns; assert f"leiden_{resolutions[1]}" in adata.obs.columns; # Example: constrain number of clusters; def test_leiden_with_nclusters(): adata = generate_dummy_adata(); sc.pp.normalize_total(adata); sc.pp.log1p(adata); sc.pp.pca(adata); sc.pp.neighbors(adata, use_rep="X_pca"); n_clusters = 5; npc.cl.leiden_with_nclusters(adata, n_clusters); assert adata.obs["leiden"].nunique() == n_clusters
```

## Curation notes

- Keep this record as provenance-preserving knowledge.
- Do not copy example paths directly into user workflows.
- Combine this record with the canonical `task` skill before producing user-facing outputs.
