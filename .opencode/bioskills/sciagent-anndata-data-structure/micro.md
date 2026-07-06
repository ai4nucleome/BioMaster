## data_structure_io.md

# AnnData — Data Structure & I/O Reference

## Detailed Slot-by-Slot API

### The `raw` Attribute

Stores a frozen snapshot before gene filtering, preserving the full variable space for DE and plotting.

```python
import anndata as ad

adata = ad.read_h5ad("data.h5ad")
adata.raw = adata.copy()  # freeze BEFORE HVG filtering

hvg_mask = adata.var["highly_variable"]
adata = adata[:, hvg_mask].copy()
print(f"Filtered: {adata.n_vars} genes, raw preserved: {adata.raw.n_vars} genes")

# Access raw expression (for genes removed from filtered adata)
raw_df = adata.raw.to_adata().to_df()
# Scanpy uses raw automatically: sc.pl.umap(adata, color="CD3D") looks in raw
```

**Gotcha**: `adata.raw = adata` captures a *reference* at that moment. Subsequent in-place changes to `adata.X` do NOT propagate. Always assign raw *before* normalization/scaling.

### obsm Element Access Patterns

```python
import anndata as ad, numpy as np, pandas as pd

adata = ad.read_h5ad("data.h5ad")
pca = adata.obsm["X_pca"]              # (n_obs, 50) numpy array
pca_10 = adata.obsm["X_pca"][:, :10]   # first 10 PCs

for key in adata.obsm.keys():  # iterate all embeddings
    print(f"  {key}: shape={adata.obsm[key].shape}, dtype={adata.obsm[key].dtype}")

# obsm can hold DataFrames (named columns for protein/ADT data)
adata.obsm["protein"] = pd.DataFrame(
    np.random.rand(adata.n_obs, 5), index=adata.obs_names,
    columns=["CD3", "CD4", "CD8", "CD19", "CD56"])

subset = adata[:100]  # subsetting preserves obsm alignment
print(f"Subset obsm: {subset.obsm['X_pca'].shape}")  # (100, 50)
```

### uns Nested Structure Conventions

```python
adata = ad.read_h5ad("processed.h5ad")

# Neighbors params (written by sc.pp.neighbors)
# {"connectivities_key": "connectivities", "distances_key": "distances",
#  "params": {"n_neighbors": 15, "method": "umap", "metric": "euclidean"}}
print(f"Neighbor params: {adata.uns.get('neighbors', {}).get('params', {})}")

# Color palettes (written by sc.pl.* for categorical columns)
# Key format: "{column_name}_colors" -> list of hex strings
print(f"Palette: {adata.uns.get('cell_type_colors', [])}")
# Override: adata.uns["cell_type_colors"] = ["#e41a1c", "#377eb8", "#4daf4a"]

# Ranking results (written by sc.tl.rank_genes_groups)
# Keys: "params", "names", "scores", "pvals", "pvals_adj", "logfoldchanges"
# Each (except params) is a structured array with group names as fields

# Custom metadata (nested dicts serialize to HDF5 groups)
adata.uns["experiment"] = {"date": "2024-06-01", "protocol": "10x_v3",
                           "sequencing": {"platform": "NovaSeq"}}
```

**Serialization rules**: H5AD supports dicts, numpy arrays, strings, numbers, pandas categoricals. Arbitrary Python objects (sklearn models, lambdas) raise `IORegistryError` on save.

### varp Usage Patterns

Stores gene-gene pairwise relationships (regulatory networks, co-expression).

```python
import numpy as np
from scipy.sparse import csr_matrix

adata = ad.read_h5ad("data.h5ad")
corr = np.corrcoef(adata.X.toarray().T if hasattr(adata.X, 'toarray') else adata.X.T)
corr[np.abs(corr) < 0.5] = 0  # sparsify: keep strong correlations
adata.varp["gene_correlations"] = csr_matrix(corr.astype(np.float32))
print(f"varp shape: {adata.varp['gene_correlations'].shape}")  # (n_vars, n_vars)
```

---

## Advanced I/O Patterns

### Chunked Reading for Very Large Files

