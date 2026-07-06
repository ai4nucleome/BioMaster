## Setup & Data Loading

_modules: setup, data-loading, chromatin-assay_

```r
# Install Signac and dependencies
install.packages('Signac')
BiocManager::install(c('EnsDb.Hsapiens.v86', 'biovizBase', 'motifmatchr', 'chromVAR', 'JASPAR2020', 'TFBSTools'))

library(Signac)
library(Seurat)
library(EnsDb.Hsapiens.v86)

# Load 10X peak-barcode matrix and per-cell metadata
counts <- Read10X_h5('filtered_peak_bc_matrix.h5')
metadata <- read.csv('singlecell.csv', header = TRUE, row.names = 1)

# Build ChromatinAssay and Seurat object
chrom_assay <- CreateChromatinAssay(
    counts = counts,
    sep = c(':', '-'),
    genome = 'hg38',
    fragments = 'fragments.tsv.gz',
    min.cells = 10,
    min.features = 200
)
obj <- CreateSeuratObject(counts = chrom_assay, assay = 'peaks', meta.data = metadata)

# Attach gene annotations from EnsDb
annotations <- GetGRangesFromEnsDb(ensdb = EnsDb.Hsapiens.v86)
seqlevelsStyle(annotations) <- 'UCSC'
Annotation(obj) <- annotations

# --- ArchR alternative (large datasets) ---
# devtools::install_github('GreenleafLab/ArchR', ref = 'master', repos = BiocManager::repositories())
# library(ArchR)
# addArchRGenome('hg38')
# inputFiles <- c('sample1_fragments.tsv.gz', 'sample2_fragments.tsv.gz')
# names(inputFiles) <- c('sample1', 'sample2')
# ArrowFiles <- createArrowFiles(inputFiles = inputFiles, sampleNames = names(inputFiles),
#     filterTSS = 4, filterFrags = 1000, addTileMat = TRUE, addGeneScoreMat = TRUE)
# proj <- ArchRProject(ArrowFiles = ArrowFiles, outputDirectory = 'ArchR_output', copyArrows = TRUE)
```

## QC & Filtering

_modules: qc, filtering, tss-enrichment, nucleosome-signal, doublet-detection_

```r
# Compute QC metrics
obj <- NucleosomeSignal(obj)
obj <- TSSEnrichment(obj, fast = FALSE)

obj$pct_reads_in_peaks <- obj$peak_region_fragments / obj$passed_filters * 100
obj$blacklist_ratio <- obj$blacklist_region_fragments / obj$peak_region_fragments

VlnPlot(obj, features = c('pct_reads_in_peaks', 'peak_region_fragments', 'TSS.enrichment',
    'blacklist_ratio', 'nucleosome_signal'), pt.size = 0.1, ncol = 5)

# Filter cells by QC thresholds
obj <- subset(obj,
    peak_region_fragments > 3000 &
    peak_region_fragments < 20000 &
    pct_reads_in_peaks > 15 &
    blacklist_ratio < 0.05 &
    nucleosome_signal < 4 &
    TSS.enrichment > 2
)

# QC threshold reference:
# | Metric             | Typical Range  | Filter        |
# | Unique fragments   | 1,000-100,000  | > 1,000-3,000 |
# | TSS enrichment     | 2-30           | > 2-4         |
# | Fraction in peaks  | 20-70%         | > 15-20%      |
# | Nucleosome signal  | 0.5-2          | < 4           |
# | Blacklist ratio    | 0-0.05         | < 0.05        |

# --- ArchR alternative: QC plot + doublet removal ---
# df <- getCellColData(proj, select = c('log10(nFrags)', 'TSSEnrichment'))
# p <- ggPoint(x = df[,1], y = df[,2], colorDensity = TRUE, continuousSet = 'sambaNight',
#     xlabel = 'Log10 Unique Fragments', ylabel = 'TSS Enrichment',
#     xlim = c(log10(500), quantile(df[,1], probs = 0.99)),
#     ylim = c(0, quantile(df[,2], probs = 0.99)))
# proj <- filterDoublets(proj)
```

