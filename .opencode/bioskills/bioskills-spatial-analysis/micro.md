## Build Spatial Graph

_modules: spatial-graph, spatial-neighbors_

```python
import squidpy as sq
import anndata as ad

# Load phenotyped data
adata = ad.read_h5ad('imc_phenotyped.h5ad')

# Ensure spatial coordinates are set
# adata.obsm['spatial'] should contain (x, y) coordinates

# Build spatial neighbor graph
sq.gr.spatial_neighbors(adata, coord_type='generic', delaunay=True)
# Or by distance
sq.gr.spatial_neighbors(adata, coord_type='generic', radius=50)  # 50 pixels

print(f'Built graph with {adata.obsp["spatial_connectivities"].nnz} edges')
```

## Interaction Enrichment & Statistical Testing

_modules: nhood-enrichment, co-occurrence, ripley, interaction-matrix, permutation-test_

```python
import squidpy as sq
from scipy import stats

# --- Neighborhood enrichment (z-score per cell-type pair) ---
sq.gr.nhood_enrichment(adata, cluster_key='cell_type')
sq.pl.nhood_enrichment(adata, cluster_key='cell_type', save='nhood_enrichment.png')
zscore = adata.uns['cell_type_nhood_enrichment']['zscore']
# Positive: enriched, Negative: depleted

# --- Co-occurrence across distance bands ---
sq.gr.co_occurrence(adata, cluster_key='cell_type')
sq.pl.co_occurrence(adata, cluster_key='cell_type', save='co_occurrence.png')

# --- Ripley's L function (clustering vs dispersion vs radius) ---
sq.gr.ripley(adata, cluster_key='cell_type', mode='L')
sq.pl.ripley(adata, cluster_key='cell_type', save='ripley.png')
# L(r) > r: clustering at distance r
# L(r) < r: dispersion at distance r
# L(r) = r: random distribution

# --- Interaction matrix (total interactions per pair) ---
sq.gr.interaction_matrix(adata, cluster_key='cell_type', normalized=True)
interaction = adata.uns['cell_type_interactions']

# --- Permutation-based p-value for a specific pair ---
def spatial_association_test(adata, type1, type2, cluster_key='cell_type', n_perm=1000):
    '''Permutation test for spatial association between cell types'''
    sq.gr.nhood_enrichment(adata, cluster_key=cluster_key)
    obs_zscore = adata.uns[f'{cluster_key}_nhood_enrichment']['zscore']
    idx1 = list(adata.obs[cluster_key].cat.categories).index(type1)
    idx2 = list(adata.obs[cluster_key].cat.categories).index(type2)
    observed = obs_zscore[idx1, idx2]
    # The z-score is already normalized; derive a two-sided p-value
    pvalue = 2 * (1 - stats.norm.cdf(abs(observed)))
    return {'zscore': observed, 'pvalue': pvalue}

result = spatial_association_test(adata, 'CD8 T cell', 'Tumor')
print(f"CD8-Tumor association: z={result['zscore']:.2f}, p={result['pvalue']:.4f}")
```

## Neighborhood Composition & Hotspots

_modules: neighborhood-composition, hotspots_

```python
import pandas as pd
import numpy as np
from scipy.spatial import cKDTree

def neighborhood_composition(adata, cluster_key='cell_type'):
    '''Calculate cell type composition of each cell's neighborhood'''
    conn = adata.obsp['spatial_connectivities']
    cell_types = adata.obs[cluster_key]
    type_categories = cell_types.cat.categories

    # One-hot encode cell types
    type_onehot = pd.get_dummies(cell_types).values

    # Neighborhood composition = connectivity * one-hot
    nhood_composition = conn @ type_onehot

    # Normalize to fractions
    nhood_sum = np.array(nhood_composition.sum(axis=1)).flatten()
    nhood_sum[nhood_sum == 0] = 1  # Avoid division by zero
    nhood_frac = nhood_composition / nhood_sum[:, np.newaxis]

    # Add to adata
    for i, ct in enumerate(type_categories):
        adata.obs[f'nhood_frac_{ct}'] = nhood_frac[:, i]

    return nhood_frac

nhood_frac = neighborhood_composition(adata)

def find_interaction_hotspots(adata, type1, type2, cluster_key='cell_type', radius=50):
    '''Find regions with high interaction between two cell types'''
    mask1 = adata.obs[cluster_key] == type1
    mask2 = adata.obs[cluster_key] == type2
    spatial = adata.obsm['spatial']

    tree2 = cKDTree(spatial[mask2])
    interaction_scores = np.zeros(mask1.sum())
    for i, (x, y) in enumerate(spatial[mask1]):
        neighbors = tree2.query_ball_point([x, y], r=radius)
        interaction_scores[i] = len(neighbors)

    return interaction_scores

cd8_tumor_interactions = find_interaction_hotspots(adata, 'CD8 T cell', 'Tumor', radius=30)
```

## Spatial Clustering

_modules: leiden, spatial-clustering_

```python
import squidpy as sq
import scanpy as sc

# Combined graph (spatial + molecular information)
sq.gr.spatial_neighbors(adata, coord_type='generic', radius=30)

# Run spatial Leiden on the spatial connectivity graph
sc.tl.leiden(
    adata,
    adjacency=adata.obsp['spatial_connectivities'],
    resolution=0.5,
    key_added='spatial_cluster',
)
```

## Visualization & Export

_modules: visualization, export_

```python
import matplotlib.pyplot as plt
import pandas as pd

# Spatial plot by cell type
sq.pl.spatial_scatter(adata, color='cell_type', size=3, save='spatial_celltypes.png')

# Multiple markers
sq.pl.spatial_scatter(adata, color=['CD8', 'CD4', 'CD68'], size=2, save='spatial_markers.png')

# Highlight a specific interaction (e.g. CD8 T cell vs Tumor)
fig, ax = plt.subplots(figsize=(10, 10))
spatial = adata.obsm['spatial']
ax.scatter(spatial[:, 0], spatial[:, 1], c='lightgray', s=1, alpha=0.5)
for ct, color in [('CD8 T cell', 'red'), ('Tumor', 'blue')]:
    mask = adata.obs['cell_type'] == ct
    ax.scatter(spatial[mask, 0], spatial[mask, 1], c=color, s=5, label=ct)
ax.legend()
ax.set_aspect('equal')
plt.savefig('cd8_tumor_spatial.png', dpi=150)

# --- Export results ---
adata.write('imc_spatial_analyzed.h5ad')

nhood_df = pd.DataFrame(
    adata.uns['cell_type_nhood_enrichment']['zscore'],
    index=adata.obs['cell_type'].cat.categories,
    columns=adata.obs['cell_type'].cat.categories,
)
nhood_df.to_csv('neighborhood_enrichment.csv')
```
