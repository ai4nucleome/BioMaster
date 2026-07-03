## api_reference.md

# Scanpy API Quick Reference

Quick reference for commonly used scanpy functions organized by module.

## Import Convention

```python
import scanpy as sc
```

## Reading and Writing Data (sc.read_*)

### Reading Functions

```python
sc.read_10x_h5(filename)                    # Read 10X HDF5 file
sc.read_10x_mtx(path)                       # Read 10X mtx directory
sc.read_h5ad(filename)                      # Read h5ad (AnnData) file
sc.read_csv(filename)                       # Read CSV file
sc.read_excel(filename)                     # Read Excel file
sc.read_loom(filename)                      # Read loom file
sc.read_text(filename)                      # Read text file
sc.read_visium(path)                        # Read Visium spatial data
```

### Writing Functions

```python
adata.write_h5ad(filename)                  # Write to h5ad format
adata.write_csvs(dirname)                   # Write to CSV files
adata.write_loom(filename)                  # Write to loom format
adata.write_zarr(filename)                  # Write to zarr format
```

## Preprocessing (sc.pp.*)

### Quality Control

```python
sc.pp.calculate_qc_metrics(adata, qc_vars=['mt'], inplace=True)
sc.pp.filter_cells(adata, min_genes=200)
sc.pp.filter_genes(adata, min_cells=3)
```

### Normalization and Transformation

```python
sc.pp.normalize_total(adata, target_sum=1e4)    # Normalize to target sum
sc.pp.log1p(adata)                               # Log(x + 1) transformation
sc.pp.sqrt(adata)                                # Square root transformation
```

### Feature Selection

```python
sc.pp.highly_variable_genes(adata, min_mean=0.0125, max_mean=3, min_disp=0.5)
sc.pp.highly_variable_genes(adata, flavor='seurat_v3', n_top_genes=2000)
```

### Scaling and Regression

```python
sc.pp.scale(adata, max_value=10)                      # Scale to unit variance
sc.pp.regress_out(adata, ['total_counts', 'pct_counts_mt'])  # Regress out unwanted variation
```

### Dimensionality Reduction (Preprocessing)

```python
sc.pp.pca(adata, n_comps=50)                     # Principal component analysis
sc.pp.neighbors(adata, n_neighbors=10, n_pcs=40) # Compute neighborhood graph
```

### Batch Correction

```python
sc.pp.combat(adata, key='batch')                 # ComBat batch correction
```

## Tools (sc.tl.*)

### Dimensionality Reduction

```python
sc.tl.pca(adata, svd_solver='arpack')            # PCA
sc.tl.umap(adata)                                 # UMAP embedding
sc.tl.tsne(adata)                                 # t-SNE embedding
sc.tl.diffmap(adata)                              # Diffusion map
sc.tl.draw_graph(adata, layout='fa')             # Force-directed graph
```

### Clustering

```python
sc.tl.leiden(adata, resolution=0.5)              # Leiden clustering (recommended)
sc.tl.louvain(adata, resolution=0.5)             # Louvain clustering
sc.tl.kmeans(adata, n_clusters=10)               # K-means clustering
```

### Marker Genes and Differential Expression

```python
sc.tl.rank_genes_groups(adata, groupby='leiden', method='wilcoxon')
sc.tl.rank_genes_groups(adata, groupby='leiden', method='t-test')
sc.tl.rank_genes_groups(adata, groupby='leiden', method='logreg')

# Get results as dataframe
sc.get.rank_genes_groups_df(adata, group='0')
```

### Trajectory Inference

```python
sc.tl.paga(adata, groups='leiden')               # PAGA trajectory
sc.tl.dpt(adata)                                  # Diffusion pseudotime
```

### Gene Scoring

```python
sc.tl.score_genes(adata, gene_list, score_name='score')
sc.tl.score_genes_cell_cycle(adata, s_genes, g2m_genes)
```

### Embeddings and Projections

```python
sc.tl.ingest(adata, adata_ref)                   # Map to reference
sc.tl.embedding_density(adata, basis='umap', groupby='leiden')
```

## Plotting (sc.pl.*)

### Basic Embeddings

```python
sc.pl.umap(adata, color='leiden')                # UMAP plot
sc.pl.tsne(adata, color='gene_name')             # t-SNE plot
sc.pl.pca(adata, color='leiden')                 # PCA plot
sc.pl.diffmap(adata, color='leiden')             # Diffusion map plot
```

