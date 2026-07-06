## Setup and Data Loading

_modules: data-loading, anndata, setup_

```python
import scanpy as sc
import numpy as np
import pandas as pd

# Configure settings
sc.settings.verbosity = 3  # errors=0, warnings=1, info=2, hints=3
sc.settings.set_figure_params(dpi=80, facecolor="white")

# Load data — pick the reader matching your format
adata = sc.read_10x_mtx(
    "path/to/filtered_feature_bc_matrix/",
    var_names="gene_symbols",
    cache=True,
)
# Alternatives:
# adata = sc.read_h5ad("data.h5ad")
# adata = sc.read_10x_h5("data.h5")
# adata = sc.read_csv("counts.csv").T  # transpose if genes=rows
# adata = sc.read_loom("data.loom")

adata.var_names_make_unique()
print(f"Loaded: {adata.n_obs} cells x {adata.n_vars} genes")

# Multi-sample concatenation (optional)
# adatas = [sc.read_10x_mtx(f"sample_{i}/") for i in range(1, 4)]
# adata = adatas[0].concatenate(adatas[1:], batch_key="sample")
```

## Quality Control

_modules: qc, filtering, mitochondrial, doublet-detection_

```python
# Annotate gene groups (human; use lowercase mt-, Rps/Rpl, Hb for mouse)
adata.var["mt"] = adata.var_names.str.startswith("MT-")
adata.var["ribo"] = adata.var_names.str.startswith(("RPS", "RPL"))
adata.var["hb"] = adata.var_names.str.contains("^HB[^(P)]", case=False)

# Calculate QC metrics
sc.pp.calculate_qc_metrics(
    adata, qc_vars=["mt", "ribo", "hb"], percent_top=None, log1p=False, inplace=True
)

# Visualize QC distributions
sc.pl.violin(adata, ["n_genes_by_counts", "total_counts", "pct_counts_mt"],
             jitter=0.4, multi_panel=True)
sc.pl.scatter(adata, x="total_counts", y="pct_counts_mt")
sc.pl.scatter(adata, x="total_counts", y="n_genes_by_counts")

# Fixed-threshold filtering
sc.pp.filter_cells(adata, min_genes=200)
sc.pp.filter_genes(adata, min_cells=3)
adata = adata[adata.obs.n_genes_by_counts < 5000, :]  # remove potential doublets
adata = adata[adata.obs.pct_counts_mt < 20, :]         # remove dying cells
print(f"After QC: {adata.n_obs} cells x {adata.n_vars} genes")

# MAD-based filtering alternative (data-driven)
# from scipy.stats import median_abs_deviation
# def is_outlier(adata, metric, nmads=5):
#     M = adata.obs[metric]
#     return (M < np.median(M) - nmads * median_abs_deviation(M)) | \
#            (M > np.median(M) + nmads * median_abs_deviation(M))
# adata.obs["outlier"] = is_outlier(adata, "log1p_total_counts", 5) | \
#                        is_outlier(adata, "log1p_n_genes_by_counts", 5)
# adata.obs["mt_outlier"] = is_outlier(adata, "pct_counts_mt", 3)
# adata = adata[(~adata.obs.outlier) & (~adata.obs.mt_outlier)].copy()
```

## Normalization, Feature Selection, and Scaling

_modules: normalization, hvg, scaling, regression, feature-selection_

```python
# Preserve raw counts in a layer
adata.layers["counts"] = adata.X.copy()

# Normalize to 10,000 counts per cell, then log-transform
sc.pp.normalize_total(adata, target_sum=1e4)
sc.pp.log1p(adata)

# Save normalized data as .raw for visualization (before HVG subset)
adata.raw = adata

# Identify highly variable genes (seurat_v3 works on raw counts)
sc.pp.highly_variable_genes(adata, n_top_genes=2000, flavor="seurat_v3", layer="counts")
sc.pl.highly_variable_genes(adata)

# Subset to HVGs
adata = adata[:, adata.var.highly_variable]
print(f"HVG subset: {adata.n_obs} cells x {adata.n_vars} genes")

# Regress out confounders (optional; slow for large datasets)
sc.pp.regress_out(adata, ["total_counts", "pct_counts_mt"])

# Scale to unit variance, clip extreme values
sc.pp.scale(adata, max_value=10)
print(f"Scaled matrix: mean={adata.X.mean():.4f}, std={adata.X.std():.4f}")
```

