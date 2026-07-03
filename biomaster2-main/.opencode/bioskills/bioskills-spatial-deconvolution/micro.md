## Data Loading & Gene Alignment

_modules: data-loading, gene-alignment_

```python
import scanpy as sc
import anndata as ad
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Load reference scRNA-seq (must contain a cell_type annotation)
adata_ref = sc.read_h5ad('reference_scrna.h5ad')
adata_ref.obs['cell_type'] = adata_ref.obs['cell_type'].astype('category')

# Load spatial data (must contain raw counts and obsm['spatial'])
adata_vis = sc.read_h5ad('spatial_data.h5ad')

# Restrict both objects to the shared gene set
intersect = np.intersect1d(adata_vis.var_names, adata_ref.var_names)
adata_ref = adata_ref[:, intersect].copy()
adata_vis = adata_vis[:, intersect].copy()
```

## Reference Signature Training (cell2location)

_modules: cell2location, reference-signature, regression-model_

```python
import cell2location
from cell2location.utils.filtering import filter_genes
from cell2location.models import RegressionModel

# Select informative genes for deconvolution
selected = filter_genes(adata_ref, cell_count_cutoff=5, cell_percentage_cutoff2=0.03,
                        nonz_mean_cutoff=1.12)
adata_ref = adata_ref[:, selected].copy()

# Configure the reference for the regression model
RegressionModel.setup_anndata(
    adata_ref,
    labels_key='cell_type',
)

# Train the reference signature model
mod = RegressionModel(adata_ref)
mod.train(max_epochs=250, use_gpu=True)

# Export posterior reference signatures
adata_ref = mod.export_posterior(adata_ref, sample_kwargs={'num_samples': 1000})
ref_sig = adata_ref.varm['means_per_cluster_mu_fg']
```

## Spatial Deconvolution (cell2location)

_modules: cell2location, spatial-deconvolution, abundance-estimation_

```python
# Align spatial data to the reference gene set
adata_vis = adata_vis[:, adata_ref.var_names].copy()

# Configure the spatial AnnData for Cell2location
cell2location.models.Cell2location.setup_anndata(adata_vis)

# Train the spatial deconvolution model
mod_spatial = cell2location.models.Cell2location(
    adata_vis,
    cell_state_df=ref_sig,
    N_cells_per_location=10,   # Expected cells per spot; tune to tissue
    detection_alpha=20,
)
mod_spatial.train(max_epochs=30000, use_gpu=True)

# Export posterior cell-type abundances
adata_vis = mod_spatial.export_posterior(adata_vis, sample_kwargs={'num_samples': 1000})
```

## Alternative Deconvolution Methods

_modules: tangram, rctd, optimal-transport, alternative-methods_

```python
import tangram as tg

# --- Tangram path ---
adata_sc = sc.read_h5ad('reference_scrna.h5ad')
adata_sp = sc.read_h5ad('spatial_data.h5ad')

sc.pp.normalize_total(adata_sc)
sc.pp.log1p(adata_sc)

# Identify marker genes per cell type
sc.tl.rank_genes_groups(adata_sc, groupby='cell_type', method='wilcoxon')
markers = sc.get.rank_genes_groups_df(adata_sc, group=None)
markers = markers[markers['pvals_adj'] < 0.01].groupby('group').head(100)
marker_genes = markers['names'].unique().tolist()

# Align adatas and map single cells to spatial spots
tg.pp_adatas(adata_sc, adata_sp, genes=marker_genes)
ad_map = tg.map_cells_to_space(
    adata_sc,
    adata_sp,
    mode='clusters',
    cluster_label='cell_type',
    device='cuda:0',
)

# Project cell-type annotations onto spatial data
tg.project_cell_annotations(ad_map, adata_sp, annotation='cell_type')
# Result stored in adata_sp.obsm['tangram_ct_pred']

# --- RCTD path (runs in R via rpy2) ---
import rpy2.robjects as ro
from rpy2.robjects import pandas2ri
pandas2ri.activate()

# Save data for R-side loading
adata_vis.write_h5ad('spatial_for_rctd.h5ad')
adata_ref.write_h5ad('reference_for_rctd.h5ad')

r_code = '''
library(spacexr)
library(Seurat)

# Load data (convert from h5ad first)
# ... R-specific loading code ...

# Create and run RCTD
rctd <- create.RCTD(puck, reference, max_cores=4)
rctd <- run_RCTD(rctd, doublet_mode='full')

# Get results
results <- rctd@results
weights <- normalize_weights(results$weights)
'''
```

