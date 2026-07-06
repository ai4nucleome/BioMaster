## QC Metrics and Visualization

_modules: qc, qc-metrics, visualization_

```python
import scanpy as sc
import matplotlib.pyplot as plt

# Flag mitochondrial genes (human: MT- prefix; adjust prefix for other species)
adata.var['mt'] = adata.var_names.str.startswith('MT-')

# Compute QC metrics; adds n_genes_by_counts, total_counts, pct_counts_mt to adata.obs
sc.pp.calculate_qc_metrics(adata, qc_vars=['mt'], percent_top=None, log1p=False, inplace=True)

# Visualize distributions and pairwise relationships
sc.pl.violin(adata, ['n_genes_by_counts', 'total_counts', 'pct_counts_mt'], jitter=0.4, multi_panel=True)
sc.pl.scatter(adata, x='total_counts', y='pct_counts_mt')
sc.pl.scatter(adata, x='total_counts', y='n_genes_by_counts')
```

```r
library(Seurat)
library(ggplot2)

# Compute mitochondrial percentage and add to metadata
seurat_obj[['percent.mt']] <- PercentageFeatureSet(seurat_obj, pattern = '^MT-')
head(seurat_obj@meta.data)

# Violin and scatter plots of QC metrics
VlnPlot(seurat_obj, features = c('nFeature_RNA', 'nCount_RNA', 'percent.mt'), ncol = 3)
plot1 <- FeatureScatter(seurat_obj, feature1 = 'nCount_RNA', feature2 = 'percent.mt')
plot2 <- FeatureScatter(seurat_obj, feature1 = 'nCount_RNA', feature2 = 'nFeature_RNA')
plot1 + plot2
```

## Filtering

_modules: filtering, qc_

```python
# Filter cells by gene count and mitochondrial percentage
sc.pp.filter_cells(adata, min_genes=200)
sc.pp.filter_cells(adata, max_genes=5000)
adata = adata[adata.obs['pct_counts_mt'] < 20, :].copy()

# Filter genes detected in too few cells
sc.pp.filter_genes(adata, min_cells=3)
print(f'After filtering: {adata.n_obs} cells, {adata.n_vars} genes')

# Preserve raw counts before normalization
adata.raw = adata.copy()
adata.layers['counts'] = adata.X.copy()
```

```r
# Filter cells by gene count and mitochondrial percentage
seurat_obj <- subset(seurat_obj,
    subset = nFeature_RNA > 200 &
             nFeature_RNA < 5000 &
             percent.mt < 20)
cat('After filtering:', ncol(seurat_obj), 'cells\n')
```

## Normalization

_modules: normalization, log-transform, sctransform_

```python
# Library-size normalize to 10,000 counts per cell, then log-transform
sc.pp.normalize_total(adata, target_sum=1e4)
sc.pp.log1p(adata)
```

```r
# Standard log normalization
seurat_obj <- NormalizeData(seurat_obj,
    normalization.method = 'LogNormalize',
    scale.factor = 10000)

# Alternative: SCTransform (recommended; jointly normalizes, selects HVGs, and scales)
# seurat_obj <- SCTransform(seurat_obj, vars.to.regress = 'percent.mt', verbose = FALSE)
```

## Highly Variable Gene Selection

_modules: hvg, feature-selection_

```python
# Identify highly variable genes (seurat_v3 works on raw counts)
sc.pp.highly_variable_genes(adata, n_top_genes=2000, flavor='seurat_v3', layer='counts')
sc.pl.highly_variable_genes(adata)
print(f'Highly variable genes: {adata.var.highly_variable.sum()}')

# Optional: subset to HVGs for downstream analysis
adata_hvg = adata[:, adata.var.highly_variable].copy()
```

```r
# Identify highly variable features (skip if using SCTransform)
seurat_obj <- FindVariableFeatures(seurat_obj, selection.method = 'vst', nfeatures = 2000)

top10 <- head(VariableFeatures(seurat_obj), 10)
plot1 <- VariableFeaturePlot(seurat_obj)
plot2 <- LabelPoints(plot = plot1, points = top10, repel = TRUE)
plot2
```

## Scaling and Confounder Regression

_modules: scaling, regress-out_

```python
# Optional: regress out confounders before scaling
sc.pp.regress_out(adata, ['total_counts', 'pct_counts_mt'])

# Scale to unit variance, zero mean; clip extreme values
sc.pp.scale(adata, max_value=10)
```

```r
# Scale all genes (or only variable features for speed)
seurat_obj <- ScaleData(seurat_obj)

# Or scale all genes explicitly
# all.genes <- rownames(seurat_obj)
# seurat_obj <- ScaleData(seurat_obj, features = all.genes)

# Regress out confounders during scaling
# seurat_obj <- ScaleData(seurat_obj, vars.to.regress = c('percent.mt', 'nCount_RNA'))
```