## Dimensionality Reduction and Embedding

_modules: pca, neighbors, umap, dimensionality-reduction_

```python
# PCA
sc.tl.pca(adata, svd_solver="arpack", n_comps=50)
sc.pl.pca_variance_ratio(adata, log=True, n_pcs=50)

# Determine n_pcs from elbow plot (typically 30-50)
n_pcs = 40

# Compute k-nearest neighbor graph
sc.pp.neighbors(adata, n_neighbors=15, n_pcs=n_pcs)

# UMAP embedding
sc.tl.umap(adata)
sc.pl.umap(adata, color=["n_genes_by_counts", "total_counts", "pct_counts_mt"])
print(f"UMAP shape: {adata.obsm['X_umap'].shape}")
```

## Clustering

_modules: leiden, clustering, community-detection_

```python
# Test multiple resolutions
for res in [0.3, 0.5, 0.8, 1.0, 1.2]:
    sc.tl.leiden(adata, resolution=res, key_added=f"leiden_res{res}",
                 flavor="igraph", n_iterations=2)

# Compare resolutions side-by-side
sc.pl.umap(
    adata,
    color=["leiden_res0.3", "leiden_res0.5", "leiden_res0.8", "leiden_res1.0"],
    ncols=2, legend_loc="on data",
)

# Pick final resolution based on biological plausibility
adata.obs["leiden"] = adata.obs["leiden_res0.5"]
n_clusters = adata.obs["leiden"].nunique()
print(f"Selected resolution=0.5: {n_clusters} clusters")
```

## Marker Gene Identification

_modules: marker-genes, differential-expression, wilcoxon, rank-genes_

```python
# Rank genes per cluster (Wilcoxon on raw counts)
sc.tl.rank_genes_groups(adata, groupby="leiden", method="wilcoxon", use_raw=True)

# Visualization
sc.pl.rank_genes_groups(adata, n_genes=20, sharey=False)
sc.pl.rank_genes_groups_dotplot(adata, n_genes=5)
sc.pl.rank_genes_groups_heatmap(adata, n_genes=10, use_raw=True, show_gene_labels=True)

# Extract as DataFrame
markers_df = sc.get.rank_genes_groups_df(adata, group=None)
top_markers = markers_df[markers_df["pvals_adj"] < 0.05].groupby("group").head(10)
print(f"Significant markers: {len(top_markers)} genes across {top_markers['group'].nunique()} clusters")
print(top_markers[["group", "names", "logfoldchanges", "pvals_adj"]].head(15))
```

## Cell Type Annotation and Export

_modules: annotation, cell-type, export, visualization, dotplot_

```python
# Define canonical markers (example: human PBMC)
marker_genes = {
    "CD4 T cells":       ["CD3D", "CD3E", "IL7R"],
    "CD8 T cells":       ["CD8A", "CD8B", "GZMK"],
    "B cells":           ["MS4A1", "CD79A", "CD79B"],
    "NK cells":          ["NKG7", "GNLY", "KLRD1"],
    "CD14+ Monocytes":   ["CD14", "LYZ", "S100A9"],
    "FCGR3A+ Monocytes": ["FCGR3A", "MS4A7"],
    "Dendritic cells":   ["FCER1A", "CST3"],
    "Platelets":         ["PPBP", "PF4"],
}

# Dot plot — rows = clusters, columns = markers
sc.pl.dotplot(adata, var_names=marker_genes, groupby="leiden", use_raw=True)

# Map clusters -> cell types (adjust based on your dot plot)
cluster_to_celltype = {
    "0": "CD4 T cells", "1": "CD14+ Monocytes", "2": "B cells",
    "3": "CD8 T cells", "4": "NK cells", "5": "FCGR3A+ Monocytes",
    "6": "Dendritic cells", "7": "Platelets",
}
adata.obs["cell_type"] = adata.obs["leiden"].map(cluster_to_celltype).fillna("Unknown")
sc.pl.umap(adata, color="cell_type", legend_loc="on data", frameon=False)

# Save results
adata.write("results/annotated_data.h5ad", compression="gzip")
adata.obs.to_csv("results/cell_metadata.csv")
markers_df.to_csv("results/marker_genes.csv", index=False)
print(f"Saved: {adata.n_obs} cells with {adata.obs['cell_type'].nunique()} cell types")
```

