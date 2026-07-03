## Data Loading & QC Preparation

_modules: data-io, qc, doublet-rate_

```python
# Python (Scanpy): load 10x matrix and compute QC metrics
import scanpy as sc

adata = sc.read_10x_mtx('filtered_feature_bc_matrix/')
adata.var['mt'] = adata.var_names.str.startswith('MT-')
sc.pp.calculate_qc_metrics(adata, qc_vars=['mt'], inplace=True)
```

```r
# R (Seurat): load 10x matrix and compute QC metrics
library(Seurat)

counts <- Read10X('filtered_feature_bc_matrix/')
seurat_obj <- CreateSeuratObject(counts = counts, min.cells = 3, min.features = 200)
seurat_obj[['percent.mt']] <- PercentageFeatureSet(seurat_obj, pattern = '^MT-')
```

```
# Expected doublet rate scales with cells loaded:
#   rate ≈ cells_loaded / 1000 * 0.008
#
#   Cells Loaded | Expected Rate
#   1,000        | ~0.8%
#   2,000        | ~1.6%
#   5,000        | ~4.0%
#   10,000       | ~8.0%
#   15,000       | ~12%
```

## Scrublet Detection (Python)

_modules: scrublet, doublet-scoring, simulation_

```python
import scrublet as scr
import scanpy as sc
import numpy as np

# Basic usage
adata = sc.read_10x_mtx('filtered_feature_bc_matrix/')

scrub = scr.Scrublet(adata.X, expected_doublet_rate=0.06)
doublet_scores, predicted_doublets = scrub.scrub_doublets()

adata.obs['doublet_score'] = doublet_scores
adata.obs['predicted_doublet'] = predicted_doublets

print(f'Detected {predicted_doublets.sum()} doublets ({100*predicted_doublets.mean():.1f}%)')

# Adjusted parameters
scrub = scr.Scrublet(adata.X, expected_doublet_rate=0.06)
doublet_scores, predicted_doublets = scrub.scrub_doublets(
    min_counts=2,
    min_cells=3,
    min_gene_variability_pctl=85,
    n_prin_comps=30,
    synthetic_doublet_umi_subsampling=1.0
)

# Manual threshold instead of automatic call
scrub = scr.Scrublet(adata.X)
doublet_scores, _ = scrub.scrub_doublets()

threshold = 0.25
predicted_doublets = doublet_scores > threshold
adata.obs['predicted_doublet'] = predicted_doublets
```

## DoubletFinder Detection (R)

_modules: doubletfinder, pann, parameter-sweep, seurat_

```r
library(Seurat)
library(DoubletFinder)

# Preprocess and cluster (required before DoubletFinder)
seurat_obj <- NormalizeData(seurat_obj)
seurat_obj <- FindVariableFeatures(seurat_obj)
seurat_obj <- ScaleData(seurat_obj)
seurat_obj <- RunPCA(seurat_obj)
seurat_obj <- RunUMAP(seurat_obj, dims = 1:20)
seurat_obj <- FindNeighbors(seurat_obj, dims = 1:20)
seurat_obj <- FindClusters(seurat_obj, resolution = 0.5)

# pK parameter sweep
sweep.res <- paramSweep(seurat_obj, PCs = 1:20, sct = FALSE)
sweep.stats <- summarizeSweep(sweep.res, GT = FALSE)
bcmvn <- find.pK(sweep.stats)

optimal_pk <- as.numeric(as.character(bcmvn$pK[which.max(bcmvn$BCmetric)]))

# Classify doublets
nExp_poi <- round(0.06 * nrow(seurat_obj@meta.data))
seurat_obj <- doubletFinder(seurat_obj, PCs = 1:20, pN = 0.25, pK = optimal_pk,
                             nExp = nExp_poi, reuse.pANN = FALSE, sct = FALSE)

colnames(seurat_obj@meta.data)

# SCTransform variant
seurat_obj <- SCTransform(seurat_obj)
seurat_obj <- RunPCA(seurat_obj)
seurat_obj <- RunUMAP(seurat_obj, dims = 1:30)
seurat_obj <- FindNeighbors(seurat_obj, dims = 1:30)
seurat_obj <- FindClusters(seurat_obj, resolution = 0.5)

sweep.res <- paramSweep(seurat_obj, PCs = 1:30, sct = TRUE)
sweep.stats <- summarizeSweep(sweep.res, GT = FALSE)
bcmvn <- find.pK(sweep.stats)

optimal_pk <- as.numeric(as.character(bcmvn$pK[which.max(bcmvn$BCmetric)]))
nExp_poi <- round(0.06 * nrow(seurat_obj@meta.data))

seurat_obj <- doubletFinder(seurat_obj, PCs = 1:30, pN = 0.25, pK = optimal_pk,
                             nExp = nExp_poi, reuse.pANN = FALSE, sct = TRUE)

# Adjust expected doublet rate by cells loaded
n_cells <- ncol(seurat_obj)
doublet_rate <- n_cells / 1000 * 0.008
nExp_poi <- round(doublet_rate * n_cells)
```