```python
import anndata as ad, numpy as np

adata_backed = ad.read_h5ad("huge_atlas.h5ad", backed="r")
chunk_size = 10000
results = []
for start in range(0, adata_backed.n_obs, chunk_size):
    end = min(start + chunk_size, adata_backed.n_obs)
    chunk = adata_backed[start:end].to_memory()
    results.append(np.array(chunk.X.sum(axis=1)).flatten())
all_totals = np.concatenate(results)
print(f"Processed {len(all_totals)} cells in {len(results)} chunks")

# Metadata-guided chunking (process by batch, avoids loading full dataset)
for batch in adata_backed.obs["batch"].unique():
    batch_data = adata_backed[adata_backed.obs["batch"] == batch].to_memory()
    print(f"  Batch {batch}: {batch_data.n_obs} cells")
```

### Backed Mode Write-Back (r+ Mode)

Allows in-place modification of the underlying HDF5 file. Changes to X are written immediately to disk with no extra memory cost.

```python
adata = ad.read_h5ad("data.h5ad", backed="r+")
# Modify X element-wise (writes directly to disk, no extra memory)
# adata.X[0, :] = 0  # written to file immediately

# Modify obs metadata (in-memory until file close)
adata.obs["processed"] = True

# LIMITATIONS: cannot change X shape, sparse format, or add new layers/obsm
# For structural changes: load subset to memory, modify, write new file
adata.file.close()
```

### Format Conversion Gotchas

```python
# Loom -> H5AD: row_attrs->var, col_attrs->obs, layers preserved
# row_graphs/col_graphs NOT mapped to obsp/varp; nested globals lost
adata = ad.read_loom("data.loom")
adata.write_h5ad("converted.h5ad", compression="gzip")

# CSV round-trip loses: sparse format, layers, obsm, obsp, uns, dtypes
# adata.to_df().to_csv("expr.csv")  # only X + index names

# 10X H5 -> H5AD: gene IDs in var_names, symbols in var["gene_symbols"]
adata = ad.read_10x_h5("filtered_feature_bc_matrix.h5")
adata.var_names = adata.var["gene_symbols"]
adata.var_names_make_unique()  # handle duplicate symbols
adata.write_h5ad("from_10x.h5ad", compression="gzip")
```

### Compression Comparison

```python
import anndata as ad, time, os

adata = ad.read_h5ad("data.h5ad")
for comp in ["gzip", "lzf", None]:
    t0 = time.time()
    fname = f"out_{comp or 'none'}.h5ad"
    adata.write_h5ad(fname, compression=comp)
    print(f"{comp or 'none':5s}: {os.path.getsize(fname)/1e6:.1f} MB, {time.time()-t0:.1f}s")
# Typical sparse scRNA-seq (50k x 20k):
# gzip: ~200 MB, ~15s | lzf: ~350 MB, ~5s | none: ~600 MB, ~3s
```

Use `gzip` for archival/sharing, `lzf` for iterative analysis, no compression for temp files. Read speed is similar across all three -- the bottleneck is decompression, which is fast for both gzip and lzf.

### H5AD Internal Structure (HDF5 Layout)

```python
import h5py

with h5py.File("data.h5ad", "r") as f:
    def show(name, obj):
        kind = "dataset" if isinstance(obj, h5py.Dataset) else "group"
        extra = f" {obj.shape} {obj.dtype}" if kind == "dataset" else ""
        print(f"  {name} ({kind}){extra}")
    f.visititems(show)

# Typical layout:
# X/data (nnz,) float32       <- sparse nonzero values
# X/indices (nnz,) int32      <- column indices (CSR)
# X/indptr (n_obs+1,) int32
# obs/cell_type (n_obs,)      <- categorical: codes + categories
# var/                         <- gene metadata
# layers/raw_counts/           <- same sparse structure as X
# obsm/X_pca (n_obs, 50)      <- dense embeddings
# obsp/connectivities/         <- sparse graphs
# uns/neighbors/params/        <- nested groups for dicts
```

---

## Zarr Advanced Patterns

### Cloud Storage (S3/GCS)

Zarr's directory-based format enables direct cloud read/write without downloading entire files.

