## Data Loading & QC

_modules: data-loading, qc, filtering_

```r
# R / Seurat
library(Seurat)
library(ggplot2)

data_dir <- 'cellranger_output/filtered_feature_bc_matrix'
counts <- Read10X(data.dir = data_dir)
seurat_obj <- CreateSeuratObject(counts = counts, project = 'my_project',
                                  min.cells = 3, min.features = 200)

# QC metrics
seurat_obj[['percent.mt']]   <- PercentageFeatureSet(seurat_obj, pattern = '^MT-')
seurat_obj[['percent.ribo']] <- PercentageFeatureSet(seurat_obj, pattern = '^RP[SL]')

# Visualize
VlnPlot(seurat_obj, features = c('nFeature_RNA', 'nCount_RNA', 'percent.mt'), ncol = 3)

# Filter cells
seurat_obj <- subset(seurat_obj,
                     nFeature_RNA > 200 &
                     nFeature_RNA < 5000 &
                     percent.mt < 20 &
                     nCount_RNA > 500)
cat('Cells after QC:', ncol(seurat_obj), '\n')
```

```python
# Python / scanpy
import scanpy as sc
import numpy as np

adata = sc.read_10x_h5('filtered_feature_bc_matrix.h5')
adata.var_names_make_unique()

# QC metrics
adata.var['mt'] = adata.var_names.str.startswith('MT-')
sc.pp.calculate_qc_metrics(adata, qc_vars=['mt'], percent_top=None, log1p=False, inplace=True)

# Filter
sc.pp.filter_cells(adata, min_genes=200)
sc.pp.filter_genes(adata, min_cells=3)
adata = adata[adata.obs.n_genes_by_counts < 5000, :]
adata = adata[adata.obs.pct_counts_mt < 20, :]
```

## Doublet Detection

_modules: doublet-detection_

```r
# R / scDblFinder
library(scDblFinder)

sce <- as.SingleCellExperiment(seurat_obj)
sce <- scDblFinder(sce)

seurat_obj$doublet_class <- sce$scDblFinder.class
seurat_obj$doublet_score <- sce$scDblFinder.score

seurat_obj <- subset(seurat_obj, doublet_class == 'singlet')
cat('Cells after doublet removal:', ncol(seurat_obj), '\n')
```

```python
# Python / scanpy (scrublet)
sc.pp.scrublet(adata)
adata = adata[~adata.obs['predicted_doublet'], :]
```

## Normalization & Feature Selection

_modules: normalization, hvg, feature-selection_

```r
# R / Seurat — SCTransform (recommended)
seurat_obj <- SCTransform(seurat_obj, vars.to.regress = 'percent.mt', verbose = FALSE)

# Alternative: standard log-normalization
seurat_obj <- NormalizeData(seurat_obj)
seurat_obj <- FindVariableFeatures(seurat_obj, selection.method = 'vst', nfeatures = 2000)
seurat_obj <- ScaleData(seurat_obj, vars.to.regress = 'percent.mt')
```

```python
# Python / scanpy
sc.pp.normalize_total(adata, target_sum=1e4)
sc.pp.log1p(adata)
sc.pp.highly_variable_genes(adata, n_top_genes=2000)
sc.pp.scale(adata, max_value=10)
```

## Dimensionality Reduction & Clustering

_modules: pca, umap, neighbors, clustering, leiden_

```r
# R / Seurat
seurat_obj <- RunPCA(seurat_obj, npcs = 50, verbose = FALSE)
ElbowPlot(seurat_obj, ndims = 50)

n_pcs <- 30  # choose based on elbow plot
seurat_obj <- RunUMAP(seurat_obj, dims = 1:n_pcs, verbose = FALSE)
seurat_obj <- FindNeighbors(seurat_obj, dims = 1:n_pcs, verbose = FALSE)
seurat_obj <- FindClusters(seurat_obj, resolution = c(0.2, 0.4, 0.6, 0.8, 1.0), verbose = FALSE)

DimPlot(seurat_obj, reduction = 'umap', group.by = 'SCT_snn_res.0.4', label = TRUE)
```

```python
# Python / scanpy
sc.tl.pca(adata, n_comps=50)
sc.pp.neighbors(adata, n_neighbors=15, n_pcs=30)
sc.tl.umap(adata)
sc.tl.leiden(adata, resolution=0.5)
```

## Marker Gene Discovery

_modules: marker-genes, differential-expression_

```r
# R / Seurat
library(dplyr)

Idents(seurat_obj) <- 'SCT_snn_res.0.4'
markers <- FindAllMarkers(seurat_obj, only.pos = TRUE, min.pct = 0.25, logfc.threshold = 0.25)

top_markers <- markers %>%
    group_by(cluster) %>%
    slice_max(n = 10, order_by = avg_log2FC)

DoHeatmap(seurat_obj, features = top_markers$gene) + NoLegend()
write.csv(markers, 'markers.csv')
```

```python
# Python / scanpy
sc.tl.rank_genes_groups(adata, 'leiden', method='wilcoxon')
sc.pl.rank_genes_groups(adata, n_genes=10, sharey=False)
```

## Cell Type Annotation

_modules: annotation, cell-type_

```r
# R / Seurat — manual annotation
cluster_annotations <- c(
    '0' = 'CD4 T cells',
    '1' = 'CD14 Monocytes',
    '2' = 'B cells',
    '3' = 'CD8 T cells',
    '4' = 'NK cells',
    '5' = 'CD16 Monocytes',
    '6' = 'Dendritic cells'
)
seurat_obj$cell_type <- cluster_annotations[as.character(Idents(seurat_obj))]

DimPlot(seurat_obj, reduction = 'umap', group.by = 'cell_type', label = TRUE)
saveRDS(seurat_obj, 'seurat_annotated.rds')
```

```python
# Python / scanpy — manual annotation
annotation = {
    '0': 'CD4 T cells',
    '1': 'CD14 Monocytes',
    '2': 'B cells',
    '3': 'CD8 T cells',
    '4': 'NK cells',
}
adata.obs['cell_type'] = adata.obs['leiden'].map(annotation)
adata.write('scanpy_annotated.h5ad')
```
