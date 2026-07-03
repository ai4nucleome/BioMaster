## Method Selection & Input Preparation

_modules: method-selection, normalization, scaling_

```python
# Decision guide (choose by question):
#   batch diagnostic / variance explained / loadings -> PCA
#   broad cluster overview                          -> UMAP (n_neighbors=30, min_dist=0.3)
#   crisp cluster boundaries                        -> t-SNE (Kobak-Berens defaults)
#   continuous trajectories / branching             -> PHATE or diffusion map

# Input prep -- single-cell (Python): normalize + scale so PCA captures biology, not library size
import scanpy as sc
sc.pp.normalize_total(adata, target_sum=1e4)
sc.pp.log1p(adata)
sc.pp.highly_variable_genes(adata, n_top_genes=2000, flavor='seurat_v3')
sc.pp.scale(adata, max_value=10)

# Input prep -- bulk RNA-seq (R): variance-stabilize before PCA
#   vsd <- DESeq2::vst(dds, blind = FALSE)

# Verify versions before running; introspect API on mismatch:
#   pip show scanpy umap-learn openTSNE phate
```

## PCA — Variance & Loadings

_modules: pca, variance-explained, loadings, batch-diagnostic_

```r
# R: DESeq2 + PCAtools -- bulk RNA-seq sample QC
library(DESeq2); library(PCAtools); library(ggplot2)
vsd <- vst(dds, blind = FALSE)
p <- pca(assay(vsd), metadata = as.data.frame(colData(dds)))
biplot(p, colby = 'condition', shape = 'batch', lab = NULL,
       hline = 0, vline = 0, legendPosition = 'right',
       title = paste0('PCA: PC1 (', round(p$variance[1], 1),
                      '%) vs PC2 (', round(p$variance[2], 1), '%)'))
screeplot(p, components = 1:10)
plotloadings(p, components = 1, rangeRetain = 0.05)
```

```python
# Python: sklearn PCA with variance-explained axis labels
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt

pca = PCA(n_components=10)
X_pca = pca.fit_transform(X)            # X must be scaled/normalized first
var = pca.explained_variance_ratio_

fig, axes = plt.subplots(1, 2, figsize=(10, 4))
axes[0].scatter(X_pca[:, 0], X_pca[:, 1], c=labels, alpha=0.7)
axes[0].set_xlabel(f'PC1 ({var[0]*100:.1f}%)')
axes[0].set_ylabel(f'PC2 ({var[1]*100:.1f}%)')
axes[1].plot(range(1, 11), var, 'o-')
axes[1].set_xlabel('PC'); axes[1].set_ylabel('Variance explained')
```

## t-SNE — Kobak-Berens Defaults

_modules: tsne, perplexity, pca-initialization_

```python
# Python: openTSNE with Kobak-Berens 2019 modern defaults
import openTSNE

embedding = openTSNE.TSNE(
    perplexity=30,                       # 30-50 for n>1000; max(5, n/30) for n<500
    n_iter=750,
    initialization='pca',                # NOT random -- recovers global structure
    learning_rate=X.shape[0] / 12,       # scales with n; default 200 over-shrinks large data
    exaggeration=12,                     # early exaggeration for large data
    n_jobs=-1,
    random_state=42).fit(X)
```

```r
# R: Rtsne (no native PCA init -- supply via Y_init= if needed)
library(Rtsne)
set.seed(42)
ts <- Rtsne(X, perplexity = 30, theta = 0.5, pca_scale = TRUE,
            initial_dims = 50, max_iter = 750)
```

## UMAP — Modern Defaults

_modules: umap, n-neighbors, min-dist, reproducibility_

```python
# Python: umap-learn
import umap
reducer = umap.UMAP(
    n_neighbors=30,      # 15-50; local-vs-global balance
    min_dist=0.3,        # 0.1-0.5; cluster tightness, NOT separation
    n_components=2,
    metric='euclidean',
    random_state=42)     # always set -- UMAP is stochastic
embedding = reducer.fit_transform(X)
```

```r
# R: uwot
library(uwot)
set.seed(42)
um <- umap(X, n_neighbors = 30, min_dist = 0.3, metric = 'euclidean')
```

```python
# scanpy convention -- after sc.tl.pca, sc.pp.neighbors
sc.pp.neighbors(adata, n_neighbors=30, n_pcs=50)
sc.tl.umap(adata, min_dist=0.3, random_state=42)
sc.pl.umap(adata, color='leiden', palette='tab20', frameon=False,
           legend_loc='on data', legend_fontsize=7, save='_clusters.pdf')
# NOTE: save='_clusters.pdf' writes figures/umap_clusters.pdf (figdir + 'umap' prefix)
```

## PHATE — Continuous Trajectories

_modules: phate, trajectory, diffusion_

```python
# Python: PHATE for continuous trajectories / branching
import phate
import matplotlib.pyplot as plt

phate_op = phate.PHATE(knn=10, decay=40, t='auto', n_jobs=-1, random_state=42)
emb = phate_op.fit_transform(X)
plt.scatter(emb[:, 0], emb[:, 1], c=pseudotime, cmap='viridis', s=5)
plt.axis('off')
```

## Plotting, Saving & Reproducibility

_modules: visualization, saving, dpi, reproducibility, interpretation_

```python
# scanpy: publication DPI + explicit save path control
import scanpy as sc
import matplotlib.pyplot as plt

sc.settings.set_figure_params(dpi_save=300, figsize=(4, 4))
sc.settings.figdir = '/abs/path/to/figures/'     # set explicitly to avoid surprises

# Option A: scanpy save (writes figdir + 'umap' prefix + suffix)
sc.pl.umap(adata, color='leiden', save='_clusters.pdf')
# -> /abs/path/to/figures/umap_clusters.pdf

# Option B: full path control via matplotlib
ax = sc.pl.umap(adata, color='leiden', show=False)
ax.figure.savefig('/abs/path/to/umap_clusters.pdf', dpi=300, bbox_inches='tight')

# Report in caption/methods: n_neighbors, min_dist, n_pcs, random_state,
# and the interpretation limit (local neighborhoods preserved; global
# distances/densities/cluster shapes NOT meaningful -- Chari & Pachter 2023).
```
