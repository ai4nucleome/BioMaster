## Validate Spatial Assets

_modules: spatial-validation, coordinate-check, barcode-alignment_

```python
import scanpy as sc
import squidpy as sq

# Load spatial data (example: Visium format)
adata = sc.read_visium('path/to/spatial/', count_file='filtered_feature_bc_matrix.h5')

# Validate coordinates exist and are non-null
assert 'spatial' in adata.obsm, 'Spatial coordinates missing from adata.obsm'
assert adata.obsm['spatial'].shape[1] == 2, 'Coordinates must be 2D (x, y)'

# Check barcode alignment between expression and spatial metadata
if 'array_row' in adata.obs.columns and 'array_col' in adata.obs.columns:
    print(f'Spot grid: {adata.obs["array_row"].nunique()} rows x {adata.obs["array_col"].nunique()} cols')

# If histology image is present, validate registration
if hasattr(adata, 'uns') and 'spatial' in adata.uns:
    for library_id in adata.uns['spatial'].keys():
        img = adata.uns['spatial'][library_id]['images']['hires']
        scalefactors = adata.uns['spatial'][library_id]['scalefactors']
        print(f'Library {library_id}: image shape {img.shape}, scalefactor {scalefactors["tissue_hires_scalef"]}')

print('Spatial assets validated successfully')
```

## Preprocess Expression and Spatial Structure

_modules: qc, normalization, hvg-selection, spatial-neighbors_

```python
import scanpy as sc
import squidpy as sq

# Filter low-quality spots
sc.pp.filter_cells(adata, min_genes=200)
sc.pp.filter_genes(adata, min_cells=3)

# Filter mitochondrial and ribosomal genes if desired
adata.var['mt'] = adata.var_names.str.startswith('MT-')
sc.pp.calculate_qc_metrics(adata, qc_vars=['mt'], percent_top=None, log1p=False, inplace=True)

# Filter spots with high mitochondrial content
adata = adata[adata.obs.pct_counts_mt < 20, :].copy()

# Normalization
sc.pp.normalize_total(adata, target_sum=1e4)
sc.pp.log1p(adata)

# Identify highly variable genes
sc.pp.highly_variable_genes(adata, n_top_genes=2000, batch_key=None)
adata = adata[:, adata.var.highly_variable].copy()

# Scale data
sc.pp.scale(adata, max_value=10)

# Build spatial neighbor graph using physical coordinates
sq.gr.spatial_neighbors(adata, coord_type='grid', n_neighs=6)
# For non-grid based data (e.g. MERFISH, Xenium):
# sq.gr.spatial_neighbors(adata, coord_type='generic', n_neighs=10, radius=50.0)

print(f'Preprocessed: {adata.n_obs} spots, {adata.n_vars} genes')
```

## Domain Detection

_modules: pca, leiden, domain-detection, spatial-autocorrelation, marker-genes_

```python
import scanpy as sc
import squidpy as sq

# PCA for dimensionality reduction
sc.tl.pca(adata, n_comps=50, svd_solver='arpack')

# Compute neighbors on PCA (for clustering)
sc.pp.neighbors(adata, n_neighbors=15, n_pcs=30)

# Leiden clustering for domain detection
sc.tl.leiden(adata, resolution=0.8, key_added='spatial_domains')

# Spatial autocorrelation (Moran's I) to find domain-marker genes
sq.gr.spatial_autocorr(
    adata,
    mode='moran',
    n_perms=100,
    n_jobs=1,
    attr='obs',
    layer=None
)

# Rank genes per domain
sc.tl.rank_genes_groups(adata, groupby='spatial_domains', method='wilcoxon')

print(f'Detected {adata.obs["spatial_domains"].nunique()} spatial domains')
print(adata.obs['spatial_domains'].value_counts())
```

## Deconvolution

_modules: deconvolution, cell-type-scoring, spatial-regression_

