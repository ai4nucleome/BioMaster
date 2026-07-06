## Pre-annotation marker inspection

_modules: marker-genes, qc-check, umap, dotplot_

```python
import scanpy as sc

adata = sc.read_h5ad("results/processed.h5ad")

# canonical lineage markers (example: immune lineages)
markers = ["CD3D", "CD3E", "CD8A", "CD4", "MS4A1", "CD79A",
           "GNLY", "NKG7", "CD14", "LYZ", "FCGR3A", "PPBP"]

# UMAP colored by marker expression
sc.pl.umap(adata, color=markers, ncols=4, save="_markers.pdf")

# dotplot of markers per cluster
sc.pl.dotplot(adata, var_names=markers, groupby="leiden", save="_markers.pdf")
```

Verify environment versions before relying on API patterns:
```bash
python -c "import scanpy, celltypist; print(scanpy.__version__, celltypist.__version__)"
```
Expected: scanpy 1.10+, celltypist 1.6+, pandas 2.2+.

## Annotation level selection

_modules: strategy, label-level, model-selection_

```python
# Decision guide (choose label_level before running annotation):
# - broad:   reference imperfect / atlas mismatch severe / sparse data
# - fine:    markers AND reference agree, conf_score typically high
# - cluster: noisy/sparse datasets, single-cell predictions unstable
label_level = "broad"  # "broad" | "fine" | "cluster"

# pick a CellTypist model matching the chosen level
# broad lineage example: Immune_All_Low.pkl covers major immune lineages
# fine-grained example:  use a subtype model only when markers support it
model_name = "Immune_All_Low.pkl"
```

## Reference-based annotation

_modules: celltypist, reference-transfer, majority-voting, confidence_

```python
import scanpy as sc
import celltypist

adata = sc.read_h5ad("results/processed.h5ad")

pred = celltypist.annotate(
    adata,
    model="Immune_All_Low.pkl",
    majority_voting=True,
)
adata = pred.to_adata()

# preserve raw prediction, confidence, and provenance
adata.obs["cell_type_raw"] = adata.obs["majority_voting"]
adata.obs["cell_type_confidence"] = adata.obs["conf_score"]
adata.obs["annotation_model"] = "Immune_All_Low.pkl"
```

## Marker-guided curation

_modules: marker-genes, curation, confidence, rank-genes, wilcoxon_

```python
import numpy as np
import scanpy as sc

# top markers per cluster
sc.tl.rank_genes_groups(adata, groupby="leiden", method="wilcoxon")
sc.pl.rank_genes_groups(adata, n_genes=10, save="_top_markers.pdf")

# confidence-aware provisional label
def provisional_label(row):
    if row["cell_type_confidence"] > 0.5:
        return row["cell_type_raw"]
    elif row["cell_type_confidence"] >= 0.2:
        return "Uncertain"
    else:
        return "Unknown"

adata.obs["cell_type_final"] = adata.obs.apply(provisional_label, axis=1)

# collapse/renamed fine categories based on marker review, e.g.:
# adata.obs["cell_type_final"] = adata.obs["cell_type_final"].replace(
#     {"Temra": "Tem", "Tcm": "Tem"}
# )
```

## Export and visualization

_modules: export, visualization, umap, dotplot_

```python
import scanpy as sc

adata.write("results/annotated.h5ad")

# per-cell labels (raw + final + confidence)
adata.obs[["cell_type_raw", "cell_type_confidence", "cell_type_final"]].to_csv(
    "results/cell_labels.tsv", sep="\t"
)

# cluster-level annotation summary (dominant final label per cluster)
summary = (
    adata.obs.groupby("leiden")["cell_type_final"]
    .agg(lambda s: s.value_counts().index[0])
    .reset_index()
)
summary.to_csv("results/cluster_annotation_summary.tsv", sep="\t", index=False)

# figures
sc.pl.umap(adata, color="cell_type_final", save="_cell_types.pdf")
sc.pl.dotplot(
    adata, var_names=markers, groupby="cell_type_final", save="_cell_types.pdf"
)
```
