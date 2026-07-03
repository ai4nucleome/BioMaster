## Inspect Markers Before Automation

_modules: marker-review, visualization_

```python
import scanpy as sc

adata = sc.read_h5ad("results/processed.h5ad")

# Define canonical lineage markers
marker_dict = {
    "T cell": ["CD3D", "IL7R"],
    "B cell": ["MS4A1", "CD79A"],
    "Monocyte": ["LYZ", "S100A8", "FCGR3A"],
}

# Visualize clusters and marker expression
sc.pl.umap(adata, color="leiden_r05", save="_clusters.pdf")
sc.pl.dotplot(adata, marker_dict, groupby="leiden_r05", save="_marker_check.pdf")
```

## Choose Annotation Level

_modules: strategy-selection_

```text
# Decision step — no code execution required.
# Document the chosen strategy in adata.obs["annotation_notes"].
```

## Run Reference-Based Annotation

_modules: celltypist, reference-transfer, majority-voting_

```python
import scanpy as sc
import celltypist

adata = sc.read_h5ad("results/processed.h5ad")

# Select a pre-trained CellTypist model
model = "Immune_All_Low.pkl"

# Run annotation with majority voting
pred = celltypist.annotate(adata, model=model, majority_voting=True)
adata = pred.to_adata()

# Store raw predictions and metadata
adata.obs["cell_type_raw"] = adata.obs["majority_voting"]
adata.obs["cell_type_confidence"] = adata.obs["conf_score"]
adata.obs["annotation_model"] = model

adata.write("results/annotated.h5ad")
```

## Curate with Markers and Cluster Context

_modules: curation, confidence-scoring, marker-validation_

```python
import scanpy as sc

adata = sc.read_h5ad("results/annotated.h5ad")

# Apply confidence thresholds to create curated labels
adata.obs["cell_type_final"] = adata.obs["cell_type_raw"]

# Low confidence -> Unknown
adata.obs.loc[adata.obs["cell_type_confidence"] < 0.2, "cell_type_final"] = "Unknown"

# Medium confidence -> mark as uncertain
uncertain_mask = (adata.obs["cell_type_confidence"] >= 0.2) & (adata.obs["cell_type_confidence"] <= 0.5)
adata.obs.loc[uncertain_mask, "cell_type_final"] = adata.obs.loc[uncertain_mask, "cell_type_raw"] + "_uncertain"

# Visualize final labels
sc.pl.umap(adata, color=["leiden_r05", "cell_type_final", "cell_type_confidence"], save="_cell_types.pdf")
sc.pl.dotplot(adata, marker_dict, groupby="cell_type_final", save="_marker_dotplot.pdf")

adata.write("results/annotated.h5ad")
```

## Export Labels

_modules: export, output_

```python
import scanpy as sc
import pandas as pd

adata = sc.read_h5ad("results/annotated.h5ad")

# Save per-cell labels
label_cols = ["cell_type_raw", "cell_type_confidence", "cell_type_final", "annotation_model"]
adata.obs[label_cols].to_csv("results/cell_labels.tsv", sep="\t")

# Generate cluster-level annotation summary
cluster_summary = (
    adata.obs.groupby("leiden_r05")["cell_type_final"]
    .agg(lambda x: x.value_counts().index[0])
    .reset_index()
)
cluster_summary.columns = ["cluster", "majority_label"]
cluster_summary.to_csv("results/cluster_annotation_summary.tsv", sep="\t", index=False)
```