## Result Extraction & Quality Evaluation

_modules: result-extraction, quality-evaluation, marker-correlation_

```python
# Extract abundances from the cell2location posterior
abundances = adata_vis.obsm['q05_cell_abundance_w_sf']
print(f'Cell types: {abundances.shape[1]}')

# Convert to proportions and assign a dominant cell type
proportions = abundances / abundances.sum(axis=1, keepdims=True)
adata_vis.obsm['cell_type_proportions'] = proportions

cell_types = adata_ref.obs['cell_type'].cat.categories
adata_vis.obs['dominant_cell_type'] = cell_types[proportions.argmax(axis=1)]

# Validate against canonical marker genes
marker_genes = {
    'T_cell': ['CD3D', 'CD3E', 'CD4', 'CD8A'],
    'Macrophage': ['CD68', 'CD14', 'CSF1R'],
    'Epithelial': ['EPCAM', 'KRT8', 'KRT18'],
}

for ct, markers in marker_genes.items():
    available_markers = [m for m in markers if m in adata_vis.var_names]
    if available_markers:
        marker_expr = adata_vis[:, available_markers].X.mean(axis=1)
        ct_idx = list(cell_types).index(ct)
        ct_prop = proportions[:, ct_idx]
        corr = np.corrcoef(marker_expr.flatten(), ct_prop)[0, 1]
        print(f'{ct}: marker-proportion correlation = {corr:.3f}')

# Compare agreement across methods (if multiple were run)
adata_vis.obsm['cell2location'] = cell2location_proportions
adata_vis.obsm['tangram'] = tangram_proportions

for ct_idx, ct in enumerate(cell_types):
    c2l = adata_vis.obsm['cell2location'][:, ct_idx]
    tg = adata_vis.obsm['tangram'][:, ct_idx]
    corr = np.corrcoef(c2l, tg)[0, 1]
    print(f'{ct}: cell2location vs tangram = {corr:.3f}')
```

## Visualization & Export

_modules: visualization, spatial-plot, export_

```python
# Spatial heatmaps of cell-type proportions
cell_types_to_plot = ['T_cell', 'Macrophage', 'Epithelial', 'Fibroblast']

fig, axes = plt.subplots(2, 2, figsize=(12, 12))
for ax, ct in zip(axes.flatten(), cell_types_to_plot):
    ct_idx = list(adata_ref.obs['cell_type'].cat.categories).index(ct)
    adata_vis.obs[f'{ct}_proportion'] = proportions[:, ct_idx]
    sc.pl.spatial(adata_vis, color=f'{ct}_proportion', ax=ax, show=False,
                  title=ct, cmap='Reds', vmin=0, vmax=1)
plt.tight_layout()
plt.savefig('cell_type_proportions.png', dpi=150)

# Optional: per-spot pie-chart overlay
from matplotlib.patches import Wedge

def plot_pie_spatial(adata, proportions, cell_types, spot_size=0.5):
    fig, ax = plt.subplots(figsize=(12, 12))
    colors = plt.cm.tab20(np.linspace(0, 1, len(cell_types)))

    coords = adata.obsm['spatial']
    for i in range(adata.n_obs):
        x, y = coords[i]
        props = proportions[i]
        start_angle = 0
        for j, prop in enumerate(props):
            if prop > 0.01:  # Skip tiny proportions
                wedge = Wedge((x, y), spot_size * 50, start_angle,
                             start_angle + prop * 360, color=colors[j])
                ax.add_patch(wedge)
                start_angle += prop * 360

    ax.set_xlim(coords[:, 0].min() - 100, coords[:, 0].max() + 100)
    ax.set_ylim(coords[:, 1].min() - 100, coords[:, 1].max() + 100)
    ax.set_aspect('equal')
    ax.invert_yaxis()

    handles = [plt.Rectangle((0, 0), 1, 1, color=colors[i]) for i in range(len(cell_types))]
    ax.legend(handles, cell_types, loc='upper right')
    plt.savefig('pie_chart_spatial.png', dpi=150)

# Export proportions and annotated AnnData
prop_df = pd.DataFrame(
    proportions,
    index=adata_vis.obs_names,
    columns=cell_types
)
prop_df.to_csv('cell_type_proportions.csv')
adata_vis.write_h5ad('spatial_deconvolved.h5ad')
```