## Advanced Analyses

_modules: batch-correction, combat, trajectory, paga, pseudotime, differential-expression, publication, visualization_

```python
# --- Recipe 1: Batch Correction with ComBat ---
# Requires 'batch' column in adata.obs; re-run PCA/neighbors/UMAP/clustering after
sc.pp.combat(adata, key="batch")
sc.tl.pca(adata, svd_solver="arpack")
sc.pp.neighbors(adata, n_pcs=40)
sc.tl.umap(adata)
sc.pl.umap(adata, color=["batch", "leiden"])

# --- Recipe 2: Trajectory Inference with PAGA + Diffusion Pseudotime ---
sc.tl.paga(adata, groups="leiden")
sc.pl.paga(adata, color="leiden", threshold=0.03)
sc.tl.umap(adata, init_pos="paga")  # reinitialize UMAP with PAGA layout
adata.uns["iroot"] = np.flatnonzero(adata.obs["leiden"] == "0")[0]  # set root cell
sc.tl.diffmap(adata)
sc.tl.dpt(adata)
sc.pl.umap(adata, color=["dpt_pseudotime", "leiden"])

# --- Recipe 3: Differential Expression Between Conditions ---
# Subset to cell type of interest, compare treated vs control
adata_t = adata[adata.obs["cell_type"] == "CD4 T cells"].copy()
sc.tl.rank_genes_groups(adata_t, groupby="condition", groups=["treated"],
                        reference="control", method="wilcoxon", use_raw=True)
sc.pl.rank_genes_groups_volcano(adata_t, groups=["treated"])
de_results = sc.get.rank_genes_groups_df(adata_t, group="treated")
sig_genes = de_results[de_results["pvals_adj"] < 0.05]
print(f"Significant DE genes: {len(sig_genes)}")

# --- Recipe 4: Publication-Quality Figures ---
sc.settings.set_figure_params(dpi=300, frameon=False, figsize=(5, 5))
sc.settings.figdir = "./figures/"
sc.settings.file_format_figs = "pdf"

# UMAP with custom palette
sc.pl.umap(adata, color="cell_type", palette="Set2", legend_loc="on data",
           legend_fontsize=10, legend_fontoutline=2, title="",
           save="_celltype_publication.pdf")

# Stacked violin of top markers
flat_markers = [g for genes in marker_genes.values() for g in genes[:2]]
sc.pl.stacked_violin(adata, var_names=flat_markers, groupby="cell_type",
                     use_raw=True, swap_axes=True, save="_markers_violin.pdf")

# Multi-panel figure with matplotlib
import matplotlib.pyplot as plt
fig, axes = plt.subplots(2, 3, figsize=(15, 10))
sc.pl.umap(adata, color="leiden", ax=axes[0, 0], show=False, title="Clusters")
sc.pl.umap(adata, color="cell_type", ax=axes[0, 1], show=False, title="Cell Types")
sc.pl.umap(adata, color="n_genes_by_counts", ax=axes[0, 2], show=False, title="nGenes")
sc.pl.umap(adata, color="CD3D", ax=axes[1, 0], show=False, use_raw=True, title="CD3D")
sc.pl.umap(adata, color="CD14", ax=axes[1, 1], show=False, use_raw=True, title="CD14")
sc.pl.umap(adata, color="MS4A1", ax=axes[1, 2], show=False, use_raw=True, title="MS4A1")
plt.tight_layout()
plt.savefig("figures/multi_panel.pdf", dpi=300, bbox_inches="tight")
plt.close()
```