### Heatmaps and Dot Plots

```python
sc.pl.heatmap(adata, var_names=genes, groupby='leiden')
sc.pl.dotplot(adata, var_names=genes, groupby='leiden')
sc.pl.matrixplot(adata, var_names=genes, groupby='leiden')
sc.pl.stacked_violin(adata, var_names=genes, groupby='leiden')
```

### Violin and Scatter Plots

```python
sc.pl.violin(adata, keys=['gene1', 'gene2'], groupby='leiden')
sc.pl.scatter(adata, x='gene1', y='gene2', color='leiden')
```

### Marker Gene Visualization

```python
sc.pl.rank_genes_groups(adata, n_genes=25, sharey=False)
sc.pl.rank_genes_groups_violin(adata, groups='0')
sc.pl.rank_genes_groups_heatmap(adata, n_genes=10)
sc.pl.rank_genes_groups_dotplot(adata, n_genes=5)
```

### Trajectory Visualization

```python
sc.pl.paga(adata, color='leiden')                # PAGA graph
sc.pl.dpt_timeseries(adata)                      # DPT timeseries
```

### QC Plots

```python
sc.pl.highest_expr_genes(adata, n_top=20)
sc.pl.violin(adata, ['n_genes_by_counts', 'total_counts', 'pct_counts_mt'])
sc.pl.scatter(adata, x='total_counts', y='n_genes_by_counts')
```

### Advanced Plots

```python
sc.pl.dendrogram(adata, groupby='leiden')
sc.pl.correlation_matrix(adata, groupby='leiden')
sc.pl.tracksplot(adata, var_names=genes, groupby='leiden')
```

## Common Parameters

### Color Parameters
- `color`: Variable(s) to color by (gene name, obs column)
- `use_raw`: Use `.raw` attribute of adata
- `palette`: Color palette to use
- `vmin`, `vmax`: Color scale limits

### Layout Parameters
- `basis`: Embedding basis ('umap', 'tsne', 'pca', etc.)
- `legend_loc`: Legend location ('on data', 'right margin', etc.)
- `size`: Point size
- `alpha`: Point transparency

### Saving Parameters
- `save`: Filename to save plot
- `show`: Whether to show plot

## AnnData Structure

```python
adata.X                    # Expression matrix (cells × genes)
adata.obs                  # Cell annotations (DataFrame)
adata.var                  # Gene annotations (DataFrame)
adata.uns                  # Unstructured annotations (dict)
adata.obsm                 # Multi-dimensional cell annotations (e.g., PCA, UMAP)
adata.varm                 # Multi-dimensional gene annotations
adata.layers               # Additional data layers
adata.raw                  # Raw data backup

# Access
adata.obs_names            # Cell barcodes
adata.var_names            # Gene names
adata.shape                # (n_cells, n_genes)

# Slicing
adata[cell_indices, gene_indices]
adata[:, adata.var_names.isin(gene_list)]
adata[adata.obs['leiden'] == '0', :]
```

## Settings

```python
sc.settings.verbosity = 3              # 0=error, 1=warning, 2=info, 3=hint
sc.settings.set_figure_params(dpi=80, facecolor='white')
sc.settings.autoshow = False           # Don't show plots automatically
sc.settings.autosave = True            # Autosave figures
sc.settings.figdir = './figures/'      # Figure directory
sc.settings.cachedir = './cache/'      # Cache directory
sc.settings.n_jobs = 8                 # Number of parallel jobs
```

## Useful Utilities

```python
sc.logging.print_versions()            # Print version information
sc.logging.print_memory_usage()        # Print memory usage
adata.copy()                           # Create a copy of AnnData object
adata.concatenate([adata1, adata2])    # Concatenate AnnData objects
```

---

## plotting_guide.md

# Scanpy Plotting Guide

Comprehensive guide for creating publication-quality visualizations with scanpy.

## General Plotting Principles

All scanpy plotting functions follow consistent patterns:
- Functions in `sc.pl.*` mirror analysis functions in `sc.tl.*`
- Most accept `color` parameter for gene names or metadata columns
- Results are saved via `save` parameter
- Multiple plots can be generated in a single call