```python
import anndata as ad

adata = ad.read_h5ad("data.h5ad")
adata.write_zarr("output.zarr")

# S3 (requires s3fs): store = s3fs.S3Map("s3://bucket/data.zarr", s3=s3fs.S3FileSystem())
# GCS (requires gcsfs): store = gcsfs.GCSMap("gs://bucket/data.zarr", gcs=gcsfs.GCSFileSystem())
# Then: adata = ad.read_zarr(store) / adata.write_zarr(store)
# Authenticated: s3 = s3fs.S3FileSystem(key="...", secret="...", endpoint_url="...")
```

### Chunk Size Selection

```python
adata.write_zarr("chunked.zarr", chunks=(1000, adata.n_vars))

# Chunk selection guide:
# Access pattern       | Recommended chunks          | Rationale
# Cell-wise iteration  | (1000-5000, n_vars)         | Full gene profile per read
# Gene-wise iteration  | (n_obs, 500-2000)           | Full cell vector per read
# Random subsets       | (500-1000, 500-1000)        | Balanced for either axis
# Cloud streaming      | Target ~1-10 MB per chunk   | Network transfer overhead
# Very sparse data     | Larger chunks (5000+)       | Sparse overhead per chunk

import zarr
z = zarr.open("chunked.zarr", "r")
if "X" in z and hasattr(z["X"], 'chunks'):
    print(f"Chunk shape: {z['X'].chunks}")
```

---

## Data Type Handling in I/O

### Sparse Format Preservation

```python
from scipy.sparse import csr_matrix, csc_matrix, issparse

adata = ad.read_h5ad("data.h5ad")
print(f"X type: {type(adata.X)}")  # e.g., csr_matrix

# H5AD preserves sparse format across read/write (CSR stays CSR, CSC stays CSC)
adata.write_h5ad("roundtrip.h5ad", compression="gzip")
adata_rt = ad.read_h5ad("roundtrip.h5ad")
print(f"After roundtrip: {type(adata_rt.X)}")  # csr_matrix preserved

# CSR = efficient for row (cell) slicing; CSC = efficient for column (gene) slicing
# Layers preserve sparse format independently (counts can be CSR while X is CSC)
# Zarr also preserves sparse format (stored as data/indices/indptr arrays)
# Force sparse on load: ad.read_h5ad("data.h5ad", as_sparse={"X": "csr"})
```

### Categorical and dtype Preservation

```python
import pandas as pd, numpy as np
from scipy.sparse import issparse

adata = ad.read_h5ad("data.h5ad")

# Categoricals preserved through I/O (stored as codes + categories in HDF5)
adata.strings_to_categoricals()  # convert before save (5-10x memory savings)
adata.obs["stage"] = pd.Categorical(["early", "mid", "late"] * (adata.n_obs // 3),
                                     categories=["early", "mid", "late"], ordered=True)
# Ordered categoricals, booleans, int32/64, float32/64 all preserved

# dtype casting: float64 -> float32 halves memory (no analytical benefit for scRNA-seq)
for slot_name, slot in [("X", adata.X)] + [(k, adata.layers[k]) for k in adata.layers]:
    if hasattr(slot, 'dtype') and slot.dtype == np.float64:
        if slot_name == "X":
            adata.X = adata.X.astype(np.float32)
        else:
            adata.layers[slot_name] = adata.layers[slot_name].astype(np.float32)

for key in adata.obsm:  # PCA/UMAP from sklearn are often float64
    if hasattr(adata.obsm[key], 'dtype') and adata.obsm[key].dtype == np.float64:
        adata.obsm[key] = adata.obsm[key].astype(np.float32)

# Integer counts: use int32 (max ~2B, sufficient for UMI). Avoid int8/int16 (overflow)
print(f"Memory: ~{adata.X.data.nbytes / 1e6:.1f} MB (X nonzeros)")
```

