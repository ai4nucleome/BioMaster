## Marker Detection

_modules: rank-genes, differential-expression, wilcoxon_

```python
# === Scanpy (Python) ===
import scanpy as sc
import pandas as pd

# Find marker genes for each cluster vs all others (Wilcoxon rank-sum, default/recommended)
sc.tl.rank_genes_groups(adata, groupby='leiden', method='wilcoxon')

# Alternative methods:
# sc.tl.rank_genes_groups(adata, groupby='leiden', method='t-test')
# sc.tl.rank_genes_groups(adata, groupby='leiden', method='logreg')

# View top markers per cluster
sc.pl.rank_genes_groups(adata, n_genes=10, sharey=False)

# Get full results as a DataFrame
markers = sc.get.rank_genes_groups_df(adata, group=None)
print(markers.head(20))

# Compare two specific clusters (cluster 0 vs reference cluster 1)
sc.tl.rank_genes_groups(adata, groupby='leiden', groups=['0'], reference='1', method='wilcoxon')
sc.pl.rank_genes_groups(adata, n_genes=10)
```

```r
# === Seurat (R) ===
library(Seurat)
library(dplyr)

# Find markers for all clusters (positive markers only, default thresholds)
all_markers <- FindAllMarkers(seurat_obj, only.pos = TRUE, min.pct = 0.25, logfc.threshold = 0.25)

top_markers <- all_markers %>%
    group_by(cluster) %>%
    slice_max(n = 5, order_by = avg_log2FC)
print(top_markers)

# Markers for a single cluster vs all others
cluster0_markers <- FindMarkers(seurat_obj, ident.1 = 0, min.pct = 0.25)

# Markers between two specific clusters
markers_0_vs_1 <- FindMarkers(seurat_obj, ident.1 = 0, ident.2 = 1, min.pct = 0.25)

# Method selection via test.use: 'wilcox' (default), 'MAST', 'DESeq2', 'LR'
# markers <- FindMarkers(seurat_obj, ident.1 = 0, test.use = 'MAST')
```

## Marker Filtering & Visualization

_modules: filtering, visualization, dotplot, heatmap_

```python
# === Scanpy (Python) ===
# Filter markers for a single cluster by significance and fold change
markers = sc.get.rank_genes_groups_df(adata, group='0')
significant = markers[(markers['pvals_adj'] < 0.05) & (markers['logfoldchanges'] > 1)]
print(f'Cluster 0 significant markers: {len(significant)}')

# Apply global filtering across all groups
sc.tl.filter_rank_genes_groups(adata, min_fold_change=1.5, min_in_group_fraction=0.25)

# Visualize canonical marker set across clusters
markers_to_plot = ['CD3D', 'CD8A', 'MS4A1', 'CD14', 'FCGR3A', 'NKG7']
sc.pl.dotplot(adata, var_names=markers_to_plot, groupby='leiden')
sc.pl.stacked_violin(adata, var_names=markers_to_plot, groupby='leiden')
sc.pl.rank_genes_groups_heatmap(adata, n_genes=5, groupby='leiden')
sc.pl.matrixplot(adata, var_names=markers_to_plot, groupby='leiden')
```

```r
# === Seurat (R) ===
# Feature plot on UMAP
FeaturePlot(seurat_obj, features = c('CD3D', 'MS4A1', 'CD14', 'NKG7'))

# Violin plot
VlnPlot(seurat_obj, features = c('CD3D', 'MS4A1', 'CD14'))

# Dot plot
markers_to_plot <- c('CD3D', 'CD8A', 'MS4A1', 'CD14', 'FCGR3A', 'NKG7')
DotPlot(seurat_obj, features = markers_to_plot) + RotatedAxis()

# Heatmap of top 10 markers per cluster
top10 <- all_markers %>%
    group_by(cluster) %>%
    top_n(n = 10, wt = avg_log2FC)
DoHeatmap(seurat_obj, features = top10$gene)
```

## Gene Set & Cell Cycle Scoring

_modules: gene-scoring, cell-cycle, module-score_

```python
# === Scanpy (Python) ===
# Score cells for a custom gene set
t_cell_genes = ['CD3D', 'CD3E', 'CD4', 'CD8A', 'CD8B']
sc.tl.score_genes(adata, gene_list=t_cell_genes, score_name='T_cell_score')
sc.pl.umap(adata, color='T_cell_score')

# Cell cycle scoring
s_genes = ['MCM5', 'PCNA', 'TYMS', 'FEN1', 'MCM2']      # S phase
g2m_genes = ['HMGB2', 'CDK1', 'NUSAP1', 'UBE2C', 'BIRC5']  # G2/M
sc.tl.score_genes_cell_cycle(adata, s_genes=s_genes, g2m_genes=g2m_genes)
sc.pl.umap(adata, color=['S_score', 'G2M_score', 'phase'])
```

```r
# === Seurat (R) ===
# Score cells for a gene module
t_cell_genes <- list(c('CD3D', 'CD3E', 'CD4', 'CD8A', 'CD8B'))
seurat_obj <- AddModuleScore(seurat_obj, features = t_cell_genes, name = 'T_cell_score')
FeaturePlot(seurat_obj, features = 'T_cell_score1')

# Cell cycle scoring with built-in gene lists
s.genes <- cc.genes$s.genes
g2m.genes <- cc.genes$g2m.genes
seurat_obj <- CellCycleScoring(seurat_obj, s.features = s.genes, g2m.features = g2m.genes)
DimPlot(seurat_obj, group.by = 'Phase')
```

## Cell Type Annotation

_modules: annotation, cell-type, manual-annotation_

```python
# === Scanpy (Python) ===
# Map leiden cluster IDs to cell types (example for PBMC data)
cluster_annotations = {
    '0': 'CD4 T cells',
    '1': 'CD14 Monocytes',
    '2': 'B cells',
    '3': 'CD8 T cells',
    '4': 'NK cells',
    '5': 'FCGR3A Monocytes'
}
adata.obs['cell_type'] = adata.obs['leiden'].map(cluster_annotations)
sc.pl.umap(adata, color='cell_type')
```

```r
# === Seurat (R) ===
new_cluster_ids <- c(
    '0' = 'CD4 T cells',
    '1' = 'CD14 Monocytes',
    '2' = 'B cells',
    '3' = 'CD8 T cells',
    '4' = 'NK cells',
    '5' = 'FCGR3A Monocytes'
)
seurat_obj <- RenameIdents(seurat_obj, new_cluster_ids)
DimPlot(seurat_obj, reduction = 'umap', label = TRUE)

# Persist labels in metadata
seurat_obj$cell_type <- Idents(seurat_obj)
```

Reference PBMC markers: CD4 T cells (CD3D, CD4, IL7R); CD8 T cells (CD3D, CD8A, CD8B); B cells (MS4A1, CD79A, CD19); NK cells (NKG7, GNLY, NCAM1); CD14 Monocytes (CD14, LYZ, S100A8); FCGR3A Monocytes (FCGR3A, MS4A7); Dendritic cells (FCER1A, CST3); Platelets (PPBP, PF4).

## Export

_modules: export, csv_

```python
# === Scanpy (Python) ===
# Export all markers to CSV
markers = sc.get.rank_genes_groups_df(adata, group=None)
markers.to_csv('all_markers.csv', index=False)

# Export top markers per cluster
top_markers = markers.groupby('group').head(20)
top_markers.to_csv('top_markers.csv', index=False)
```

```r
# === Seurat (R) ===
write.csv(all_markers, file = 'all_markers.csv', row.names = FALSE)
write.csv(top_markers, file = 'top_markers.csv', row.names = FALSE)
```
