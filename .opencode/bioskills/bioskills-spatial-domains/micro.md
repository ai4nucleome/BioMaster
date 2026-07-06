## Setup & Baseline Clustering

_modules: setup, baseline, neighbors, leiden_

```python
import squidpy as sq
import scanpy as sc
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Reference versions: matplotlib 3.8+, numpy 1.26+, pandas 2.2+,
# scanpy 1.10+, scikit-learn 1.4+, scipy 1.12+, squidpy 1.3+
# Verify with `pip show <package>` and adapt APIs if versions differ.

# Baseline: expression-only Leiden clustering (ignores spatial context)
sc.pp.neighbors(adata, n_neighbors=15, n_pcs=30)
sc.tl.leiden(adata, resolution=0.5, key_added='leiden')

# Visualize baseline clusters on tissue
sq.pl.spatial_scatter(adata, color='leiden', size=1.3)
```

## Spatial Domain Detection

_modules: spatial-neighbors, spatial-leiden, combined-graph, bayesspace, stagate, graph-attention_

```python
from scipy.sparse import csr_matrix
from sklearn.preprocessing import normalize

# --- (a) Squidpy spatial graph + Leiden (spatial proximity only) ---
sq.gr.spatial_neighbors(adata, coord_type='generic', n_neighs=6)
sc.tl.leiden(adata, resolution=0.5, key_added='spatial_leiden',
             neighbors_key='spatial_neighbors')
sq.pl.spatial_scatter(adata, color='spatial_leiden', size=1.3)

# --- (b) Combined expression + spatial graph (weighted average) ---
sq.gr.spatial_neighbors(adata, coord_type='generic', n_neighs=6)
sc.pp.neighbors(adata, n_neighbors=15, n_pcs=30)

spatial_weight = 0.3
spatial_norm = normalize(adata.obsp['spatial_connectivities'], norm='l1', axis=1)
expr_norm = normalize(adata.obsp['connectivities'], norm='l1', axis=1)
combined = spatial_weight * spatial_norm + (1 - spatial_weight) * expr_norm
adata.obsp['combined_connectivities'] = csr_matrix(combined)

sc.tl.leiden(adata, resolution=0.5, key_added='combined_leiden',
             adjacency=adata.obsp['combined_connectivities'])

# --- (c) BayesSpace (run in R, import results via rpy2) ---
# R: library(BayesSpace)
#     sce <- spatialPreprocess(sce, platform="Visium")
#     sce <- spatialCluster(sce, q=7, nrep=10000)
#     saveRDS(sce, "sce_bayesspace.rds")
import rpy2.robjects as ro
from rpy2.robjects import pandas2ri
pandas2ri.activate()
ro.r('sce <- readRDS("sce_bayesspace.rds")')
adata.obs['bayesspace'] = list(ro.r('colData(sce)$spatial.cluster'))

# --- (d) STAGATE (graph attention network embeddings) ---
import STAGATE
STAGATE.Cal_Spatial_Net(adata, rad_cutoff=150)
STAGATE.Stats_Spatial_Net(adata)
adata = STAGATE.train_STAGATE(adata, alpha=0)
sc.pp.neighbors(adata, use_rep='STAGATE')
sc.tl.leiden(adata, resolution=0.5, key_added='stagate_leiden')
```

## Domain Refinement

_modules: smoothing, boundary-refinement_

```python
from scipy import sparse

def smooth_domains(adata, cluster_key, n_iter=1):
    conn = adata.obsp['spatial_connectivities']
    labels = adata.obs[cluster_key].values
    categories = adata.obs[cluster_key].cat.categories
    for _ in range(n_iter):
        new_labels = []
        for i in range(adata.n_obs):
            neighbors = conn[i].nonzero()[1]
            if len(neighbors) > 0:
                neighbor_labels = labels[neighbors]
                unique, counts = np.unique(neighbor_labels, return_counts=True)
                new_labels.append(unique[counts.argmax()])
            else:
                new_labels.append(labels[i])
        labels = np.array(new_labels)
    adata.obs[f'{cluster_key}_smoothed'] = pd.Categorical(labels, categories=categories)

smooth_domains(adata, 'leiden', n_iter=2)
sq.pl.spatial_scatter(adata, color=['leiden', 'leiden_smoothed'], ncols=2)
```

## Evaluation & Comparison

_modules: silhouette, ari, evaluation_

```python
from sklearn.metrics import silhouette_score, adjusted_rand_score

# Spatial and transcriptional coherence of domains
coords = adata.obsm['spatial']
labels = adata.obs['spatial_leiden'].values
spatial_silhouette = silhouette_score(coords, labels)
expr_silhouette = silhouette_score(adata.obsm['X_pca'], labels)
print(f'Spatial silhouette: {spatial_silhouette:.3f}')
print(f'Expression silhouette: {expr_silhouette:.3f}')

# Compare methods with adjusted Rand index
methods = ['leiden', 'spatial_leiden', 'combined_leiden']
for i, m1 in enumerate(methods):
    for m2 in methods[i+1:]:
        ari = adjusted_rand_score(adata.obs[m1], adata.obs[m2])
        print(f'{m1} vs {m2}: ARI = {ari:.3f}')
```

## Marker Genes & Annotation

_modules: marker-genes, differential-expression, annotation_

```python
# Marker genes per domain (Wilcoxon rank-sum)
sc.tl.rank_genes_groups(adata, groupby='spatial_leiden', method='wilcoxon')
markers = sc.get.rank_genes_groups_df(adata, group=None)
print(markers.groupby('group').head(5))

top_markers = markers.groupby('group').head(1)['names'].tolist()
sq.pl.spatial_scatter(adata, color=top_markers[:6], ncols=3)

# Manual annotation based on markers
 domain_annotations = {
    '0': 'White matter',
    '1': 'Cortex layer 1',
    '2': 'Cortex layer 2/3',
    '3': 'Cortex layer 4',
    '4': 'Cortex layer 5',
    '5': 'Cortex layer 6',
}
adata.obs['domain'] = adata.obs['spatial_leiden'].map(domain_annotations)
sq.pl.spatial_scatter(adata, color='domain', size=1.3)
```
