## Input Preparation & Preprocessing

_modules: input-prep, version-check, velocyto, format-conversion_

```bash
# Version checks before running
# Python: pip show <package>; then help(module.function) to check signatures
# R: packageVersion('<pkg>'); then ?function_name to verify parameters
# CLI: <tool> --version; then <tool> --help to confirm flags

# Generate spliced/unspliced loom from Cell Ranger output
velocyto run10x -m repeat_mask.gtf /path/to/cellranger_output annotation.gtf

# For SmartSeq2
velocyto run_smartseq2 -o output -m repeat_mask.gtf -e sample bam_files/*.bam annotation.gtf
```

```r
library(monocle3)
# Convert Seurat to cell_data_set for Monocle3
cds <- as.cell_data_set(seurat_obj)

library(slingshot)
library(SingleCellExperiment)
# Convert Seurat to SCE for Slingshot; carry over UMAP embedding
sce <- as.SingleCellExperiment(seurat_obj)
reducedDims(sce)$UMAP <- Embeddings(seurat_obj, 'umap')
```

```python
import scvelo as scv
# Load AnnData and merge velocyto loom for scVelo
adata = scv.read('data.h5ad')
ldata = scv.read('velocyto_output.loom')
adata = scv.utils.merge(adata, ldata)
```

## Dimensionality Reduction & Clustering

_modules: preprocessing, pca, umap, clustering_

```r
library(monocle3)
# Preprocess CDS if not already done
cds <- preprocess_cds(cds, num_dim = 50)
cds <- reduce_dimension(cds, reduction_method = 'UMAP')
cds <- cluster_cells(cds)
```

# For Slingshot/PAGA: ensure cluster labels and UMAP are present on the object
# (e.g. seurat_clusters on the SCE, leiden on the AnnData) before proceeding.

## Trajectory Graph Construction

_modules: principal-graph, mst, principal-curves, paga_

```r
# Monocle3: learn principal graph through the manifold
cds <- learn_graph(cds)

# Slingshot: MST over cluster centroids + principal curves (basic)
sce <- slingshot(sce, clusterLabels = 'seurat_clusters', reducedDim = 'UMAP')
curves <- slingCurves(sce)

# Slingshot: specify start and end clusters
sce <- slingshot(sce, clusterLabels = 'seurat_clusters', reducedDim = 'UMAP',
                 start.clus = 'HSC', end.clus = c('Erythroid', 'Myeloid'))
```

```python
import scanpy as sc
# PAGA: abstracted connectivity graph over clusters
sc.tl.paga(adata, groups='leiden')
sc.pl.paga(adata, color='leiden', threshold=0.03)
sc.tl.draw_graph(adata, init_pos='paga')
sc.pl.draw_graph(adata, color='leiden')
```

## Pseudotime Ordering & Root Selection

_modules: pseudotime, root-selection, ordering, dpt_

```r
# Monocle3: programmatically find root node from a progenitor cluster
get_earliest_principal_node <- function(cds, cluster_name) {
    cell_ids <- which(colData(cds)$seurat_clusters == cluster_name)
    closest_vertex <- cds@principal_graph_aux[['UMAP']]$pr_graph_cell_proj_closest_vertex
    closest_vertex <- as.matrix(closest_vertex[cell_ids, ])
    root_pr_nodes <- igraph::V(principal_graph(cds)[['UMAP']])$name[as.numeric(names(which.max(table(closest_vertex))))]
    root_pr_nodes
}
cds <- order_cells(cds, root_pr_nodes = get_earliest_principal_node(cds, 'stem_cluster'))
pseudotime <- pseudotime(cds)

# Plot trajectory with pseudotime
plot_cells(cds, color_cells_by = 'pseudotime', label_branch_points = TRUE, label_leaves = TRUE)

# Slingshot: per-lineage pseudotime matrix
pseudotime_mat <- slingPseudotime(sce)
```

```python
import numpy as np
import scanpy as sc
# PAGA / diffusion pseudotime
adata.uns['iroot'] = np.flatnonzero(adata.obs['leiden'] == 'root_cluster')[0]
sc.tl.dpt(adata)
sc.pl.draw_graph(adata, color='dpt_pseudotime')
```

## RNA Velocity Estimation

_modules: rna-velocity, scvelo, stochastic, dynamical, velocity-graph_

```python
import scvelo as scv

# Preprocess spliced/unspliced counts
scv.pp.filter_and_normalize(adata, min_shared_counts=20, n_top_genes=2000)
scv.pp.moments(adata, n_pcs=30, n_neighbors=30)

# Stochastic model (fast)
scv.tl.velocity(adata, mode='stochastic')
scv.tl.velocity_graph(adata)
scv.pl.velocity_embedding_stream(adata, basis='umap', color='clusters')

# Dynamical model (more accurate but slower)
scv.tl.recover_dynamics(adata, n_jobs=8)
scv.tl.velocity(adata, mode='dynamical')
scv.tl.velocity_graph(adata)

# Latent time (model-derived pseudotime)
scv.tl.latent_time(adata)
scv.pl.scatter(adata, color='latent_time', cmap='gnuplot')

# Velocity confidence
scv.tl.velocity_confidence(adata)
scv.pl.scatter(adata, color=['velocity_confidence', 'velocity_length'])
```

## Branch Point & Gene Dynamics Analysis

_modules: branch-points, gene-dynamics, morans-i, tradeseq, rank-velocity-genes_

```r
# Monocle3: genes varying over pseudotime (Moran's I)
graph_test_res <- graph_test(cds, neighbor_graph = 'principal_graph', cores = 4)
sig_genes <- graph_test_res %>% filter(q_value < 0.05) %>% arrange(desc(morans_I))
plot_genes_in_pseudotime(cds[rownames(cds) %in% top_genes, ], color_cells_by = 'cluster')

# tradeSeq: branch point analysis on Slingshot lineages
library(tradeSeq)
sce <- fitGAM(sce, nknots = 6)
branch_res <- earlyDETest(sce, knots = c(3, 4))
```

```python
# scVelo: rank velocity genes by likelihood and inspect phase portraits
scv.tl.rank_velocity_genes(adata, groupby='clusters', min_corr=0.3)
top_genes = adata.uns['rank_velocity_genes']['names']
scv.pl.velocity(adata, var_names=['gene1', 'gene2'], basis='umap')
```