*Condensed from data_structure.md (315 lines) and io_operations.md (405 lines). Retained: raw attribute API and gotchas, obsm access/iteration/DataFrame patterns, uns conventions (neighbors, colors, rankings, serialization rules), varp gene-gene usage, chunked reading, backed r+ write-back with limitations, format conversion gotchas (loom/CSV/10X metadata mapping), compression benchmarks (gzip vs lzf), H5AD internal HDF5 layout, Zarr cloud storage (S3/GCS), chunk size selection guide, sparse format preservation (CSR/CSC roundtrip), categorical/ordered preservation, dtype casting patterns. Omitted: introductory prose on what AnnData is (redundant with SKILL.md Overview), basic slot descriptions (in SKILL.md Key Concepts table), simple read/write examples (in SKILL.md Core API Module 2), basic backed mode open/filter/to_memory (in SKILL.md Core API Module 2 second block), format comparison table (in SKILL.md Key Concepts Storage Formats). Relocated to SKILL.md: core slot table, basic I/O patterns, format comparison, backed mode basics.*

---

## manipulation_concatenation.md

# AnnData — Manipulation & Concatenation Reference

Advanced patterns for data manipulation, concatenation, and memory optimization beyond what the main SKILL.md covers.

## Advanced Concatenation

### On-Disk Concatenation

For datasets that collectively exceed RAM, write the concatenated result directly to disk:

```python
from anndata.experimental import concat_on_disk
import anndata as ad

concat_on_disk(
    ["batch1.h5ad", "batch2.h5ad", "batch3.h5ad"],
    "combined.h5ad",
    join="outer",
)
# Verify with backed mode (no full load)
adata = ad.read_h5ad("combined.h5ad", backed="r")
print(f"Combined: {adata.n_obs} cells x {adata.n_vars} genes")
```

### AnnCollection API (Lazy Concatenation)

`AnnCollection` provides virtual concatenation without copying data -- ideal for exploring multi-dataset collections before committing to a full merge.

```python
from anndata.experimental import AnnCollection
import anndata as ad

adata1 = ad.read_h5ad("batch1.h5ad")
adata2 = ad.read_h5ad("batch2.h5ad")

collection = AnnCollection(
    {"batch1": adata1, "batch2": adata2},
    join_obs="inner",
    join_vars="inner",
    label="batch",
    keys=["batch1", "batch2"],
    harmonize_dtypes=True,   # unify categorical codes across datasets
)
print(f"Total obs: {collection.n_obs}")  # metadata available immediately

# Subset lazily, materialize only when needed
subset = collection[collection.obs["cell_type"] == "T_cell"]
adata_full = collection.to_adata()  # loads all data into memory
```

### Merge Strategy Edge Cases

The `merge` parameter controls how **non-concatenation-axis annotations** (e.g., `var` columns when concatenating along axis=0) are combined:

| Strategy | Behavior | Use When | Edge Case |
|----------|----------|----------|-----------|
| `None` | Drop all non-concat metadata | Metadata irrelevant or will be rebuilt | Loses all var annotations |
| `"same"` | Keep columns identical across objects | Shared genome annotations (chromosome, biotype) | Silently drops columns that differ in even one object |
| `"unique"` | Keep columns where each var has one value | Gene IDs, stable identifiers | Fails if same gene has different values across datasets |
| `"first"` | Take value from first object | Descriptions, where order matters | Silently ignores conflicting values in later objects |
| `"only"` | Keep columns exclusive to one object | Dataset-specific annotations | Drops columns present in multiple objects, even if identical |

```python
import anndata as ad, numpy as np, pandas as pd

genes = [f"Gene_{i}" for i in range(50)]
a1 = ad.AnnData(X=np.random.rand(100, 50).astype(np.float32),
                 var=pd.DataFrame(index=genes))
a2 = ad.AnnData(X=np.random.rand(80, 50).astype(np.float32),
                 var=pd.DataFrame(index=genes))
a1.var["biotype"] = "protein_coding"; a2.var["biotype"] = "protein_coding"
a1.var["source"] = "dataset_A";       a2.var["source"] = "dataset_B"
a1.var["custom_A"] = 1.0;             a2.var["custom_B"] = 2.0

c_same = ad.concat([a1, a2], merge="same")
print(list(c_same.var.columns))   # ['biotype'] -- 'source' dropped (differs)

c_first = ad.concat([a1, a2], merge="first")
print(c_first.var["source"].unique())  # ['dataset_A'] -- a2 ignored

c_only = ad.concat([a1, a2], merge="only")
print(list(c_only.var.columns))   # ['custom_A', 'custom_B'] -- shared dropped
```