## scDblFinder Detection (R)

_modules: scdblfinder, gradient-boosting, singlecellexperiment_

```r
library(scDblFinder)
library(SingleCellExperiment)

# Basic usage from counts matrix
sce <- SingleCellExperiment(assays = list(counts = counts_matrix))
sce <- scDblFinder(sce)

table(sce$scDblFinder.class)

# From a Seurat object
library(Seurat)

sce <- as.SingleCellExperiment(seurat_obj)
sce <- scDblFinder(sce)

seurat_obj$scDblFinder_class <- sce$scDblFinder.class
seurat_obj$scDblFinder_score <- sce$scDblFinder.score

DimPlot(seurat_obj, group.by = 'scDblFinder_class')

# Multi-sample processing (run per sample)
sce <- scDblFinder(sce, samples = 'sample_id')

# Adjust parameters
sce <- scDblFinder(sce,
    dbr = 0.06,
    dbr.sd = 0.015,
    nfeatures = 1500,
    dims = 20,
    k = 30
)
```

## Visualization & Doublet Filtering

_modules: visualization, filtering, umap, homotypic-heterotypic_

```python
# Python (Scrublet): histogram and UMAP
import matplotlib.pyplot as plt

scrub.plot_histogram()
plt.savefig('doublet_histogram.pdf')

# UMAP with doublet scores
sc.pp.normalize_total(adata, target_sum=1e4)
sc.pp.log1p(adata)
sc.pp.highly_variable_genes(adata)
sc.pp.pca(adata)
sc.pp.neighbors(adata)
sc.tl.umap(adata)

sc.pl.umap(adata, color=['doublet_score', 'predicted_doublet'], save='_doublets.pdf')

# Filter doublets
adata_filtered = adata[~adata.obs['predicted_doublet']].copy()
print(f'Kept {adata_filtered.n_obs} cells after doublet removal')

# Inspect homotypic doublets (same cell type, higher total counts)
adata.obs['log_counts'] = np.log1p(adata.obs['total_counts'])
sc.pl.violin(adata, 'log_counts', groupby='predicted_doublet')
```

```r
# R (DoubletFinder): filter singlets
df_col <- grep('DF.classifications', colnames(seurat_obj@meta.data), value = TRUE)
seurat_obj$doublet <- seurat_obj@meta.data[[df_col]]

DimPlot(seurat_obj, group.by = 'doublet')

seurat_obj <- subset(seurat_obj, subset = doublet == 'Singlet')

# R (scDblFinder): filter singlets
seurat_obj <- subset(seurat_obj, subset = scDblFinder_class == 'singlet')
```

## Method Comparison & Pipeline Integration

_modules: method-comparison, pipeline-integration, scanpy, seurat_

