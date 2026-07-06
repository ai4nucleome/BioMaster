## Data Preparation

_modules: prepdata, transform, sce_

```r
library(CATALYST)
library(SingleCellExperiment)

# Create SCE from flowSet with arcsinh transformation
sce <- prepData(fs, panel, md, transform = TRUE, cofactor = 5)

# Inspect marker classes (type vs state)
table(rowData(sce)$marker_class)
```

## Clustering

_modules: flowsom, catalyst, phenograph, clustering_

```r
# --- CATALYST / FlowSOM (recommended) ---
sce <- cluster(sce,
               features = 'type',   # use type markers from panel
               xdim = 10, ydim = 10,
               maxK = 20,
               seed = 42)

# Inspect metacluster sizes
table(cluster_ids(sce, 'meta20'))

# --- Standalone FlowSOM on a single flowFrame ---
library(FlowSOM)
marker_cols <- grep('CD|HLA', colnames(fcs), value = TRUE)
fsom <- FlowSOM(fcs, colsToUse = marker_cols,
                xdim = 10, ydim = 10, nClus = 20, seed = 42)
clusters <- GetMetaclusters(fsom)
exprs(fcs) <- cbind(exprs(fcs), cluster = clusters)

# --- Phenograph (graph-based alternative) ---
library(Rphenograph)
expr <- assay(sce, 'exprs')
pheno_result <- Rphenograph(t(expr[rowData(sce)$marker_class == 'type', ]), k = 30)
sce$phenograph <- factor(membership(pheno_result[[2]]))
```

## Dimensionality Reduction & Visualization

_modules: umap, tsne, dimensionality-reduction, visualization_

```r
# Compute embeddings on type markers
sce <- runDR(sce, dr = 'UMAP', features = 'type')
sce <- runDR(sce, dr = 'TSNE', features = 'type')

# Visualize by cluster and by metadata
plotDR(sce, 'UMAP', color_by = 'meta20')
plotDR(sce, 'UMAP', color_by = 'batch')
```

## Cluster Annotation & Merging

_modules: annotation, heatmap, merging, k-selection_

```r
# Choose K: NRS plot and heatmap comparison
plotNRS(sce, features = 'type')
plotExprHeatmap(sce, features = 'type', by = 'cluster_id', k = 'meta10')
plotExprHeatmap(sce, features = 'type', by = 'cluster_id', k = 'meta20',
                scale = 'first', row_anno = FALSE)

# Manual cluster -> cell type mapping
cluster_annotation <- c(
    '1' = 'CD4 T cells',
    '2' = 'CD8 T cells',
    '3' = 'B cells',
    '4' = 'NK cells',
    '5' = 'Monocytes'
)
sce$cell_type <- cluster_annotation[as.character(cluster_ids(sce, 'meta20'))]

# Merge over-clustered groups into broader populations
merging_table <- data.frame(
    original = 1:20,
    merged = c(1, 1, 2, 2, 3, 3, 4, 4, 5, 5,
               6, 6, 7, 7, 8, 8, 9, 9, 10, 10)
)
sce <- mergeClusters(sce, k = 'meta20', table = merging_table, id = 'merged')
```

## Abundance & Marker Expression Analysis

_modules: abundance, marker-expression, pseudo-bulk_

```r
# Per-sample cluster frequencies
abundances <- table(cluster_ids(sce, 'meta20'), sce$sample_id)
freq <- prop.table(abundances, margin = 2)

# Abundance by condition
plotAbundances(sce, k = 'meta20', by = 'cluster_id', group_by = 'condition')

# Median expression per cluster
plotClusterExprs(sce, k = 'meta20', features = 'type')

# Pseudo-bulk expression by cluster
plotPbExprs(sce, k = 'meta20', features = 'type', facet_by = 'cluster_id')
```

## Export & Batch Integration

_modules: export, batch-correction, batchelor_

```r
# --- Export ---
colData(sce)$cluster <- cluster_ids(sce, 'meta20')
results <- as.data.frame(colData(sce))
write.csv(results, 'clustering_results.csv', row.names = FALSE)
saveRDS(sce, 'sce_clustered.rds')

# --- Batch integration (if needed) ---
library(batchelor)
# Detect batch effects on the embedding
plotDR(sce, 'UMAP', color_by = 'batch')
# MNN correction
sce_corrected <- fastMNN(sce, batch = sce$batch)
```