### Handling Mismatched Layers, obsm, and obsp

- **Layers/obsm**: only keys present in **all** objects are concatenated; missing keys silently dropped
- **obsp**: dropped by default; use `pairwise=True` to create block-diagonal matrices
- **uns**: use `uns_merge` parameter (`"same"`, `"unique"`, `"first"`, `"only"`)

```python
import anndata as ad, numpy as np
from scipy.sparse import csr_matrix

a1 = ad.AnnData(X=np.random.rand(100, 50).astype(np.float32))
a2 = ad.AnnData(X=np.random.rand(80, 50).astype(np.float32))
a1.layers["counts"] = a1.X.copy(); a1.layers["normalized"] = a1.X * 2
a2.layers["counts"] = a2.X.copy()  # a2 missing "normalized"

combined = ad.concat([a1, a2])
print(list(combined.layers.keys()))  # ['counts'] -- 'normalized' dropped

# Workaround: pad missing layers before concat
for adata in [a1, a2]:
    if "normalized" not in adata.layers:
        adata.layers["normalized"] = np.zeros_like(adata.X)
combined = ad.concat([a1, a2])
print(list(combined.layers.keys()))  # ['counts', 'normalized']

# obsp block-diagonal concat
a1.obsp["nn"] = csr_matrix(np.eye(100)); a2.obsp["nn"] = csr_matrix(np.eye(80))
combined = ad.concat([a1, a2], pairwise=True)
print(combined.obsp["nn"].shape)  # (180, 180)

# uns merge
a1.uns["exp"] = {"date": "2024-01-01", "batch": "A"}
a2.uns["exp"] = {"date": "2024-01-01", "batch": "B"}
c = ad.concat([a1, a2], uns_merge="unique")  # keeps "date", drops "batch"
```

## Advanced Data Manipulation

### Bulk Renaming Patterns

```python
import anndata as ad, pandas as pd, numpy as np

adata = ad.AnnData(X=np.random.rand(200, 100).astype(np.float32),
                   obs=pd.DataFrame(index=[f"cell_{i}" for i in range(200)]),
                   var=pd.DataFrame(index=[f"ENSG{i:05d}" for i in range(100)]))
adata.obs["cell_type"] = pd.Categorical(["TypeA", "TypeB"] * 100)

# Bulk rename obs_names (e.g., add sample prefix)
adata.obs_names = "sample1_" + adata.obs_names

# Bulk rename var_names via mapping table
gene_map = pd.read_csv("gene_id_to_symbol.csv", index_col=0)
mapped = gene_map.reindex(adata.var_names)["symbol"]
adata.var_names = mapped.fillna(adata.var_names).values
adata.var_names_make_unique()

# Category renaming, adding, and cleaning
adata.obs["cell_type"] = adata.obs["cell_type"].cat.rename_categories(
    {"TypeA": "T_cell", "TypeB": "B_cell"})
adata.obs["cell_type"] = adata.obs["cell_type"].cat.add_categories(["NK_cell"])
adata.obs.loc[adata.obs_names[:10], "cell_type"] = "NK_cell"
adata.obs["cell_type"] = adata.obs["cell_type"].cat.remove_unused_categories()
```

### Sparse Format Switching (CSR / CSC / COO)

CSR is best for row slicing (cell access), CSC for column slicing (gene access), COO for construction from triplets.

```python
from scipy.sparse import csr_matrix, csc_matrix, coo_matrix, issparse
import numpy as np

# CSR -> CSC (faster gene-wise ops like sc.pp.filter_genes)
adata.X = csc_matrix(adata.X)
# CSC -> CSR (faster cell-wise ops like sc.pp.normalize_total)
adata.X = csr_matrix(adata.X)

# COO for construction from triplets, then convert for access
row, col = np.array([0, 0, 1, 2]), np.array([0, 2, 1, 3])
data = np.array([1.0, 2.0, 3.0, 4.0], dtype=np.float32)
adata.X = csr_matrix(coo_matrix((data, (row, col)), shape=(1000, 5000)))

# Convert all layers to consistent format
for key in adata.layers:
    if issparse(adata.layers[key]):
        adata.layers[key] = csr_matrix(adata.layers[key])
```