## Essential Quality Control Plots

### Visualize QC Metrics

```python
# Violin plots for QC metrics
sc.pl.violin(adata, ['n_genes_by_counts', 'total_counts', 'pct_counts_mt'],
             jitter=0.4, multi_panel=True, save='_qc_violin.pdf')

# Scatter plots to identify outliers
sc.pl.scatter(adata, x='total_counts', y='pct_counts_mt', save='_qc_mt.pdf')
sc.pl.scatter(adata, x='total_counts', y='n_genes_by_counts', save='_qc_genes.pdf')

# Highest expressing genes
sc.pl.highest_expr_genes(adata, n_top=20, save='_highest_expr.pdf')
```

### Post-filtering QC

```python
# Compare before and after filtering
sc.pl.violin(adata, ['n_genes_by_counts', 'total_counts'],
             groupby='sample', save='_post_filter.pdf')
```

## Dimensionality Reduction Visualizations

### PCA Plots

```python
# Basic PCA
sc.pl.pca(adata, color='leiden', save='_pca.pdf')

# PCA colored by gene expression
sc.pl.pca(adata, color=['gene1', 'gene2', 'gene3'], save='_pca_genes.pdf')

# Variance ratio plot (elbow plot)
sc.pl.pca_variance_ratio(adata, log=True, n_pcs=50, save='_variance.pdf')

# PCA loadings
sc.pl.pca_loadings(adata, components=[1, 2, 3], save='_loadings.pdf')
```

### UMAP Plots

```python
# Basic UMAP with clusters
sc.pl.umap(adata, color='leiden', legend_loc='on data', save='_umap_leiden.pdf')

# UMAP colored by multiple variables
sc.pl.umap(adata, color=['leiden', 'cell_type', 'batch'],
           save='_umap_multi.pdf')

# UMAP with gene expression
sc.pl.umap(adata, color=['CD3D', 'CD14', 'MS4A1'],
           use_raw=False, save='_umap_genes.pdf')

# Customize appearance
sc.pl.umap(adata, color='leiden',
           palette='Set2',
           size=50,
           alpha=0.8,
           frameon=False,
           title='Cell Types',
           save='_umap_custom.pdf')
```

### t-SNE Plots

```python
# t-SNE with clusters
sc.pl.tsne(adata, color='leiden', legend_loc='right margin', save='_tsne.pdf')

# Multiple t-SNE perplexities (if computed)
sc.pl.tsne(adata, color='leiden', save='_tsne_default.pdf')
```

## Clustering Visualizations

### Basic Cluster Plots

```python
# UMAP with cluster annotations
sc.pl.umap(adata, color='leiden', add_outline=True,
           legend_loc='on data', legend_fontsize=12,
           legend_fontoutline=2, frameon=False,
           save='_clusters.pdf')

# Show cluster proportions
sc.pl.umap(adata, color='leiden', size=50, edges=True,
           edges_width=0.1, save='_clusters_edges.pdf')
```

### Cluster Comparison

```python
# Compare clustering results
sc.pl.umap(adata, color=['leiden', 'louvain'],
           save='_cluster_comparison.pdf')

# Cluster dendrogram
sc.tl.dendrogram(adata, groupby='leiden')
sc.pl.dendrogram(adata, groupby='leiden', save='_dendrogram.pdf')
```

## Marker Gene Visualizations

### Ranked Marker Genes

```python
# Overview of top markers per cluster
sc.pl.rank_genes_groups(adata, n_genes=25, sharey=False,
                        save='_marker_overview.pdf')

# Heatmap of top markers
sc.pl.rank_genes_groups_heatmap(adata, n_genes=10, groupby='leiden',
                                 show_gene_labels=True,
                                 save='_marker_heatmap.pdf')

# Dot plot of markers
sc.pl.rank_genes_groups_dotplot(adata, n_genes=5,
                                 save='_marker_dotplot.pdf')

# Stacked violin plots
sc.pl.rank_genes_groups_stacked_violin(adata, n_genes=5,
                                        save='_marker_violin.pdf')

# Matrix plot
sc.pl.rank_genes_groups_matrixplot(adata, n_genes=5,
                                    save='_marker_matrix.pdf')
```

### Specific Gene Expression

