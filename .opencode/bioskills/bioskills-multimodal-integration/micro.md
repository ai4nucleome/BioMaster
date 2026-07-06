## Load Multimodal Data

_modules: data-io, multi-assay, cite-seq, multiome_

```r
library(Seurat)

# --- CITE-seq: RNA + ADT ---
data <- Read10X('filtered_feature_bc_matrix/')
rna_counts <- data$`Gene Expression`
adt_counts <- data$`Antibody Capture`

obj <- CreateSeuratObject(counts = rna_counts, assay = 'RNA')
obj[['ADT']] <- CreateAssayObject(counts = adt_counts)

# --- 10X Multiome: RNA + ATAC ---
library(Signac)
rna_counts <- Read10X_h5('filtered_feature_bc_matrix.h5')$`Gene Expression`
atac_counts <- Read10X_h5('filtered_feature_bc_matrix.h5')$Peaks
fragments <- CreateFragmentObject('atac_fragments.tsv.gz')

obj <- CreateSeuratObject(counts = rna_counts, assay = 'RNA')
obj[['ATAC']] <- CreateChromatinAssay(counts = atac_counts, fragments = fragments,
                                       genome = 'hg38', min.cells = 5)
```

```python
# Python (muon)
import scanpy as sc
import muon as mu
from muon import prot as pt

mdata = mu.read_10x_h5('filtered_feature_bc_matrix.h5')
rna = mdata.mod['rna']
prot = mdata.mod['prot']
```

## Per-Modality QC and Normalization

_modules: qc, normalization, clr, tfidf, mito, tss-enrichment_

```r
# --- RNA QC + normalization ---
obj <- PercentageFeatureSet(obj, pattern = '^MT-', col.name = 'percent.mt')
obj <- subset(obj, nFeature_RNA > 200 & percent.mt < 20)
obj <- NormalizeData(obj, assay = 'RNA')
obj <- FindVariableFeatures(obj, assay = 'RNA')
obj <- ScaleData(obj, assay = 'RNA')

# --- ADT: CLR normalization ---
obj <- NormalizeData(obj, assay = 'ADT', normalization.method = 'CLR', margin = 2)
obj <- ScaleData(obj, assay = 'ADT')

# --- ATAC: QC + TF-IDF ---
obj <- NucleosomeSignal(obj)
obj <- TSSEnrichment(obj)
obj <- RunTFIDF(obj, assay = 'ATAC')
obj <- FindTopFeatures(obj, assay = 'ATAC', min.cutoff = 'q0')
```

```python
# Python (muon): RNA + protein normalization
sc.pp.filter_cells(rna, min_genes=200)
sc.pp.normalize_total(rna, target_sum=1e4)
sc.pp.log1p(rna)
sc.pp.highly_variable_genes(rna)
pt.pp.clr(prot)
```

## Per-Modality Dimensionality Reduction

_modules: pca, lsi, svd, dimensionality-reduction_

```r
# RNA PCA
obj <- RunPCA(obj, assay = 'RNA', reduction.name = 'pca')

# ADT PCA (use all protein features)
obj <- RunPCA(obj, assay = 'ADT', reduction.name = 'apca',
              features = rownames(obj[['ADT']]))

# ATAC LSI/SVD (run after TF-IDF)
obj <- RunSVD(obj, assay = 'ATAC')
```

```python
# Python (muon): RNA PCA
sc.tl.pca(rna)
```

## Multimodal Integration

_modules: wnn, mofa, integration, multimodal-neighbors_

```r
# --- CITE-seq WNN ---
obj <- FindMultiModalNeighbors(obj,
    reduction.list = list('pca', 'apca'),
    dims.list = list(1:30, 1:18))

# --- 10X Multiome WNN (skip LSI component 1, depth-correlated) ---
obj <- FindMultiModalNeighbors(obj,
    reduction.list = list('pca', 'lsi'),
    dims.list = list(1:30, 2:30))
```

```python
# Python (muon): MOFA factors
mu.tl.mofa(mdata, n_factors=20)
```

## Joint Clustering and Embedding

_modules: clustering, umap, community-detection, leiden_

```r
# Cluster on WNN graph
obj <- FindClusters(obj, graph.name = 'wsnn', resolution = 0.5)

# UMAP on weighted nearest neighbors
obj <- RunUMAP(obj, nn.name = 'weighted.nn', reduction.name = 'wnn.umap')
```

```python
# Python (muon): joint UMAP on MOFA factors
mu.tl.umap(mdata)
```

## Visualization and Marker Discovery

_modules: visualization, markers, modality-weights, differential-expression_

```r
# UMAP colored by cluster
DimPlot(obj, reduction = 'wnn.umap', label = TRUE)

# ADT expression on UMAP
FeaturePlot(obj, features = c('adt_CD3', 'adt_CD19', 'adt_CD14'),
            reduction = 'wnn.umap')

# Per-cell modality weights by cluster
VlnPlot(obj, features = 'RNA.weight', group.by = 'seurat_clusters')

# Inspect raw weights and average by cluster
weights <- obj@reductions$wnn@misc$weights
aggregate(weights, by = list(obj$seurat_clusters), mean)

# Multi-modal markers per cluster
DefaultAssay(obj) <- 'RNA'
rna_markers <- FindAllMarkers(obj, only.pos = TRUE)
DefaultAssay(obj) <- 'ADT'
adt_markers <- FindAllMarkers(obj, only.pos = TRUE)

all_markers <- rbind(
    transform(rna_markers, modality = 'RNA'),
    transform(adt_markers, modality = 'ADT')
)
```

```python
# Python: joint UMAP plot and RNA-protein correlation
mu.pl.umap(mdata, color=['rna:leiden', 'prot:CD3'])

import numpy as np
common = set(rna.var_names) & set(prot.var_names)
for gene in common:
    rna_expr = rna[:, gene].X.toarray().flatten()
    prot_expr = prot[:, gene].X.toarray().flatten()
    corr = np.corrcoef(rna_expr, prot_expr)[0, 1]
    print(f'{gene}: r={corr:.3f}')
```