### In-Place vs Copy Operations

In-place operations (no memory overhead): `adata.obs["score"] = values`, `del adata.obs["col"]`, `adata.obs_names_make_unique()`, `adata.strings_to_categoricals()`. Copy-required: subsetting returns a view (`is_view=True`) -- must `.copy()` before modifying. Transposition (`adata.T`) always returns a new object.

## Memory Optimization

### Memory Estimation Before Loading

```python
import os, h5py, numpy as np

def estimate_h5ad_memory(path):
    """Estimate in-memory size from H5AD file metadata without loading."""
    with h5py.File(path, "r") as f:
        if "X" not in f: return 0
        ds = f["X"]
        if isinstance(ds, h5py.Dataset):
            nbytes = np.prod(ds.shape) * np.dtype(ds.dtype).itemsize
        elif "data" in ds:  # sparse
            nbytes = ds["data"].nbytes + ds["indices"].nbytes + ds["indptr"].nbytes
        else: return 0
    print(f"~{nbytes/1e9:.2f} GB in memory (X only)")
    return nbytes / 1e9

# Decision: if estimated > 70% available RAM, use backed mode
import psutil
if estimate_h5ad_memory("large.h5ad") > psutil.virtual_memory().available / 1e9 * 0.7:
    print("-> Use backed mode")
```

### Garbage Collection

After dropping large intermediates, `del obj; gc.collect()` forces immediate reclaim. Strip bulky slots: `del adata.obsm["X_pca"]; del adata.obsp; adata.uns = {}; gc.collect()`.

### Chunk Processing for Large AnnData

```python
import anndata as ad, numpy as np
from scipy.sparse import issparse

adata = ad.read_h5ad("huge.h5ad", backed="r")
chunk_size = 5000
gene_sums = np.zeros(adata.n_vars, dtype=np.float64)
gene_nnz = np.zeros(adata.n_vars, dtype=np.int64)

for start in range(0, adata.n_obs, chunk_size):
    end = min(start + chunk_size, adata.n_obs)
    X = adata[start:end].to_memory().X
    if issparse(X):
        gene_sums += np.array(X.sum(axis=0)).flatten()
        gene_nnz += np.array((X > 0).sum(axis=0)).flatten()
    else:
        gene_sums += X.sum(axis=0); gene_nnz += (X > 0).sum(axis=0)

gene_means = gene_sums / adata.n_obs
print(f"Mean expression range: [{gene_means.min():.4f}, {gene_means.max():.4f}]")
```

### Efficient Iteration Patterns

```python
import anndata as ad, numpy as np
adata = ad.read_h5ad("data.h5ad")

# Anti-pattern: repeated boolean subsetting (slow, creates many views)
# Better: pre-compute group indices via groupby
groups = adata.obs.groupby("cell_type").groups
results = {}
for cell_type, idx in groups.items():
    results[cell_type] = np.array(adata[idx].X.mean(axis=0)).flatten()

# Fastest: integer indices avoid pandas index lookup
for cell_type, _ in groups.items():
    int_idx = np.where(adata.obs["cell_type"] == cell_type)[0]
    subset = adata[int_idx]
```

## Common Anti-Patterns (Detailed)

**1. Modifying views**: Subsetting returns a view -- modifying it triggers `ImplicitModificationWarning` and may corrupt the parent. Always `adata[:100].copy()` before modification.

**2. String columns wasting memory**: Object dtype strings use ~80x more memory than categoricals. Always `pd.Categorical(series)` or `adata.strings_to_categoricals()`.

**3. Dense operations on sparse data**: `adata.X + 1` or `np.log1p(adata.X)` silently densify sparse matrices (OOM risk). Instead operate on `.data`: `X = adata.X.copy(); X.data = np.log1p(X.data)`.

**4. Deleting parent before materializing view**: `view = adata[:100]; del adata` -- view may become invalid. Always `.copy()` before deleting the parent.

## Batch-Aware QC Patterns

### Multi-Metric QC with Adaptive Thresholds