```python
# Violin plots for specific genes
marker_genes = ['CD3D', 'CD14', 'MS4A1', 'NKG7', 'FCGR3A']
sc.pl.violin(adata, keys=marker_genes, groupby='leiden',
             save='_markers_violin.pdf')

# Dot plot for curated markers
sc.pl.dotplot(adata, var_names=marker_genes, groupby='leiden',
              save='_markers_dotplot.pdf')

# Heatmap for specific genes
sc.pl.heatmap(adata, var_names=marker_genes, groupby='leiden',
              swap_axes=True, save='_markers_heatmap.pdf')

# Stacked violin for gene sets
sc.pl.stacked_violin(adata, var_names=marker_genes, groupby='leiden',
                     save='_markers_stacked.pdf')
```

### Gene Expression on Embeddings

```python
# Multiple genes on UMAP
genes = ['CD3D', 'CD14', 'MS4A1', 'NKG7']
sc.pl.umap(adata, color=genes, cmap='viridis',
           save='_umap_markers.pdf')

# Gene expression with custom colormap
sc.pl.umap(adata, color='CD3D', cmap='Reds',
           vmin=0, vmax=3, save='_umap_cd3d.pdf')
```

## Trajectory and Pseudotime Visualizations

### PAGA Plots

```python
# PAGA graph
sc.pl.paga(adata, color='leiden', save='_paga.pdf')

# PAGA with gene expression
sc.pl.paga(adata, color=['leiden', 'dpt_pseudotime'],
           save='_paga_pseudotime.pdf')

# PAGA overlaid on UMAP
sc.pl.umap(adata, color='leiden', save='_umap_with_paga.pdf',
           edges=True, edges_color='gray')
```

### Pseudotime Plots

```python
# DPT pseudotime on UMAP
sc.pl.umap(adata, color='dpt_pseudotime', save='_umap_dpt.pdf')

# Gene expression along pseudotime
sc.pl.dpt_timeseries(adata, save='_dpt_timeseries.pdf')

# Heatmap ordered by pseudotime
sc.pl.heatmap(adata, var_names=genes, groupby='leiden',
              use_raw=False, show_gene_labels=True,
              save='_pseudotime_heatmap.pdf')
```

## Advanced Visualizations

### Tracks Plot (Gene Expression Trends)

```python
# Show gene expression across cell types
sc.pl.tracksplot(adata, var_names=marker_genes, groupby='leiden',
                 save='_tracks.pdf')
```

### Correlation Matrix

```python
# Correlation between clusters
sc.pl.correlation_matrix(adata, groupby='leiden',
                         save='_correlation.pdf')
```

### Embedding Density

```python
# Cell density on UMAP
sc.tl.embedding_density(adata, basis='umap', groupby='cell_type')
sc.pl.embedding_density(adata, basis='umap', key='umap_density_cell_type',
                        save='_density.pdf')
```

## Multi-Panel Figures

### Creating Panel Figures

```python
import matplotlib.pyplot as plt

# Create multi-panel figure
fig, axes = plt.subplots(2, 2, figsize=(12, 12))

# Plot on specific axes
sc.pl.umap(adata, color='leiden', ax=axes[0, 0], show=False)
sc.pl.umap(adata, color='CD3D', ax=axes[0, 1], show=False)
sc.pl.umap(adata, color='CD14', ax=axes[1, 0], show=False)
sc.pl.umap(adata, color='MS4A1', ax=axes[1, 1], show=False)

plt.tight_layout()
plt.savefig('figures/multi_panel.pdf')
plt.show()
```

## Publication-Quality Customization

### High-Quality Settings

```python
# Set publication-quality defaults
sc.settings.set_figure_params(dpi=300, frameon=False, figsize=(5, 5),
                               facecolor='white')

# Vector graphics output
sc.settings.figdir = './figures/'
sc.settings.file_format_figs = 'pdf'  # or 'svg'
```

### Custom Color Palettes

```python
# Use custom colors
custom_colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']
sc.pl.umap(adata, color='leiden', palette=custom_colors,
           save='_custom_colors.pdf')

# Continuous color maps
sc.pl.umap(adata, color='CD3D', cmap='viridis', save='_viridis.pdf')
sc.pl.umap(adata, color='CD3D', cmap='RdBu_r', save='_rdbu.pdf')
```

### Remove Axes and Frames