```python
import scanpy as sc
import squidpy as sq

# Option A: Marker-based cell-type enrichment scoring
# Requires a dictionary of cell-type marker genes
if 'cell_type_markers' in locals() or 'cell_type_markers' in globals():
    for ct_name, ct_genes in cell_type_markers.items():
        ct_genes = [g for g in ct_genes if g in adata.var_names]
        if len(ct_genes) > 0:
            sc.tl.score_genes(adata, gene_list=ct_genes, score_name=f'{ct_name}_score')

# Option B: Squidpy's deconvolution with a single-cell reference
# sq.gr.deconvolve(adata, reference_adata, source='cell2location', ...)

# Option C: Spatial regression (e.g. spatial DE)
# sq.gr.spatial_de(adata, cluster_key='spatial_domains')

print('Deconvolution complete. Cell-type scores added to adata.obs.')
```

## Neighborhood and Communication Analysis

_modules: neighborhood-enrichment, interaction-matrix, ripley, ligand-receptor_

```python
import squidpy as sq

# Neighborhood enrichment between spatial domains
sq.gr.nhood_enrichment(
    adata,
    cluster_key='spatial_domains',
    n_perms=1000,
    n_jobs=1
)

# Interaction matrix (co-occurrence)
sq.gr.interaction_matrix(adata, cluster_key='spatial_domains')

# Ripley's statistics for spatial dispersion
sq.gr.ripley(adata, cluster_key='spatial_domains', mode='F')

# Optional: Ligand-receptor analysis (requires a ligand-receptor database)
# sq.gr.ligrec(adata, cluster_key='spatial_domains', ...)

print('Neighborhood analysis complete.')
```

## Visualize Spatial Biology

_modules: spatial-plotting, visualization, publication-figures_

```python
import scanpy as sc
import matplotlib.pyplot as plt

# Spatial scatter plot of domains
sc.pl.spatial(
    adata,
    color='spatial_domains',
    title='Spatial Domains',
    spot_size=1.5,
    show=False,
    save='spatial_domains.png'
)

# Spatial plot of gene expression
sc.pl.spatial(
    adata,
    color='CD3E',  # example gene
    title='CD3E Expression',
    spot_size=1.5,
    cmap='viridis',
    show=False,
    save='gene_expression.png'
)

# Multi-panel figure
fig, axes = plt.subplots(1, 3, figsize=(18, 6))
for idx, (color, title) in enumerate([
    ('spatial_domains', 'Domains'),
    ('n_genes_by_counts', 'Gene Count'),
    ('total_counts', 'UMI Count')
]):
    sc.pl.spatial(
        adata,
        color=color,
        title=title,
        spot_size=1.5,
        ax=axes[idx],
        show=False
    )
plt.tight_layout()
plt.savefig('figures/spatial_overview.png', dpi=150, bbox_inches='tight')
plt.show()
```

## Export Interpretable Artifacts

_modules: export, save-results, csv-output, h5ad_

```python
import pandas as pd
import os

os.makedirs('results', exist_ok=True)
os.makedirs('figures', exist_ok=True)
os.makedirs('qc', exist_ok=True)

# Export domain assignments
adata.obs[['spatial_domains']].to_csv('results/spatial_domains.csv')

# Export coordinates with domain labels
coords_df = pd.DataFrame(
    adata.obsm['spatial'],
    index=adata.obs_names,
    columns=['x', 'y']
)
coords_df['spatial_domain'] = adata.obs['spatial_domains'].values
coords_df.to_csv('results/spatial_coordinates_with_domains.csv')

# Export deconvolution scores if present
score_cols = [c for c in adata.obs.columns if c.endswith('_score')]
if score_cols:
    adata.obs[score_cols].to_csv('results/cell_type_scores.csv')

# Save full AnnData object
adata.write('results/spatial_annotated.h5ad')

print('Artifacts exported to results/, figures/, and qc/ directories.')
```