Different batches have systematically different QC distributions. Use MAD-based thresholds per batch instead of global cutoffs.

```python
import anndata as ad, numpy as np, pandas as pd

adata = ad.read_h5ad("multi_batch.h5ad")
adata.obs["n_genes"] = np.array((adata.X > 0).sum(axis=1)).flatten()
adata.obs["total_counts"] = np.array(adata.X.sum(axis=1)).flatten()
mito = adata.var_names.str.startswith("MT-")
adata.obs["pct_mito"] = (np.array(adata[:, mito].X.sum(axis=1)).flatten()
                          / np.array(adata.X.sum(axis=1)).flatten())

def mad_filter(series, n_mads=5):
    """Boolean mask: values within n_mads of median."""
    med = series.median()
    mad = np.median(np.abs(series - med))
    return (series > med - n_mads * mad) & (series < med + n_mads * mad)

keep = pd.Series(True, index=adata.obs_names)
for batch in adata.obs["batch"].unique():
    m = adata.obs["batch"] == batch
    keep.loc[m] &= mad_filter(adata.obs.loc[m, "n_genes"])
    keep.loc[m] &= mad_filter(adata.obs.loc[m, "total_counts"])
    keep.loc[m] &= adata.obs.loc[m, "pct_mito"] < 0.2

adata_qc = adata[keep.values].copy()
print(f"After batch-aware QC: {adata_qc.n_obs}/{adata.n_obs} cells")

# Doublet detection (requires scrublet):
# import scrublet as scr
# scrub = scr.Scrublet(adata_qc.X)
# scores, predicted = scrub.scrub_doublets()
# adata_qc.obs["doublet_score"] = scores
# adata_qc = adata_qc[~predicted].copy()

# Ambient RNA estimation (requires DecontX from celda):
# from celda import DecontX
# decontx = DecontX(); decontx.fit(adata_qc)
# adata_qc.layers["decontaminated"] = decontx.decontaminated_counts
```

### Sorting and Reordering

Sort observations: `adata = adata[adata.obs.sort_values("total_counts", ascending=False).index]`. Reorder variables to match an external gene list: `adata[:, [g for g in desired_genes if g in adata.var_names]].copy()`.

---

*Condensed from manipulation.md (517 lines), concatenation.md (397 lines), and best_practices.md (526 lines) — 1,440 total. Retained: on-disk concat, AnnCollection API (lazy concat, harmonize, to_adata), merge strategy edge cases (same/unique/first/only with examples), mismatched layers/obsm/obsp handling, uns merge, bulk renaming (obs_names, var_names, category mapping), sparse format switching (CSR/CSC/COO), memory estimation before loading, garbage collection, chunk processing, efficient iteration (groupby vs repeated subsetting), batch-aware QC (MAD thresholds, doublet/ambient RNA setup), subsetting performance, common anti-patterns with detailed explanations, sorting/reordering. Omitted from manipulation.md: basic subsetting by index/name/mask/metadata (Core API 3), transposition, copy semantics basics, adding/removing layers/embeddings/obsp/uns (Core API 4), QC metric computation (Core API 6), normalize/log/z-score transforms (Workflow 1), downsampling/train-test split (generic Python), obs_vector/var_vector (thin wrappers), external metadata merge (Best Practices 7). Omitted from concatenation.md: basic axis=0/axis=1 concat (Core API 5), inner/outer join basics (Core API 5), batch label tracking (Core API 5), fill_value parameter (trivial), index_unique parameter (trivial), layer/obsm basic concat mechanics, common patterns (replicates, batches — Workflow 2), post-concat validation (generic). Omitted from best_practices.md: sparse matrix basics (Best Practices 1), strings-to-categoricals basics (Best Practices 2), backed mode intro (Best Practices 3), views vs copies intro (Key Concepts), storage format comparison (Key Concepts), file size optimization (Common Recipes), raw data usage (niche — consult scanpy), metadata naming conventions (generic), reproducibility boilerplate (generic Python), data validation assertions (generic), scanpy/pandas/PyTorch integration (Ecosystem Integration + Recipes). Relocated to SKILL.md: QC filtering, basic concat, core best practices, views vs copies.*
