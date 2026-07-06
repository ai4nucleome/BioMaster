## Dimensionality Reduction (PCA)

_modules: pca, dimensionality-reduction_

```python
# Scanpy (Python)
import scanpy as sc
import matplotlib.pyplot as plt

# Run PCA on highly variable features
sc.tl.pca(adata, n_comps=50, svd_solver='arpack')

# Inspect variance explained (elbow) to choose n_pcs
sc.pl.pca_variance_ratio(adata, n_pcs=50, log=True)

# Visualize PCA colored by a QC metric
sc.pl.pca(adata, color='n_genes_by_counts')

# Choose number of PCs to carry forward (typically 10-50)
n_pcs = 30
```

```r
# Seurat (R)
library(Seurat)
library(ggplot2)

# Run PCA on variable features
seurat_obj <- RunPCA(seurat_obj, features = VariableFeatures(seurat_obj), npcs = 50)

# Visualize PCA
DimPlot(seurat_obj, reduction = 'pca')
VizDimLoadings(seurat_obj, dims = 1:2, reduction = 'pca')
DimHeatmap(seurat_obj, dims = 1:6, cells = 500, balanced = TRUE)

# Elbow plot to choose number of PCs
ElbowPlot(seurat_obj, ndims = 50)

# Optional: JackStraw (more rigorous but slower)
seurat_obj <- JackStraw(seurat_obj, num.replicate = 100)
seurat_obj <- ScoreJackStraw(seurat_obj, dims = 1:20)
JackStrawPlot(seurat_obj, dims = 1:20)
```

## Neighbor Graph Construction

_modules: neighbors, knn-graph_

```python
# Scanpy (Python)
# Build k-nearest neighbor graph on the first n_pcs principal components
sc.pp.neighbors(adata, n_neighbors=15, n_pcs=30)
```

```r
# Seurat (R)
# Build SNN/KNN graph on the first 30 PCs
seurat_obj <- FindNeighbors(seurat_obj, dims = 1:30)
```

## Clustering

_modules: leiden, louvain, clustering, resolution_

```python
# Scanpy (Python)
# Leiden clustering (preferred over Louvain)
sc.tl.leiden(adata, resolution=0.5)

# View cluster sizes
adata.obs['leiden'].value_counts()

# Alternative: Louvain clustering
# sc.tl.louvain(adata, resolution=0.5)

# Sweep multiple resolutions to compare granularity
for res in [0.2, 0.5, 0.8, 1.0, 1.5]:
    sc.tl.leiden(adata, resolution=res, key_added=f'leiden_r{res}')
    n_clusters = adata.obs[f'leiden_r{res}'].nunique()
    print(f'Resolution {res}: {n_clusters} clusters')
```

```r
# Seurat (R)
# Louvain/Leiden clustering (default algorithm)
seurat_obj <- FindClusters(seurat_obj, resolution = 0.5)

# View cluster assignments
head(Idents(seurat_obj))
table(Idents(seurat_obj))

# Sweep multiple resolutions
seurat_obj <- FindClusters(seurat_obj, resolution = c(0.2, 0.5, 0.8, 1.0, 1.5))
head(seurat_obj@meta.data)

# Compare resolution hierarchy with clustree
library(clustree)
clustree(seurat_obj, prefix = 'RNA_snn_res.')
```

## Embedding & Visualization

_modules: umap, tsne, visualization_

```python
# Scanpy (Python)
# Compute UMAP embedding
sc.tl.umap(adata, min_dist=0.3, spread=1.0)

# Visualize clusters on UMAP
sc.pl.umap(adata, color='leiden')

# Color by marker gene expression
sc.pl.umap(adata, color=['leiden', 'CD3D', 'MS4A1', 'CD14'])

# Alternative: tSNE (slower than UMAP)
# sc.tl.tsne(adata, n_pcs=30, perplexity=30)
# sc.pl.tsne(adata, color='leiden')
```

```r
# Seurat (R)
# Run UMAP
seurat_obj <- RunUMAP(seurat_obj, dims = 1:30)

# Visualize
DimPlot(seurat_obj, reduction = 'umap', label = TRUE)

# Split by sample
DimPlot(seurat_obj, reduction = 'umap', split.by = 'sample')

# Alternative: tSNE
# seurat_obj <- RunTSNE(seurat_obj, dims = 1:30)
# DimPlot(seurat_obj, reduction = 'tsne')

# Access embeddings for custom plotting
umap_coords <- Embeddings(seurat_obj, reduction = 'umap')
seurat_obj$UMAP_1 <- umap_coords[, 1]
seurat_obj$UMAP_2 <- umap_coords[, 2]
```

## Graph Abstraction (PAGA)

_modules: paga, trajectory_

```python
# Scanpy (Python)
# Partition-based graph abstraction on the Leiden clusters
sc.tl.paga(adata, groups='leiden')
sc.pl.paga(adata, color='leiden')

# Re-compute UMAP initialized from PAGA for a topology-aware embedding
sc.tl.umap(adata, init_pos='paga')
```

```r
# Seurat (R): PAGA is a Scanpy-specific tool. For trajectory inference in R,
# consider Monocle3 or slingshot as alternatives (out of scope for this skill).
```