## Normalization & Dimensionality Reduction

_modules: normalization, tf-idf, lsi, dimensionality-reduction_

```r
# TF-IDF normalization and feature selection
obj <- RunTFIDF(obj)
obj <- FindTopFeatures(obj, min.cutoff = 'q0')

# Latent semantic indexing (LSI via SVD)
obj <- RunSVD(obj)
DepthCor(obj)  # identify depth-correlated components; drop them downstream (e.g. start at dim 2)

# --- ArchR alternative: iterative LSI ---
# proj <- addIterativeLSI(proj, useMatrix = 'TileMatrix', name = 'IterativeLSI',
#     iterations = 2,
#     clusterParams = list(resolution = c(0.2), sampleCells = 10000, n.start = 10),
#     varFeatures = 25000, dimsToUse = 1:30)
```

## Clustering & Cell Annotation

_modules: clustering, umap, leiden, gene-activity, annotation_

```r
# UMAP embedding and clustering (skip depth-correlated LSI component 1)
obj <- RunUMAP(obj, reduction = 'lsi', dims = 2:30)
obj <- FindNeighbors(obj, reduction = 'lsi', dims = 2:30)
obj <- FindClusters(obj, algorithm = 3, resolution = 0.5)
DimPlot(obj, label = TRUE) + NoLegend()

# Gene activity scores for annotation
gene_activities <- GeneActivity(obj)
obj[['RNA']] <- CreateAssayObject(counts = gene_activities)
obj <- NormalizeData(obj, assay = 'RNA', normalization.method = 'LogNormalize',
    scale.factor = median(obj$nCount_RNA))
DefaultAssay(obj) <- 'RNA'
FeaturePlot(obj, features = c('CD34', 'MS4A1', 'CD3D', 'CD14'), pt.size = 0.1, max.cutoff = 'q95')

# --- ArchR alternative ---
# proj <- addClusters(proj, reducedDims = 'IterativeLSI', method = 'Seurat',
#     name = 'Clusters', resolution = 0.8)
# proj <- addUMAP(proj, reducedDims = 'IterativeLSI', name = 'UMAP',
#     nNeighbors = 30, minDist = 0.5, metric = 'cosine')
# plotEmbedding(proj, colorBy = 'cellColData', name = 'Clusters', embedding = 'UMAP')
# markersGS <- getMarkerFeatures(proj, useMatrix = 'GeneScoreMatrix', groupBy = 'Clusters',
#     bias = c('TSSEnrichment', 'log10(nFrags)'), testMethod = 'wilcoxon')
# markerList <- getMarkers(markersGS, cutOff = 'FDR <= 0.01 & Log2FC >= 1.25')
# heatmapGS <- plotMarkerHeatmap(seMarker = markersGS, cutOff = 'FDR <= 0.01 & Log2FC >= 1.25',
#     labelMarkers = c('CD34', 'MS4A1', 'CD3D', 'CD14'))
```

## Peak Calling & Differential Accessibility

_modules: peak-calling, macs2, differential-accessibility_

```r
# Call peaks per cluster with MACS2
peaks <- CallPeaks(obj, group.by = 'seurat_clusters', macs2.path = '/path/to/macs2')

# Quantify unified peak set across all cells
peak_counts <- FeatureMatrix(fragments = Fragments(obj), features = peaks, cells = colnames(obj))
obj[['peaks_called']] <- CreateChromatinAssay(counts = peak_counts,
    fragments = Fragments(obj), annotation = Annotation(obj))

# Differential accessibility between clusters (control for sequencing depth)
DefaultAssay(obj) <- 'peaks'
da_peaks <- FindMarkers(obj, ident.1 = 'cluster1', ident.2 = 'cluster2',
    test.use = 'LR', latent.vars = 'peak_region_fragments')
head(da_peaks[order(da_peaks$avg_log2FC, decreasing = TRUE), ], 10)

# --- ArchR alternative ---
# proj <- addGroupCoverages(proj, groupBy = 'Clusters')
# proj <- addReproduciblePeakSet(proj, groupBy = 'Clusters', pathToMacs2 = '/path/to/macs2')
# proj <- addPeakMatrix(proj)
```

