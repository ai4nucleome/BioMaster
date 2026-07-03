## Input Validation & Loading

_modules: input-validation, loading, raw-counts_

```python
import scanpy as sc
import numpy as np
from pathlib import Path

# Load raw-count .h5ad or 10x Matrix Market directory
if str(input_path).endswith(".h5ad"):
    adata = sc.read_h5ad(input_path)
else:
    adata = sc.read_10x_mtx(str(input_path), var_names="gene_symbols", cache=True)

# Reject processed-like matrices: raw counts must be non-negative integers
X = adata.X
if hasattr(X, "data"):
    vals = X.data
else:
    vals = X
if not np.allclose(vals, np.round(vals)) or np.nanmax(vals) > 1e6:
    raise ValueError(
        "Input appears to be a processed (normalized) matrix; provide raw counts."
    )

# Preserve raw counts for scVI training
adata.layers["counts"] = adata.X.copy()
```

```bash
# Standard / batch-aware / scANVI / 10x / demo invocations
python skills/scrna-embedding/scrna_embedding.py --input <input.h5ad> --output <report_dir>
python skills/scrna-embedding/scrna_embedding.py --input <input.h5ad> --output <report_dir> --batch-key sample_id
python skills/scrna-embedding/scrna_embedding.py --input <input.h5ad> --output <report_dir> --method scanvi --labels-key cell_type --unlabeled-category Unknown
python skills/scrna-embedding/scrna_embedding.py --input <filtered_feature_bc_matrix_dir> --output <report_dir>
python skills/scrna-embedding/scrna_embedding.py --demo --output <report_dir>
python clawbio.py run scrna-embedding --input <input.h5ad> --output <report_dir>
python clawbio.py run scrna-embedding --demo
```

## QC & Feature Selection

_modules: qc, normalization, hvg, feature-selection_

```python
import scanpy as sc

# QC metrics with mitochondrial flag
adata.var["mt"] = adata.var_names.str.startswith("MT-")
sc.pp.calculate_qc_metrics(adata, qc_vars=["mt"], inplace=True)

# Filter cells and genes, then drop high-mito cells
sc.pp.filter_cells(adata, min_genes=min_genes)        # default min_genes
sc.pp.filter_genes(adata, min_cells=min_cells)        # default min_cells
adata = adata[adata.obs["pct_counts_mt"] < max_mt_pct].copy()

# Keep raw counts; build a normalized log1p branch for HVG selection
adata.layers["counts"] = adata.X.copy()
sc.pp.normalize_total(adata, target_sum=1e4)
sc.pp.log1p(adata)

# Select HVGs (Seurat flavor) to scope scVI training
sc.pp.highly_variable_genes(adata, n_top_genes=2000, flavor="seurat", subset=True)
```

## Latent Model Training

_modules: scvi, scanvi, latent-embedding, batch-correction_

```python
import scvi

# Register raw counts; include batch covariate when --batch-key is provided
scvi.model.SCVI.setup_anndata(
    adata,
    layer="counts",
    batch_key=batch_key,        # None or e.g. "sample_id"
)

# Train scVI on HVG raw counts
model = scvi.model.SCVI(adata, n_layers=2, n_latent=30, gene_likelihood="nb")
model.train(max_epochs=200, early_stopping=True)

# Optional scANVI refinement with explicit labels
if method == "scanvi" and labels_key is not None:
    model = scvi.model.SCANVI(
        adata,
        unlabeled_category=unlabeled_category,
        labels_key=labels_key,
    )
    model.train(max_epochs=200, early_stopping=True)

# Export latent representation
adata.obsm["X_scvi"] = model.get_latent_representation()
```

## Latent Projection & UMAP

_modules: neighbors, umap, latent-projection_

```python
import scanpy as sc
import pandas as pd
from pathlib import Path

# Neighbors + UMAP in the learned latent space
sc.pp.neighbors(adata, use_rep="X_scvi", n_neighbors=15)
sc.tl.umap(adata)

# Export per-cell latent coordinates
latent_df = pd.DataFrame(adata.obsm["X_scvi"], index=adata.obs_names)
latent_df.to_csv(Path(output_dir) / "tables" / "latent_embeddings.csv")

# UMAP figure (batch-colored when --batch-key is set)
if batch_key is not None:
    sc.pl.umap(adata, color=batch_key, save="_scvi_batch.png", show=False)
sc.pl.umap(adata, save="_scvi_latent.png", show=False)
```

## Diagnostics, Export & Reporting

_modules: batch-diagnostics, export, reporting, reproducibility_

```python
import pandas as pd
from pathlib import Path

# Batch-mixing diagnostics when --batch-key is provided
if batch_key is not None:
    metrics = compute_batch_mixing(adata, batch_key=batch_key)
    # returns: cross-batch neighbor fraction, neighbor entropy, batch silhouette
    pd.DataFrame([metrics]).to_csv(
        Path(output_dir) / "tables" / "batch_mixing_metrics.csv", index=False
    )

# Save integrated AnnData: log-normalized X, raw counts in layers, X_scvi in obsm
adata.write_h5ad(Path(output_dir) / "integrated.h5ad")

# Reproducibility bundle
write_reproducibility(
    Path(output_dir),
    commands=cmd_str,        # exact invocation -> commands.sh
    env=env_dict,            # pinned versions -> environment.yml
    checksums=True,          # -> checksums.sha256
)

# report.md + result.json with downstream recommendation:
#   scrna-orchestrator --use-rep X_scvi
write_report(Path(output_dir), adata, method=method, batch_key=batch_key)
```

```text
output_directory/
├── report.md
├── result.json
├── integrated.h5ad
├── figures/
│   ├── umap_scvi_latent.png
│   └── umap_scvi_batch.png           # only when batch integration is enabled
├── tables/
│   ├── latent_embeddings.csv
│   └── batch_mixing_metrics.csv      # only when batch integration is enabled
└── reproducibility/
    ├── commands.sh
    ├── environment.yml
    └── checksums.sha256
```
