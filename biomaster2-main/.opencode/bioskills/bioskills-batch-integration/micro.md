## Preprocessing & Merging

_modules: merge, qc, normalization, hvg, pca_

```r
library(Seurat)

# Load and merge samples
samples <- list.files('data/', pattern = '*.h5', full.names = TRUE)
obj_list <- lapply(samples, Read10X_h5)
names(obj_list) <- gsub('.h5', '', basename(samples))

merged <- merge(CreateSeuratObject(obj_list[[1]], project = names(obj_list)[1]),
                y = lapply(2:length(obj_list), function(i)
                    CreateSeuratObject(obj_list[[i]], project = names(obj_list)[i])))

# QC
merged[['percent.mt']] <- PercentageFeatureSet(merged, pattern = '^MT-')
merged <- subset(merged, nFeature_RNA > 200 & nFeature_RNA < 5000 & percent.mt < 20)

# Preprocess
merged <- NormalizeData(merged)
merged <- FindVariableFeatures(merged, nfeatures = 2000)
merged <- ScaleData(merged, vars.to.regress = 'percent.mt')
merged <- RunPCA(merged, npcs = 50)
```

```python
# Python / Scanpy equivalent
import scanpy as sc

adata = sc.read_h5ad('merged.h5ad')
sc.pp.normalize_total(adata, target_sum=1e4)
sc.pp.log1p(adata)
sc.pp.highly_variable_genes(adata, batch_key='batch')
adata = adata[:, adata.var.highly_variable]
sc.pp.scale(adata)
sc.tl.pca(adata)
```

## Batch Correction

_modules: harmony, scvi, scanvi, seurat, cca, rpca, fastmnn, batch-correction_

```r
# ---- Harmony (R / Seurat) ----
library(harmony)
merged <- RunHarmony(merged, group.by.vars = 'orig.ident', dims.use = 1:30)

# Multiple batch variables (e.g. sample + technology)
merged <- RunHarmony(merged, group.by.vars = c('sample', 'technology'),
                     dims.use = 1:30, max.iter.harmony = 20)
```

```python
# ---- Harmony (Python / Scanpy) ----
import scanpy.external as sce
sce.pp.harmony_integrate(adata, key='batch')
# corrected embedding stored in adata.obsm['X_pca_harmony']
```

```python
# ---- scVI (Python) ----
import scvi
scvi.model.SCVI.setup_anndata(adata, batch_key='batch')
model = scvi.model.SCVI(adata, n_latent=30, n_layers=2)
model.train(max_epochs=100, early_stopping=True)
adata.obsm['X_scVI'] = model.get_latent_representation()

# scVI with continuous covariates
scvi.model.SCVI.setup_anndata(adata, batch_key='batch',
                               continuous_covariate_keys=['percent_mito'])
model = scvi.model.SCVI(adata, n_latent=30)
model.train()
```

```python
# ---- scANVI (semi-supervised label transfer) ----
scvi.model.SCANVI.setup_anndata(adata, batch_key='batch', labels_key='cell_type',
                                 unlabeled_category='Unknown')
model = scvi.model.SCANVI(adata, n_latent=30)
model.train(max_epochs=100)
adata.obs['predicted_type'] = model.predict()
```

```r
# ---- Seurat CCA integration ----
obj_list <- SplitObject(merged, split.by = 'batch')
obj_list <- lapply(obj_list, function(x) {
    x <- NormalizeData(x)
    x <- FindVariableFeatures(x, selection.method = 'vst', nfeatures = 2000)
    return(x)
})
anchors <- FindIntegrationAnchors(object.list = obj_list, dims = 1:30)
integrated <- IntegrateData(anchorset = anchors, dims = 1:30)
DefaultAssay(integrated) <- 'integrated'
integrated <- ScaleData(integrated)
integrated <- RunPCA(integrated)

# ---- Seurat RPCA (faster for large datasets) ----
anchors <- FindIntegrationAnchors(object.list = obj_list, dims = 1:30,
                                   reduction = 'rpca')
integrated <- IntegrateData(anchorset = anchors, dims = 1:30)

# ---- Seurat v5 integration ----
merged[['RNA']] <- split(merged[['RNA']], f = merged$batch)
merged <- IntegrateLayers(merged, method = CCAIntegration, orig.reduction = 'pca',
                          new.reduction = 'integrated.cca')
merged <- JoinLayers(merged)
```

```r
# ---- fastMNN (R) ----
library(batchelor)
library(SingleCellExperiment)
sce <- as.SingleCellExperiment(merged)
corrected <- fastMNN(sce, batch = sce$batch, d = 30, k = 20)
reducedDim(sce, 'MNN') <- reducedDim(corrected, 'corrected')
```

## Downstream Clustering & Visualization

_modules: neighbors, umap, leiden, clustering, visualization_

```r
# Seurat - use corrected reduction
merged <- RunUMAP(merged, reduction = 'harmony', dims = 1:30)
merged <- FindNeighbors(merged, reduction = 'harmony', dims = 1:30)
merged <- FindClusters(merged, resolution = 0.5)
DimPlot(merged, group.by = c('orig.ident', 'seurat_clusters'), ncol = 2)
```

```python
# Scanpy - use corrected representation
sc.pp.neighbors(adata, use_rep='X_pca_harmony')   # or use_rep='X_scVI'
sc.tl.umap(adata)
sc.tl.leiden(adata)
```

## Integration Evaluation

_modules: lisi, silhouette, evaluation, qc_

```r
# LISI (R) - higher batch LISI = more mixed; lower cell_type LISI = preserved
library(lisi)
lisi_scores <- compute_lisi(Embeddings(merged, 'harmony'),
                            merged@meta.data, c('batch', 'cell_type'))
mean(lisi_scores$batch)      # Want high (batches mixed)
mean(lisi_scores$cell_type)  # Want low (types preserved)

# Visual assessment before vs after
DimPlot(merged, reduction = 'pca', group.by = 'batch')
DimPlot(merged, reduction = 'pca', group.by = 'cell_type')
DimPlot(merged, reduction = 'harmony', group.by = 'batch')
DimPlot(merged, reduction = 'harmony', group.by = 'cell_type')
```

```python
# Silhouette score (Python)
from sklearn.metrics import silhouette_score
batch_sil = silhouette_score(adata.obsm['X_scVI'], adata.obs['batch'])        # want low (batches mixed)
celltype_sil = silhouette_score(adata.obsm['X_scVI'], adata.obs['cell_type'])  # want high (types separated)
```