```python
# Clean plot without axes
sc.pl.umap(adata, color='leiden', frameon=False,
           save='_clean.pdf')

# No legend
sc.pl.umap(adata, color='leiden', legend_loc=None,
           save='_no_legend.pdf')
```

## Exporting Plots

### Save Individual Plots

```python
# Automatic saving with save parameter
sc.pl.umap(adata, color='leiden', save='_leiden.pdf')
# Saves to: sc.settings.figdir + 'umap_leiden.pdf'

# Manual saving
import matplotlib.pyplot as plt
fig = sc.pl.umap(adata, color='leiden', show=False, return_fig=True)
fig.savefig('figures/my_umap.pdf', dpi=300, bbox_inches='tight')
```

### Batch Export

```python
# Save multiple versions
for gene in ['CD3D', 'CD14', 'MS4A1']:
    sc.pl.umap(adata, color=gene, save=f'_{gene}.pdf')
```

## Common Customization Parameters

### Layout Parameters
- `figsize`: Figure size (width, height)
- `frameon`: Show frame around plot
- `title`: Plot title
- `legend_loc`: 'right margin', 'on data', 'best', or None
- `legend_fontsize`: Font size for legend
- `size`: Point size

### Color Parameters
- `color`: Variable(s) to color by
- `palette`: Color palette (e.g., 'Set1', 'viridis')
- `cmap`: Colormap for continuous variables
- `vmin`, `vmax`: Color scale limits
- `use_raw`: Use raw counts for gene expression

### Saving Parameters
- `save`: Filename suffix for saving
- `show`: Whether to display plot
- `dpi`: Resolution for raster formats

## Tips for Publication Figures

1. **Use vector formats**: PDF or SVG for scalable graphics
2. **High DPI**: Set dpi=300 or higher for raster images
3. **Consistent styling**: Use the same color palette across figures
4. **Clear labels**: Ensure gene names and cell types are readable
5. **White background**: Use `facecolor='white'` for publications
6. **Remove clutter**: Set `frameon=False` for cleaner appearance
7. **Legend placement**: Use 'on data' for compact figures
8. **Color blind friendly**: Consider palettes like 'colorblind' or 'Set2'

---

## standard_workflow.md

# Standard Scanpy Workflow for Single-Cell Analysis

This document outlines the standard workflow for analyzing single-cell RNA-seq data using scanpy.

## Complete Analysis Pipeline

### 1. Data Loading and Initial Setup

```python
import scanpy as sc
import pandas as pd
import numpy as np

# Configure scanpy settings
sc.settings.verbosity = 3  # verbosity: errors (0), warnings (1), info (2), hints (3)
sc.settings.set_figure_params(dpi=80, facecolor='white')

# Load data (various formats)
adata = sc.read_10x_mtx('path/to/data/')  # For 10X data
# adata = sc.read_h5ad('path/to/data.h5ad')  # For h5ad format
# adata = sc.read_csv('path/to/data.csv')  # For CSV format
```

### 2. Quality Control (QC)

```python
# Calculate QC metrics
sc.pp.calculate_qc_metrics(adata, qc_vars=['mt'], percent_top=None, log1p=False, inplace=True)

# Common filtering thresholds (adjust based on dataset)
sc.pp.filter_cells(adata, min_genes=200)
sc.pp.filter_genes(adata, min_cells=3)

# Remove cells with high mitochondrial content
adata = adata[adata.obs.pct_counts_mt < 5, :]

# Visualize QC metrics
sc.pl.violin(adata, ['n_genes_by_counts', 'total_counts', 'pct_counts_mt'],
             jitter=0.4, multi_panel=True)
sc.pl.scatter(adata, x='total_counts', y='pct_counts_mt')
sc.pl.scatter(adata, x='total_counts', y='n_genes_by_counts')
```

### 3. Normalization

```python
# Normalize to 10,000 counts per cell
sc.pp.normalize_total(adata, target_sum=1e4)

# Log-transform the data
sc.pp.log1p(adata)

# Store normalized data in raw for later use
adata.raw = adata
```

### 4. Feature Selection

```python
# Identify highly variable genes
sc.pp.highly_variable_genes(adata, min_mean=0.0125, max_mean=3, min_disp=0.5)

# Visualize highly variable genes
sc.pl.highly_variable_genes(adata)

# Subset to highly variable genes
adata = adata[:, adata.var.highly_variable]
```

