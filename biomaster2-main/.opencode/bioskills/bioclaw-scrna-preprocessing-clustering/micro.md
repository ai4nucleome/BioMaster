## Load And Validate

_modules: data-io, anndata, var-names_

```python
import scanpy as sc

adata = sc.read_h5ad("input.h5ad")  # or sc.read_10x_mtx("counts/")
adata.var_names_make_unique()
adata.var["mt"] = adata.var_names.str.upper().str.startswith("MT-")
```

## Compute QC Metrics

_modules: qc, qc-metrics, violin-plot_

```python
sc.pp.calculate_qc_metrics(adata, qc_vars=["mt"], inplace=True)
sc.pl.violin(adata, ["n_genes_by_counts", "total_counts", "pct_counts_mt"], jitter=0.4, multi_panel=True, save="_qc_violin.pdf")
```

## Filter Cells And Genes

_modules: filtering, doublet-removal, thresholds_

```python
adata = adata[(adata.obs["n_genes_by_counts"] >= 200)
    & (adata.obs["n_genes_by_counts"] <= 6000)
    & (adata.obs["pct_counts_mt"] < 15), :].copy()
sc.pp.filter_genes(adata, min_cells=3)
```

Threshold defaults: `min_genes=200`, `max_genes=6000`, `pct_counts_mt<15`, `min_cells=3`.

## Normalize And Select HVGs

_modules: normalization, log1p, highly-variable-genes, scaling_

```python
sc.pp.normalize_total(adata, target_sum=1e4)
sc.pp.log1p(adata)
adata.raw = adata.copy()
sc.pp.highly_variable_genes(adata, flavor="seurat_v3", n_top_genes=3000)
adata = adata[:, adata.var["highly_variable"]].copy()
sc.pp.scale(adata, max_value=10)
```

## Reduce Dimensions And Cluster

_modules: pca, neighbors, umap, leiden, clustering_

```python
sc.tl.pca(adata, svd_solver="arpack")
sc.pp.neighbors(adata, n_neighbors=15, n_pcs=30)
sc.tl.umap(adata)
for res in [0.2, 0.5, 0.8, 1.0]:
    sc.tl.leiden(adata, resolution=res, key_added=f"leiden_{res}")
```

## Export Analysis-Ready Artifacts

_modules: export, h5ad, qc-report_

```python
adata.write("results/processed.h5ad")
adata.obs[["leiden_0.5"]].to_csv("results/cluster_assignments.tsv", sep="\t")
```

Outputs: `results/processed.h5ad`, `results/cluster_assignments.tsv`, `qc/filter_summary.tsv`, `figures/qc_violin.pdf`, `figures/umap_leiden_0.5.pdf`.
