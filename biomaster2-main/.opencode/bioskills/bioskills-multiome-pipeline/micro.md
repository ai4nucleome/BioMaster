## Load Multiome Data

_modules: data-io, seurat, signac, chromatin-assay_

```r
library(Seurat)
library(Signac)
library(EnsDb.Hsapiens.v86)
library(ggplot2)

# Load RNA + ATAC from the joint 10X Multiome HDF5
rna_counts <- Read10X_h5('filtered_feature_bc_matrix.h5')
# For multiome this returns a list with 'Gene Expression' and 'Peaks'

# Base Seurat object from RNA
seurat_obj <- CreateSeuratObject(
    counts = rna_counts$`Gene Expression`,
    assay = 'RNA'
)

# ATAC counts and fragments
atac_counts <- rna_counts$Peaks
frags <- CreateFragmentObject('atac_fragments.tsv.gz', cells = colnames(seurat_obj))

# Build ChromatinAssay with gene annotations
atac_assay <- CreateChromatinAssay(
    counts = atac_counts,
    sep = c(':', '-'),
    fragments = frags,
    annotation = GetGRangesFromEnsDb(ensdb = EnsDb.Hsapiens.v86)
)

seurat_obj[['ATAC']] <- atac_assay
```

## RNA Quality Control and Processing

_modules: qc, sctransform, pca_

```r
# QC metrics
seurat_obj[['percent.mt']] <- PercentageFeatureSet(seurat_obj, pattern = '^MT-')

# Filter cells
seurat_obj <- subset(seurat_obj,
    nCount_RNA > 1000 &
    nCount_RNA < 25000 &
    percent.mt < 20
)

# Normalize RNA with SCTransform and run PCA
seurat_obj <- SCTransform(seurat_obj, assay = 'RNA', verbose = FALSE)
seurat_obj <- RunPCA(seurat_obj, assay = 'SCT', verbose = FALSE)
```

## ATAC Quality Control and Processing

_modules: qc, tf-idf, lsi, tss-enrichment, nucleosome-signal_

```r
# ATAC QC metrics
DefaultAssay(seurat_obj) <- 'ATAC'
seurat_obj <- NucleosomeSignal(seurat_obj)
seurat_obj <- TSSEnrichment(seurat_obj)

# Visualize QC
VlnPlot(seurat_obj, features = c('nCount_ATAC', 'TSS.enrichment', 'nucleosome_signal'),
        pt.size = 0, ncol = 3)

# Filter ATAC
seurat_obj <- subset(seurat_obj,
    nCount_ATAC > 1000 &
    nCount_ATAC < 100000 &
    TSS.enrichment > 2 &
    nucleosome_signal < 4
)

# Normalize ATAC: TF-IDF + SVD (LSI)
seurat_obj <- RunTFIDF(seurat_obj)
seurat_obj <- FindTopFeatures(seurat_obj, min.cutoff = 'q0')
seurat_obj <- RunSVD(seurat_obj)

# Inspect LSI components (first often correlates with depth)
DepthCor(seurat_obj)
```

## Weighted Nearest Neighbors Integration

_modules: wnn, integration, umap, clustering_

```r
# Build WNN graph from both modalities
seurat_obj <- FindMultiModalNeighbors(
    seurat_obj,
    reduction.list = list('pca', 'lsi'),
    dims.list = list(1:30, 2:30),  # Skip LSI component 1 if depth-correlated
    modality.weight.name = 'RNA.weight'
)

# UMAP on WNN graph
seurat_obj <- RunUMAP(seurat_obj, nn.name = 'weighted.nn',
                       reduction.name = 'wnn.umap', reduction.key = 'wnnUMAP_')

# Cluster on the joint WNN graph
seurat_obj <- FindClusters(seurat_obj, graph.name = 'wsnn',
                            algorithm = 3, resolution = 0.5, verbose = FALSE)
```

## Visualization and Markers

_modules: visualization, marker-genes, differential-peaks_

```r
# Compare modality-specific and joint embeddings
p1 <- DimPlot(seurat_obj, reduction = 'pca', label = TRUE) + ggtitle('RNA PCA')
p2 <- DimPlot(seurat_obj, reduction = 'lsi', label = TRUE) + ggtitle('ATAC LSI')
p3 <- DimPlot(seurat_obj, reduction = 'wnn.umap', label = TRUE) + ggtitle('WNN UMAP')
p1 + p2 + p3

# Modality weights per cell
VlnPlot(seurat_obj, features = 'RNA.weight', group.by = 'seurat_clusters', pt.size = 0)

# RNA markers per cluster
DefaultAssay(seurat_obj) <- 'SCT'
rna_markers <- FindAllMarkers(seurat_obj, only.pos = TRUE, min.pct = 0.25)

# Differentially accessible ATAC peaks (regress out total ATAC counts)
DefaultAssay(seurat_obj) <- 'ATAC'
atac_markers <- FindAllMarkers(seurat_obj, only.pos = TRUE, min.pct = 0.05,
                                test.use = 'LR', latent.vars = 'nCount_ATAC')
```

## Gene-Peak Linkage

_modules: gene-peak-linkage, coverage-plot, cis-regulatory_

```r
# Compute region statistics against the reference genome
DefaultAssay(seurat_obj) <- 'ATAC'
seurat_obj <- RegionStats(seurat_obj, genome = BSgenome.Hsapiens.UCSC.hg38)

# Link peaks to genes by correlating accessibility with expression
seurat_obj <- LinkPeaks(
    seurat_obj,
    peak.assay = 'ATAC',
    expression.assay = 'SCT',
    genes.use = c('CD8A', 'CD4', 'MS4A1', 'CD14')  # Example marker genes
)

# Visualize peak-gene coverage around a gene
CoveragePlot(seurat_obj, region = 'CD8A', features = 'CD8A',
             expression.assay = 'SCT', extend.upstream = 10000, extend.downstream = 10000)
```