### 5. Scaling and Regression

```python
# Regress out effects of total counts per cell and percent mitochondrial genes
sc.pp.regress_out(adata, ['total_counts', 'pct_counts_mt'])

# Scale data to unit variance and zero mean
sc.pp.scale(adata, max_value=10)
```

### 6. Dimensionality Reduction

```python
# Principal Component Analysis (PCA)
sc.tl.pca(adata, svd_solver='arpack')

# Visualize PCA results
sc.pl.pca(adata, color='CST3')
sc.pl.pca_variance_ratio(adata, log=True)

# Computing neighborhood graph
sc.pp.neighbors(adata, n_neighbors=10, n_pcs=40)

# UMAP for visualization
sc.tl.umap(adata)

# t-SNE (alternative to UMAP)
# sc.tl.tsne(adata)
```

### 7. Clustering

```python
# Leiden clustering (recommended)
sc.tl.leiden(adata, resolution=0.5)

# Alternative: Louvain clustering
# sc.tl.louvain(adata, resolution=0.5)

# Visualize clustering results
sc.pl.umap(adata, color=['leiden'], legend_loc='on data')
```

### 8. Marker Gene Identification

```python
# Find marker genes for each cluster
sc.tl.rank_genes_groups(adata, 'leiden', method='wilcoxon')

# Visualize top marker genes
sc.pl.rank_genes_groups(adata, n_genes=25, sharey=False)

# Get marker gene dataframe
marker_genes = sc.get.rank_genes_groups_df(adata, group='0')

# Visualize specific markers
sc.pl.umap(adata, color=['leiden', 'CST3', 'NKG7'])
```

### 9. Cell Type Annotation

```python
# Manual annotation based on marker genes
cluster_annotations = {
    '0': 'CD4 T cells',
    '1': 'CD14+ Monocytes',
    '2': 'B cells',
    '3': 'CD8 T cells',
    # ... add more annotations
}
adata.obs['cell_type'] = adata.obs['leiden'].map(cluster_annotations)

# Visualize annotated cell types
sc.pl.umap(adata, color='cell_type', legend_loc='on data')
```

### 10. Saving Results

```python
# Save the processed AnnData object
adata.write('results/processed_data.h5ad')

# Export results to CSV
adata.obs.to_csv('results/cell_metadata.csv')
adata.var.to_csv('results/gene_metadata.csv')
```

## Additional Analysis Options

### Trajectory Inference

```python
# PAGA (Partition-based graph abstraction)
sc.tl.paga(adata, groups='leiden')
sc.pl.paga(adata, color=['leiden'])

# Diffusion pseudotime (DPT)
adata.uns['iroot'] = np.flatnonzero(adata.obs['leiden'] == '0')[0]
sc.tl.dpt(adata)
sc.pl.umap(adata, color=['dpt_pseudotime'])
```

### Differential Expression Between Conditions

```python
# Compare conditions within a cell type
sc.tl.rank_genes_groups(adata, groupby='condition', groups=['treated'],
                         reference='control', method='wilcoxon')
sc.pl.rank_genes_groups(adata, groups=['treated'])
```

### Gene Set Scoring

```python
# Score cells for gene set expression
gene_set = ['CD3D', 'CD3E', 'CD3G']
sc.tl.score_genes(adata, gene_set, score_name='T_cell_score')
sc.pl.umap(adata, color='T_cell_score')
```

## Common Parameters to Adjust

- **QC thresholds**: `min_genes`, `min_cells`, `pct_counts_mt` - depends on dataset quality
- **Normalization target**: Usually 1e4, but can be adjusted
- **HVG parameters**: Affects feature selection stringency
- **PCA components**: Check variance ratio plot to determine optimal number
- **Clustering resolution**: Higher values give more clusters (typically 0.4-1.2)
- **n_neighbors**: Affects granularity of UMAP and clustering (typically 10-30)

## Best Practices

1. Always visualize QC metrics before filtering
2. Save raw counts before normalization (`adata.raw = adata`)
3. Use Leiden instead of Louvain for clustering (more efficient)
4. Try multiple clustering resolutions to find optimal granularity
5. Validate cell type annotations with known marker genes
6. Save intermediate results at key steps
