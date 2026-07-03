## Reading 10X Genomics Data

_modules: read-10x, cellranger, scanpy, seurat_

```python
# Python: Scanpy
import scanpy as sc

# Read 10X cellranger MTX directory (filtered_feature_bc_matrix/)
adata = sc.read_10x_mtx('filtered_feature_bc_matrix/', var_names='gene_symbols', cache=True)
print(f'Loaded {adata.n_obs} cells x {adata.n_vars} genes')

# Read 10X h5 file directly
adata = sc.read_10x_h5('filtered_feature_bc_matrix.h5')
```

```r
# R: Seurat
library(Seurat)

# Read 10X cellranger MTX directory
counts <- Read10X(data.dir = 'filtered_feature_bc_matrix/')
seurat_obj <- CreateSeuratObject(counts = counts, project = 'PBMC',
                                 min.cells = 3, min.features = 200)

# Read 10X h5 file directly
counts <- Read10X_h5('filtered_feature_bc_matrix.h5')
seurat_obj <- CreateSeuratObject(counts = counts, project = 'PBMC')
```

## Creating Objects from Matrices

_modules: anndata, seurat-object, object-structure, from-matrix_

```python
import anndata as ad
import numpy as np
import pandas as pd

# Build AnnData from a count matrix (100 cells x 500 genes)
counts = np.random.poisson(1, size=(100, 500))
adata = ad.AnnData(
    X=counts,
    obs=pd.DataFrame(index=[f'cell_{i}' for i in range(100)]),
    var=pd.DataFrame(index=[f'gene_{i}' for i in range(500)])
)

# AnnData structure map:
#   adata.X      expression matrix (cells x genes)
#   adata.obs    cell metadata (DataFrame)
#   adata.var    gene metadata (DataFrame)
#   adata.uns    unstructured annotations (dict)
#   adata.obsm   cell embeddings (PCA, UMAP)
#   adata.varm   gene embeddings
#   adata.obsp   cell-cell graphs
#   adata.layers alternative matrices (raw counts, normalized)
print(f'Shape: {adata.shape}')
print(f'Cell metadata: {adata.obs.columns.tolist()}')
print(f'Gene metadata: {adata.var.columns.tolist()}')
```

```r
library(Seurat)
library(Matrix)

# Build Seurat object from a sparse matrix (500 genes x 1000 cells)
counts <- Matrix(rpois(1000 * 500, 1), nrow = 500, ncol = 1000, sparse = TRUE)
rownames(counts) <- paste0('gene_', 1:500)
colnames(counts) <- paste0('cell_', 1:1000)
seurat_obj <- CreateSeuratObject(counts = counts, project = 'MyProject')

# Seurat v5 structure map:
#   Layers:      counts, data, scale.data
#   Metadata:    seurat_obj@meta.data
#   Reductions:  seurat_obj@reductions
#   Graphs:      seurat_obj@graphs
counts <- LayerData(seurat_obj, layer = 'counts')  # or seurat_obj[['RNA']]$counts
head(seurat_obj@meta.data)
```

## Reading and Writing Native Formats

_modules: h5ad, rds, csv, loom, io, serialization_

```python
import scanpy as sc

# h5ad is the native AnnData format
adata = sc.read_h5ad('data.h5ad')
adata.write_h5ad('output.h5ad')
adata.write_h5ad('output.h5ad', compression='gzip')

# Other readable formats
adata = sc.read_csv('counts.csv')      # CSV/TSV (genes as columns, cells as rows)
adata = sc.read_loom('data.loom')      # Loom
adata = sc.read_text('counts.txt')     # Tab-separated text
```

```r
library(Seurat)

# RDS is the native Seurat serialization
saveRDS(seurat_obj, file = 'seurat_obj.rds')
seurat_obj <- readRDS('seurat_obj.rds')
```

## Metadata, Subsetting, and Raw Counts

_modules: metadata, subsetting, raw-counts, layers, add-metadata_

```python
import scanpy as sc

# Add cell metadata
adata.obs['sample'] = 'sample_1'
adata.obs['batch'] = ['batch_1'] * 50 + ['batch_2'] * 50

# Add gene metadata and unstructured data
adata.var['gene_type'] = 'protein_coding'
adata.uns['experiment'] = 'PBMC_3k'

# Subsetting
adata_subset = adata[adata.obs['batch'] == 'batch_1'].copy()   # by cells
adata_subset = adata[:, adata.var['highly_variable']].copy()   # by genes
adata_subset = adata[adata.obs['n_genes'] > 200, :].copy()     # boolean mask

# Store raw counts before normalization
adata.raw = adata.copy()                  # access later via adata.raw.X
adata.layers['counts'] = adata.X.copy()   # or keep a parallel layer
```

```r
library(Seurat)

# Add cell metadata
seurat_obj$sample <- 'sample_1'
seurat_obj$batch <- c(rep('batch_1', 500), rep('batch_2', 500))

# Add metadata via AddMetaData
metadata_df <- data.frame(
    cell_type = rep('unknown', ncol(seurat_obj)),
    row.names = colnames(seurat_obj)
)
seurat_obj <- AddMetaData(seurat_obj, metadata = metadata_df)

# Subsetting
seurat_subset <- subset(seurat_obj, subset = batch == 'batch_1')
seurat_subset <- subset(seurat_obj, cells = colnames(seurat_obj)[1:500])
seurat_subset <- subset(seurat_obj, features = rownames(seurat_obj)[1:100])
```

## Merging and Format Conversion

_modules: merge, join-layers, format-conversion, seuratdisk, h5seurat, cross-language_

```r
library(Seurat)
library(SeuratDisk)

# Merge multiple Seurat objects
merged <- merge(seurat_obj1, y = c(seurat_obj2, seurat_obj3),
                add.cell.ids = c('S1', 'S2', 'S3'))
merged <- JoinLayers(merged)   # v5: unify split layers after merge

# Seurat -> AnnData
SaveH5Seurat(seurat_obj, filename = 'data.h5seurat')
Convert('data.h5seurat', dest = 'h5ad')
```

```python
import scanpy as sc

# Read the converted h5ad (coming from Seurat)
adata = sc.read_h5ad('data.h5ad')

# AnnData -> Seurat: write h5ad, then convert in R
adata.write_h5ad('data.h5ad')
```

```r
# In R: convert h5ad back to Seurat
library(SeuratDisk)
Convert('data.h5ad', dest = 'h5seurat')
seurat_obj <- LoadH5Seurat('data.h5seurat')
```
