## Setup & Basic Spatial Plot

_modules: imports, spatial-scatter, qc-overlay_

```python
import squidpy as sq
import scanpy as sc
import matplotlib.pyplot as plt

# Version sanity check (adapt signatures if versions differ)
# pip show <package>  ->  help(module.function)

# Squidpy: spots colored by a single variable
sq.pl.spatial_scatter(adata, color='total_counts', size=1.3)

# Squidpy: multiple variables in one figure
sq.pl.spatial_scatter(adata, color=['total_counts', 'n_genes_by_counts'], ncols=2)

# Scanpy: spatial plot colored by cluster label
sc.pl.spatial(adata, color='leiden', spot_size=1.5)

# Scanpy: multiple genes side by side
sc.pl.spatial(adata, color=['GENE1', 'GENE2', 'GENE3'], ncols=3)
```

## Tissue Image Overlay & Appearance

_modules: histology-overlay, appearance, spot-size_

```python
# Plot with tissue background and semi-transparent image
sc.pl.spatial(adata, color='leiden', img_key='hires', alpha_img=0.5)

# Plot without the tissue image
sc.pl.spatial(adata, color='leiden', img_key=None)

# Customize spot size, palette, title, and frame
sc.pl.spatial(
    adata,
    color='leiden',
    spot_size=1.5,
    palette='tab20',
    title='Cluster assignments',
    frameon=False,
)
```

## Gene Expression on Tissue

_modules: gene-expression, colormap, co-expression_

```python
import numpy as np
from matplotlib.colors import Normalize

# Single gene with percentile-capped range
sc.pl.spatial(adata, color='CD3D', cmap='viridis', vmin=0, vmax='p99')

# Multiple genes side by side
genes = ['CD3D', 'MS4A1', 'CD14', 'NKG7']
sc.pl.spatial(adata, color=genes, ncols=2, cmap='Reds', vmin=0)

# Manual colorbar control across a multi-gene panel
fig, axes = plt.subplots(1, 2, figsize=(12, 5))
for ax, gene in zip(axes, ['GENE1', 'GENE2']):
    sc.pl.spatial(adata, color=gene, ax=ax, show=False, vmin=0, vmax=5, cmap='viridis')
    ax.set_title(gene)
plt.tight_layout()
plt.savefig('gene_expression.png', dpi=300)

# Co-expression as dual-channel RGB (red=gene1, green=gene2)
gene1, gene2 = 'CD3D', 'CD8A'
expr1 = adata[:, gene1].X.toarray().flatten()
expr2 = adata[:, gene2].X.toarray().flatten()

norm = Normalize(vmin=0, vmax=np.percentile(np.concatenate([expr1, expr2]), 99))
colors = np.zeros((adata.n_obs, 3))
colors[:, 0] = norm(expr1)  # Red channel
colors[:, 1] = norm(expr2)  # Green channel

fig, ax = plt.subplots(figsize=(8, 8))
coords = adata.obsm['spatial']
ax.scatter(coords[:, 0], coords[:, 1], c=colors, s=10)
ax.set_aspect('equal')
ax.set_title(f'{gene1} (red) + {gene2} (green)')
plt.savefig('coexpression.png', dpi=300)
```

## Multi-Sample Comparison & Annotation

_modules: multi-sample, annotation, crop-zoom_

```python
# Split by sample using scanpy's groups argument
sc.pl.spatial(adata, color='leiden', groups=['sample1', 'sample2'], ncols=2)

# Manual per-sample panels
samples = adata.obs['sample'].unique()
fig, axes = plt.subplots(1, len(samples), figsize=(5*len(samples), 5))
for ax, sample in zip(axes, samples):
    adata_sub = adata[adata.obs['sample'] == sample]
    sc.pl.spatial(adata_sub, color='leiden', ax=ax, show=False, title=sample)
plt.tight_layout()

# Overlay cluster labels at spatial centroids
fig, ax = plt.subplots(figsize=(8, 8))
sc.pl.spatial(adata, color='leiden', ax=ax, show=False)
for cluster in adata.obs['leiden'].unique():
    mask = adata.obs['leiden'] == cluster
    coords = adata.obsm['spatial'][mask].mean(axis=0)
    ax.annotate(f'C{cluster}', coords, fontsize=12, ha='center')
plt.savefig('annotated.png', dpi=300)

# Crop / zoom into a region (note: y is inverted in images)
x_min, x_max = 2000, 4000
y_min, y_max = 2000, 4000
fig, ax = plt.subplots(figsize=(8, 8))
sc.pl.spatial(adata, color='leiden', ax=ax, show=False)
ax.set_xlim(x_min, x_max)
ax.set_ylim(y_max, y_min)
plt.savefig('zoomed.png', dpi=300)
```

## Spatial Statistics Visualization

_modules: spatial-statistics, moran-i, neighborhood-enrichment_

```python
# Map a gene of interest (e.g. a Moran's I hit) onto the tissue
sq.pl.spatial_scatter(adata, color='GENE1', size=1.3)

# Neighborhood enrichment heatmap between clusters
sq.pl.nhood_enrichment(adata, cluster_key='leiden')

# Co-occurrence probability across spatial scales
sq.pl.co_occurrence(adata, cluster_key='leiden')
```

## Interactive Exploration & Publication Figures

_modules: napari, publication, multi-panel_

```python
import napari

# Interactive napari exploration
viewer = napari.Viewer()
library_id = list(adata.uns['spatial'].keys())[0]
img = adata.uns['spatial'][library_id]['images']['hires']
viewer.add_image(img, name='tissue')
coords = adata.obsm['spatial']
scalef = adata.uns['spatial'][library_id]['scalefactors']['tissue_hires_scalef']
viewer.add_points(coords * scalef, size=10, name='spots')
napari.run()

# Publication-quality single figure (PDF + PNG)
fig, ax = plt.subplots(figsize=(8, 8))
sc.pl.spatial(
    adata,
    color='leiden',
    ax=ax,
    show=False,
    frameon=False,
    title='',
    legend_loc='right margin',
)
plt.savefig('figure.pdf', dpi=300, bbox_inches='tight')
plt.savefig('figure.png', dpi=300, bbox_inches='tight')

# Composite multi-panel overview (2x3)
fig = plt.figure(figsize=(15, 10))
ax1 = fig.add_subplot(2, 3, 1)
sc.pl.spatial(adata, color='leiden', ax=ax1, show=False, title='Clusters')
ax2 = fig.add_subplot(2, 3, 2)
sc.pl.spatial(adata, color='CD3D', ax=ax2, show=False, title='CD3D', cmap='Reds')
ax3 = fig.add_subplot(2, 3, 3)
sc.pl.spatial(adata, color='MS4A1', ax=ax3, show=False, title='MS4A1', cmap='Blues')
ax4 = fig.add_subplot(2, 3, 4)
sc.pl.spatial(adata, color='total_counts', ax=ax4, show=False, title='Total counts')
ax5 = fig.add_subplot(2, 3, 5)
sc.pl.umap(adata, color='leiden', ax=ax5, show=False, title='UMAP')
ax6 = fig.add_subplot(2, 3, 6)
sc.pl.violin(adata, ['CD3D', 'MS4A1'], groupby='leiden', ax=ax6, show=False)
plt.tight_layout()
plt.savefig('multi_panel.png', dpi=300)
```