## Motif Activity & Visualization

_modules: motif, chromvar, coverage-plot, integration, label-transfer_

```r
# Motif annotations and chromVAR deviation scoring
library(JASPAR2020)
library(TFBSTools)
library(motifmatchr)

pfm <- getMatrixSet(JASPAR2020, opts = list(collection = 'CORE',
    tax_group = 'vertebrates', all_versions = FALSE))
obj <- AddMotifs(obj, genome = BSgenome.Hsapiens.UCSC.hg38, pfm = pfm)
obj <- RunChromVAR(obj, genome = BSgenome.Hsapiens.UCSC.hg38)

DefaultAssay(obj) <- 'chromvar'
FeaturePlot(obj, features = 'MA0139.1', min.cutoff = 'q10', max.cutoff = 'q90')  # CTCF

# Differential motif activity between clusters
differential_activity <- FindMarkers(obj, ident.1 = 'cluster1', ident.2 = 'cluster2',
    only.pos = TRUE, mean.fxn = rowMeans, fc.name = 'avg_diff')

# Coverage plots over regions/genes
CoveragePlot(obj, region = 'chr1-1000000-1050000', group.by = 'seurat_clusters', annotation = TRUE)
CoveragePlot(obj, region = 'MS4A1', group.by = 'seurat_clusters',
    extend.upstream = 10000, extend.downstream = 5000)

# Integration with scRNA-seq reference (label transfer)
transfer_anchors <- FindTransferAnchors(reference = rna_obj, query = obj,
    features = VariableFeatures(rna_obj), reference.assay = 'RNA', query.assay = 'RNA',
    reduction = 'cca')
predicted_labels <- TransferData(anchorset = transfer_anchors, refdata = rna_obj$celltype,
    weight.reduction = obj[['lsi']], dims = 2:30)
obj <- AddMetaData(obj, metadata = predicted_labels)

# --- chromVAR standalone ---
# library(chromVAR); library(motifmatchr); library(BSgenome.Hsapiens.UCSC.hg38)
# counts <- readRDS('peak_counts.rds')  # SummarizedExperiment
# counts <- addGCBias(counts, genome = BSgenome.Hsapiens.UCSC.hg38)
# motifs <- getJasparMotifs()
# motif_ix <- matchMotifs(motifs, counts, genome = BSgenome.Hsapiens.UCSC.hg38)
# bg <- getBackgroundPeaks(counts)
# dev <- computeDeviations(counts, motif_ix, background_peaks = bg)
# variability <- computeVariability(dev)
# plotVariability(variability, use_plotly = FALSE)

# --- ArchR alternative ---
# proj <- addMotifAnnotations(proj, motifSet = 'cisbp', name = 'Motif')
# enrichMotifs <- peakAnnoEnrichment(seMarker = markersPeaks, ArchRProj = proj,
#     peakAnnotation = 'Motif', cutOff = 'FDR <= 0.1 & Log2FC >= 0.5')
# heatmapEM <- plotEnrichHeatmap(enrichMotifs, n = 7, transpose = TRUE)
# proj <- addBgdPeaks(proj)
# proj <- addDeviationsMatrix(proj, peakAnnotation = 'Motif', force = TRUE)
# plotVarDev <- getVarDeviations(proj, name = 'MotifMatrix', plot = TRUE)
# motifs <- c('GATA1', 'CEBPA', 'EBF1', 'IRF8', 'PAX5')
# markerMotifs <- getFeatures(proj, select = paste(motifs, collapse = '|'), useMatrix = 'MotifMatrix')
# p <- plotEmbedding(proj, colorBy = 'MotifMatrix', name = sort(markerMotifs),
#     embedding = 'UMAP', imputeWeights = getImputeWeights(proj))
```