```r
# Compare multiple methods
library(scDblFinder)

seurat_obj$scrublet <- scrublet_results
sce <- as.SingleCellExperiment(seurat_obj)
sce <- scDblFinder(sce)
seurat_obj$scDblFinder <- sce$scDblFinder.class

DimPlot(seurat_obj, group.by = c('doublet', 'scDblFinder', 'scrublet'), ncol = 3)

table(seurat_obj$doublet, seurat_obj$scDblFinder)
```

```
# Method comparison summary:
#   Method        | Speed | Accuracy  | Language
#   Scrublet      | Fast  | Good      | Python
#   DoubletFinder | Slow  | Good      | R
#   scDblFinder   | Fast  | Excellent | R
```

```python
# Scanpy integration pipeline: detect doublets before QC filtering
import scanpy as sc
import scrublet as scr

adata = sc.read_10x_mtx('filtered_feature_bc_matrix/')

adata.var['mt'] = adata.var_names.str.startswith('MT-')
sc.pp.calculate_qc_metrics(adata, qc_vars=['mt'], inplace=True)

scrub = scr.Scrublet(adata.X, expected_doublet_rate=0.06)
doublet_scores, predicted_doublets = scrub.scrub_doublets()
adata.obs['doublet_score'] = doublet_scores
adata.obs['is_doublet'] = predicted_doublets

print(f'Before filtering: {adata.n_obs} cells')
adata = adata[~adata.obs['is_doublet']].copy()
adata = adata[adata.obs['pct_counts_mt'] < 20].copy()
print(f'After filtering: {adata.n_obs} cells')

sc.pp.normalize_total(adata, target_sum=1e4)
sc.pp.log1p(adata)
sc.pp.highly_variable_genes(adata)
sc.pp.pca(adata)
sc.pp.neighbors(adata)
sc.tl.umap(adata)
sc.tl.leiden(adata)
```

```r
# Seurat integration pipeline: preprocess, detect, filter, re-preprocess
library(Seurat)
library(DoubletFinder)

seurat_obj <- Read10X('filtered_feature_bc_matrix/')
seurat_obj <- CreateSeuratObject(counts = seurat_obj, min.cells = 3, min.features = 200)

seurat_obj[['percent.mt']] <- PercentageFeatureSet(seurat_obj, pattern = '^MT-')

seurat_obj <- NormalizeData(seurat_obj)
seurat_obj <- FindVariableFeatures(seurat_obj)
seurat_obj <- ScaleData(seurat_obj)
seurat_obj <- RunPCA(seurat_obj)
seurat_obj <- RunUMAP(seurat_obj, dims = 1:20)
seurat_obj <- FindNeighbors(seurat_obj, dims = 1:20)
seurat_obj <- FindClusters(seurat_obj, resolution = 0.5)

sweep.res <- paramSweep(seurat_obj, PCs = 1:20)
sweep.stats <- summarizeSweep(sweep.res)
bcmvn <- find.pK(sweep.stats)
pk <- as.numeric(as.character(bcmvn$pK[which.max(bcmvn$BCmetric)]))
nExp <- round(0.06 * ncol(seurat_obj))

seurat_obj <- doubletFinder(seurat_obj, PCs = 1:20, pN = 0.25, pK = pk, nExp = nExp)

df_col <- grep('DF.classifications', colnames(seurat_obj@meta.data), value = TRUE)
seurat_obj <- subset(seurat_obj, cells = colnames(seurat_obj)[seurat_obj@meta.data[[df_col]] == 'Singlet'])
seurat_obj <- subset(seurat_obj, subset = percent.mt < 20)

# Re-preprocess clean singlets
seurat_obj <- NormalizeData(seurat_obj)
seurat_obj <- FindVariableFeatures(seurat_obj)
seurat_obj <- ScaleData(seurat_obj)
seurat_obj <- RunPCA(seurat_obj)
seurat_obj <- RunUMAP(seurat_obj, dims = 1:20)
seurat_obj <- FindNeighbors(seurat_obj, dims = 1:20)
seurat_obj <- FindClusters(seurat_obj)
```
