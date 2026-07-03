## Check Topology Assumptions

_modules: topology-check, diffusion-map, neighborhood-graph_

```python
import scanpy as sc

# Compute neighborhood graph if not already present
sc.pp.neighbors(adata, n_neighbors=15, n_pcs=30)

# Compute diffusion map for manifold visualization
sc.tl.diffmap(adata)

# Compute a force-directed layout for trajectory-friendly visualization
sc.tl.draw_graph(adata, layout='fa')

# Visualize clusters on the diffusion map / draw_graph to assess continuity
sc.pl.diffmap(adata, color='leiden', legend_loc='on data')
sc.pl.draw_graph(adata, color='leiden', legend_loc='on data')
```

## Pick Roots and Branches

_modules: root-selection, branch-definition, marker-based-root_

```python
import scanpy as sc
import numpy as np

# Option A: Root by known marker expression (e.g., high expression of a progenitor marker)
root_marker = 'POU5F1'  # example; adjust per dataset
if root_marker in adata.var_names:
    root_cells = adata[:, root_marker].X.toarray().flatten() > 0.5
    adata.obs['root_score'] = adata[:, root_marker].X.toarray().flatten()

# Option B: Root by earliest time point in metadata
if 'timepoint' in adata.obs:
    earliest = adata.obs['timepoint'].min()
    root_cells = adata.obs['timepoint'] == earliest

# Store root mask for downstream use
adata.obs['is_root'] = root_cells

# Print number of root cells identified
print(f'Root cells identified: {root_cells.sum()}')
```

## Infer Trajectories

_modules: pseudotime, dpt, rna-velocity, trajectory-inference_

```python
import scanpy as sc

# --- Diffusion Pseudotime (DPT) ---
# Requires a root cell to be specified
sc.tl.dpt(adata, n_branchings=1)

# Verify pseudotime aligns with known markers
sc.pl.diffmap(adata, color=['dpt_pseudotime', 'leiden', root_marker],
              legend_loc='on data')

# --- RNA Velocity (if spliced/unspliced data available) ---
# import scvelo as scv
# scv.pp.moments(adata, n_pcs=30, n_neighbors=30)
# scv.tl.velocity(adata)
# scv.tl.velocity_graph(adata)
# scv.pl.velocity_embedding_stream(adata, basis='umap')
# scv.tl.pseudotime(adata)  # velocity-driven pseudotime
# scv.pl.scatter(adata, color='velocity_pseudotime', cmap='viridis')
```

## Identify Dynamic Features

_modules: dynamic-genes, branch-markers, differential-expression, pseudotime-genes_

```python
import scanpy as sc

# --- Genes varying along pseudotime (DPT groups) ---
sc.tl.dpt_groups_pseudotime(adata)
sc.tl.rank_genes_groups(adata, groupby='dpt_groups', method='wilcoxon')
sc.pl.rank_genes_groups(adata, n_genes=20, sharey=False)

# --- Branch-specific markers (if branching exists) ---
# sc.tl.rank_genes_groups(adata, groupby='dpt_groups', groups=['Branch_A'],
#                         reference='Branch_B', method='wilcoxon')

# --- Dynamic gene trends along pseudotime ---
# sc.tl.paga(adata, groups='leiden')
# sc.pl.paga_compare(adata, threshold=0.1, edge_width_scale=0.5)

# Export top dynamic genes
result = sc.get.rank_genes_groups_df(adata, group=None)
result.to_csv('results/dynamic_genes.csv', index=False)
```

## Visualize with Context

_modules: visualization, trajectory-overlay, pseudotime-heatmap, branch-visualization_

```python
import scanpy as sc
import matplotlib.pyplot as plt

# --- Trajectory overlay on UMAP ---
sc.pl.umap(adata, color=['dpt_pseudotime', 'leiden'],
           legend_loc='on data', title=['Pseudotime', 'Clusters'],
           save='_pseudotime_trajectory.png')

# --- Pseudotime heatmap of top dynamic genes ---
top_genes = result['names'].head(20).tolist()
sc.pl.heatmap(adata, top_genes, groupby='dpt_groups',
              dendrogram=True, standard_scale='var',
              save='_pseudotime_heatmap.png')

# --- Branch-specific expression (if applicable) ---
# sc.pl.umap(adata, color=['Branch_marker_1', 'Branch_marker_2'],
#            cmap='RdBu_r', save='_branch_markers.png')

plt.close('all')
```
