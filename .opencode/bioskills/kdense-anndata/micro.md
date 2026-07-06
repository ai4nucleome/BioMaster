## best_practices.md

# Best Practices

Guidelines for efficient and effective use of AnnData.

## Memory Management

### Use sparse matrices for sparse data
```python
import numpy as np
from scipy.sparse import csr_matrix
import anndata as ad

# Check data sparsity
data = np.random.rand(1000, 2000)
sparsity = 1 - np.count_nonzero(data) / data.size
print(f"Sparsity: {sparsity:.2%}")

# Convert to sparse if >50% zeros
if sparsity > 0.5:
    adata = ad.AnnData(X=csr_matrix(data))
else:
    adata = ad.AnnData(X=data)

# Benefits: 10-100x memory reduction for sparse genomics data
```

### Convert strings to categoricals
```python
# Inefficient: string columns use lots of memory
adata.obs['cell_type'] = ['Type_A', 'Type_B', 'Type_C'] * 333 + ['Type_A']

# Efficient: convert to categorical
adata.obs['cell_type'] = adata.obs['cell_type'].astype('category')

# Convert all string columns
adata.strings_to_categoricals()

# Benefits: 10-50x memory reduction for repeated strings
```

### Use backed mode for large datasets
```python
# Don't load entire dataset into memory
adata = ad.read_h5ad('large_dataset.h5ad', backed='r')

# Work with metadata
filtered = adata[adata.obs['quality'] > 0.8]

# Load only filtered subset
adata_subset = filtered.to_memory()

# Benefits: Work with datasets larger than RAM
```

## Views vs Copies

### Understanding views
```python
# Subsetting creates a view by default
subset = adata[0:100, :]
print(subset.is_view)  # True

# Views don't copy data (memory efficient)
# But modifications can affect original

# Check if object is a view
if adata.is_view:
    adata = adata.copy()  # Make independent
```

### When to use views
```python
# Good: Read-only operations on subsets
mean_expr = adata[adata.obs['cell_type'] == 'T cell'].X.mean()

# Good: Temporary analysis
temp_subset = adata[:100, :]
result = analyze(temp_subset.X)
```

### When to use copies
```python
# Create independent copy for modifications
adata_filtered = adata[keep_cells, :].copy()

# Safe to modify without affecting original
adata_filtered.obs['new_column'] = values

# Always copy when:
# - Storing subset for later use
# - Modifying subset data
# - Passing to function that modifies data
```

## Data Storage Best Practices

### Choose the right format

**H5AD (HDF5) - Default choice**
```python
adata.write_h5ad('data.h5ad', compression='gzip')
```
- Fast random access
- Supports backed mode
- Good compression
- Best for: Most use cases

**Zarr - Cloud and parallel access**
```python
adata.write_zarr('data.zarr', chunks=(100, 100))
```
- Excellent for cloud storage (S3, GCS)
- Supports parallel I/O
- Good compression
- Best for: Large datasets, cloud workflows, parallel processing

**CSV - Interoperability**
```python
adata.write_csvs('output_dir/')
```
- Human readable
- Compatible with all tools
- Large file sizes, slow
- Best for: Sharing with non-Python tools, small datasets

### Optimize file size
```python
# Before saving, optimize:

# 1. Convert to sparse if appropriate
from scipy.sparse import csr_matrix, issparse
if not issparse(adata.X):
    density = np.count_nonzero(adata.X) / adata.X.size
    if density < 0.5:
        adata.X = csr_matrix(adata.X)

# 2. Convert strings to categoricals
adata.strings_to_categoricals()

# 3. Use compression
adata.write_h5ad('data.h5ad', compression='gzip', compression_opts=9)

# Typical results: 5-20x file size reduction
```

## Backed Mode Strategies

### Read-only analysis
```python
# Open in read-only backed mode
adata = ad.read_h5ad('data.h5ad', backed='r')

# Perform filtering without loading data
high_quality = adata[adata.obs['quality_score'] > 0.8]

# Load only filtered data
adata_filtered = high_quality.to_memory()
```

### Read-write modifications
```python
# Open in read-write backed mode
adata = ad.read_h5ad('data.h5ad', backed='r+')

# Modify metadata (written to disk)
adata.obs['new_annotation'] = values

# X remains on disk, modifications saved immediately
```

### Chunked processing
```python
# Process large dataset in chunks
adata = ad.read_h5ad('huge_dataset.h5ad', backed='r')

results = []
chunk_size = 1000

for i in range(0, adata.n_obs, chunk_size):
    chunk = adata[i:i+chunk_size, :].to_memory()
    result = process(chunk)
    results.append(result)

final_result = combine(results)
```

## Performance Optimization

### Subsetting performance
```python
# Fast: Boolean indexing with arrays
mask = np.array(adata.obs['quality'] > 0.5)
subset = adata[mask, :]

# Slow: Boolean indexing with Series (creates view chain)
subset = adata[adata.obs['quality'] > 0.5, :]

# Fastest: Integer indices
indices = np.where(adata.obs['quality'] > 0.5)[0]
subset = adata[indices, :]
```

### Avoid repeated subsetting
```python
# Inefficient: Multiple subset operations
for cell_type in ['A', 'B', 'C']:
    subset = adata[adata.obs['cell_type'] == cell_type]
    process(subset)

# Efficient: Group and process
groups = adata.obs.groupby('cell_type').groups
for cell_type, indices in groups.items():
    subset = adata[indices, :]
    process(subset)
```

### Use chunked operations for large matrices
```python
# Process X in chunks
for chunk in adata.chunked_X(chunk_size=1000):
    result = compute(chunk)

# More memory efficient than loading full X
```

## Working with Raw Data

### Store raw before filtering
```python
# Original data with all genes
adata = ad.AnnData(X=counts)

# Store raw before filtering
adata.raw = adata.copy()

# Filter to highly variable genes
adata = adata[:, adata.var['highly_variable']]

# Later: access original data
original_expression = adata.raw.X
all_genes = adata.raw.var_names
```

### When to use raw
```python
# Use raw for:
# - Differential expression on filtered genes
# - Visualization of specific genes not in filtered set
# - Accessing original counts after normalization

# Access raw data
if adata.raw is not None:
    gene_expr = adata.raw[:, 'GENE_NAME'].X
else:
    gene_expr = adata[:, 'GENE_NAME'].X
```

## Metadata Management

### Naming conventions
```python
# Consistent naming improves usability

# Observation metadata (obs):
# - cell_id, sample_id
# - cell_type, tissue, condition
# - n_genes, n_counts, percent_mito
# - cluster, leiden, louvain

# Variable metadata (var):
# - gene_id, gene_name
# - highly_variable, n_cells
# - mean_expression, dispersion

# Embeddings (obsm):
# - X_pca, X_umap, X_tsne
# - X_diffmap, X_draw_graph_fr

# Follow conventions from scanpy/scverse ecosystem
```

### Document metadata
```python
# Store metadata descriptions in uns
adata.uns['metadata_descriptions'] = {
    'cell_type': 'Cell type annotation from automated clustering',
    'quality_score': 'QC score from scrublet (0-1, higher is better)',
    'batch': 'Experimental batch identifier'
}

# Store processing history
adata.uns['processing_steps'] = [
    'Raw counts loaded from 10X',
    'Filtered: n_genes > 200, n_counts < 50000',
    'Normalized to 10000 counts per cell',
    'Log transformed'
]
```

## Reproducibility

### Set random seeds
```python
import numpy as np

# Set seed for reproducible results
np.random.seed(42)

# Document in uns
adata.uns['random_seed'] = 42
```

### Store parameters
```python
# Store analysis parameters in uns
adata.uns['pca'] = {
    'n_comps': 50,
    'svd_solver': 'arpack',
    'random_state': 42
}

adata.uns['neighbors'] = {
    'n_neighbors': 15,
    'n_pcs': 50,
    'metric': 'euclidean',
    'method': 'umap'
}
```

### Version tracking
```python
import anndata
import scanpy
import numpy

# Store versions
adata.uns['versions'] = {
    'anndata': anndata.__version__,
    'scanpy': scanpy.__version__,
    'numpy': numpy.__version__,
    'python': sys.version
}
```

## Error Handling

### Check data validity
```python
# Verify dimensions
assert adata.n_obs == len(adata.obs)
assert adata.n_vars == len(adata.var)
assert adata.X.shape == (adata.n_obs, adata.n_vars)

# Check for NaN values
has_nan = np.isnan(adata.X.data).any() if issparse(adata.X) else np.isnan(adata.X).any()
if has_nan:
    print("Warning: Data contains NaN values")

# Check for negative values (if counts expected)
has_negative = (adata.X.data < 0).any() if issparse(adata.X) else (adata.X < 0).any()
if has_negative:
    print("Warning: Data contains negative values")
```

### Validate metadata
```python
# Check for missing values
missing_obs = adata.obs.isnull().sum()
if missing_obs.any():
    print("Missing values in obs:")
    print(missing_obs[missing_obs > 0])

# Verify indices are unique
assert adata.obs_names.is_unique, "Observation names not unique"
assert adata.var_names.is_unique, "Variable names not unique"

# Check metadata alignment
assert len(adata.obs) == adata.n_obs
assert len(adata.var) == adata.n_vars
```

## Integration with Other Tools

### Scanpy integration
```python
import scanpy as sc

# AnnData is native format for scanpy
sc.pp.filter_cells(adata, min_genes=200)
sc.pp.filter_genes(adata, min_cells=3)
sc.pp.normalize_total(adata, target_sum=1e4)
sc.pp.log1p(adata)
sc.pp.highly_variable_genes(adata)
sc.pp.pca(adata)
sc.pp.neighbors(adata)
sc.tl.umap(adata)
```

### Pandas integration
```python
import pandas as pd

# Convert to DataFrame
df = adata.to_df()

# Create from DataFrame
adata = ad.AnnData(df)

# Work with metadata as DataFrames
adata.obs = adata.obs.merge(external_metadata, left_index=True, right_index=True)
```

### PyTorch integration
```python
from anndata.experimental import AnnLoader

# Create PyTorch DataLoader
dataloader = AnnLoader(adata, batch_size=128, shuffle=True)

# Iterate in training loop
for batch in dataloader:
    X = batch.X
    # Train model on batch
```

## Common Pitfalls

### Pitfall 1: Modifying views
```python
# Wrong: Modifying view can affect original
subset = adata[:100, :]
subset.X = new_data  # May modify adata.X!

# Correct: Copy before modifying
subset = adata[:100, :].copy()
subset.X = new_data  # Independent copy
```

### Pitfall 2: Index misalignment
```python
# Wrong: Assuming order matches
external_data = pd.read_csv('data.csv')
adata.obs['new_col'] = external_data['values']  # May misalign!

# Correct: Align on index
adata.obs['new_col'] = external_data.set_index('cell_id').loc[adata.obs_names, 'values']
```

### Pitfall 3: Mixing sparse and dense
```python
# Wrong: Converting sparse to dense uses huge memory
result = adata.X + 1  # Converts sparse to dense!

# Correct: Use sparse operations
from scipy.sparse import issparse
if issparse(adata.X):
    result = adata.X.copy()
    result.data += 1
```

### Pitfall 4: Not handling views
```python
# Wrong: Assuming subset is independent
subset = adata[mask, :]
del adata  # subset may become invalid!

# Correct: Copy when needed
subset = adata[mask, :].copy()
del adata  # subset remains valid
```

### Pitfall 5: Ignoring memory constraints
```python
# Wrong: Loading huge dataset into memory
adata = ad.read_h5ad('100GB_file.h5ad')  # OOM error!

# Correct: Use backed mode
adata = ad.read_h5ad('100GB_file.h5ad', backed='r')
subset = adata[adata.obs['keep']].to_memory()
```

## Workflow Example

Complete best-practices workflow:

```python
import anndata as ad
import numpy as np
from scipy.sparse import csr_matrix

# 1. Load with backed mode if large
adata = ad.read_h5ad('data.h5ad', backed='r')

# 2. Quick metadata check without loading data
print(f"Dataset: {adata.n_obs} cells × {adata.n_vars} genes")

# 3. Filter based on metadata
high_quality = adata[adata.obs['quality_score'] > 0.8]

# 4. Load filtered subset to memory
adata = high_quality.to_memory()

# 5. Convert to optimal storage types
adata.strings_to_categoricals()
if not issparse(adata.X):
    density = np.count_nonzero(adata.X) / adata.X.size
    if density < 0.5:
        adata.X = csr_matrix(adata.X)

# 6. Store raw before filtering genes
adata.raw = adata.copy()

# 7. Filter to highly variable genes
adata = adata[:, adata.var['highly_variable']].copy()

# 8. Document processing
adata.uns['processing'] = {
    'filtered': 'quality_score > 0.8',
    'n_hvg': adata.n_vars,
    'date': '2025-11-03'
}

# 9. Save optimized
adata.write_h5ad('processed.h5ad', compression='gzip')
```

---

## concatenation.md

# Concatenating AnnData Objects

Combine multiple AnnData objects along either observations or variables axis.

## Basic Concatenation

### Concatenate along observations (stack cells/samples)
```python
import anndata as ad
import numpy as np

# Create multiple AnnData objects
adata1 = ad.AnnData(X=np.random.rand(100, 50))
adata2 = ad.AnnData(X=np.random.rand(150, 50))
adata3 = ad.AnnData(X=np.random.rand(200, 50))

# Concatenate along observations (axis=0, default)
adata_combined = ad.concat([adata1, adata2, adata3], axis=0)

print(adata_combined.shape)  # (450, 50)
```

### Concatenate along variables (stack genes/features)
```python
# Create objects with same observations, different variables
adata1 = ad.AnnData(X=np.random.rand(100, 50))
adata2 = ad.AnnData(X=np.random.rand(100, 30))
adata3 = ad.AnnData(X=np.random.rand(100, 70))

# Concatenate along variables (axis=1)
adata_combined = ad.concat([adata1, adata2, adata3], axis=1)

print(adata_combined.shape)  # (100, 150)
```

## Join Types

### Inner join (intersection)
Keep only variables/observations present in all objects.

```python
import pandas as pd

# Create objects with different variables
adata1 = ad.AnnData(
    X=np.random.rand(100, 50),
    var=pd.DataFrame(index=[f'Gene_{i}' for i in range(50)])
)
adata2 = ad.AnnData(
    X=np.random.rand(150, 60),
    var=pd.DataFrame(index=[f'Gene_{i}' for i in range(10, 70)])
)

# Inner join: only genes 10-49 are kept (overlap)
adata_inner = ad.concat([adata1, adata2], join='inner')
print(adata_inner.n_vars)  # 40 genes (overlap)
```

### Outer join (union)
Keep all variables/observations, filling missing values.

```python
# Outer join: all genes are kept
adata_outer = ad.concat([adata1, adata2], join='outer')
print(adata_outer.n_vars)  # 70 genes (union)

# Missing values are filled with appropriate defaults:
# - 0 for sparse matrices
# - NaN for dense matrices
```

### Fill values for outer joins
```python
# Specify fill value for missing data
adata_filled = ad.concat([adata1, adata2], join='outer', fill_value=0)
```

## Tracking Data Sources

### Add batch labels
```python
# Label which object each observation came from
adata_combined = ad.concat(
    [adata1, adata2, adata3],
    label='batch',  # Column name for labels
    keys=['batch1', 'batch2', 'batch3']  # Labels for each object
)

print(adata_combined.obs['batch'].value_counts())
# batch1    100
# batch2    150
# batch3    200
```

### Automatic batch labels
```python
# If keys not provided, uses integer indices
adata_combined = ad.concat(
    [adata1, adata2, adata3],
    label='dataset'
)
# dataset column contains: 0, 1, 2
```

## Merge Strategies

Control how metadata from different objects is combined using the `merge` parameter.

### merge=None (default for observations)
Exclude metadata on non-concatenation axis.

```python
# When concatenating observations, var metadata must match
adata1.var['gene_type'] = 'protein_coding'
adata2.var['gene_type'] = 'protein_coding'

# var is kept only if identical across all objects
adata_combined = ad.concat([adata1, adata2], merge=None)
```

### merge='same'
Keep metadata that is identical across all objects.

```python
adata1.var['chromosome'] = ['chr1'] * 25 + ['chr2'] * 25
adata2.var['chromosome'] = ['chr1'] * 25 + ['chr2'] * 25
adata1.var['type'] = 'protein_coding'
adata2.var['type'] = 'lncRNA'  # Different

# 'chromosome' is kept (same), 'type' is excluded (different)
adata_combined = ad.concat([adata1, adata2], merge='same')
```

### merge='unique'
Keep metadata columns where each key has exactly one value.

```python
adata1.var['gene_id'] = [f'ENSG{i:05d}' for i in range(50)]
adata2.var['gene_id'] = [f'ENSG{i:05d}' for i in range(50)]

# gene_id is kept (unique values for each key)
adata_combined = ad.concat([adata1, adata2], merge='unique')
```

### merge='first'
Take values from the first object containing each key.

```python
adata1.var['description'] = ['Desc1'] * 50
adata2.var['description'] = ['Desc2'] * 50

# Uses descriptions from adata1
adata_combined = ad.concat([adata1, adata2], merge='first')
```

### merge='only'
Keep metadata that appears in only one object.

```python
adata1.var['adata1_specific'] = [1] * 50
adata2.var['adata2_specific'] = [2] * 50

# Both metadata columns are kept
adata_combined = ad.concat([adata1, adata2], merge='only')
```

## Handling Index Conflicts

### Make indices unique
```python
import pandas as pd

# Create objects with overlapping observation names
adata1 = ad.AnnData(
    X=np.random.rand(3, 10),
    obs=pd.DataFrame(index=['cell_1', 'cell_2', 'cell_3'])
)
adata2 = ad.AnnData(
    X=np.random.rand(3, 10),
    obs=pd.DataFrame(index=['cell_1', 'cell_2', 'cell_3'])
)

# Make indices unique by appending batch keys
adata_combined = ad.concat(
    [adata1, adata2],
    label='batch',
    keys=['batch1', 'batch2'],
    index_unique='_'  # Separator for making indices unique
)

print(adata_combined.obs_names)
# ['cell_1_batch1', 'cell_2_batch1', 'cell_3_batch1',
#  'cell_1_batch2', 'cell_2_batch2', 'cell_3_batch2']
```

## Concatenating Layers

```python
# Objects with layers
adata1 = ad.AnnData(X=np.random.rand(100, 50))
adata1.layers['normalized'] = np.random.rand(100, 50)
adata1.layers['scaled'] = np.random.rand(100, 50)

adata2 = ad.AnnData(X=np.random.rand(150, 50))
adata2.layers['normalized'] = np.random.rand(150, 50)
adata2.layers['scaled'] = np.random.rand(150, 50)

# Layers are concatenated automatically if present in all objects
adata_combined = ad.concat([adata1, adata2])

print(adata_combined.layers.keys())
# dict_keys(['normalized', 'scaled'])
```

## Concatenating Multi-dimensional Annotations

### obsm/varm
```python
# Objects with embeddings
adata1.obsm['X_pca'] = np.random.rand(100, 50)
adata2.obsm['X_pca'] = np.random.rand(150, 50)

# obsm is concatenated along observation axis
adata_combined = ad.concat([adata1, adata2])
print(adata_combined.obsm['X_pca'].shape)  # (250, 50)
```

### obsp/varp (pairwise annotations)
```python
from scipy.sparse import csr_matrix

# Pairwise matrices
adata1.obsp['connectivities'] = csr_matrix((100, 100))
adata2.obsp['connectivities'] = csr_matrix((150, 150))

# By default, obsp is NOT concatenated (set pairwise=True to include)
adata_combined = ad.concat([adata1, adata2])
# adata_combined.obsp is empty

# Include pairwise data (creates block diagonal matrix)
adata_combined = ad.concat([adata1, adata2], pairwise=True)
print(adata_combined.obsp['connectivities'].shape)  # (250, 250)
```

## Concatenating uns (unstructured)

Unstructured metadata is merged recursively:

```python
adata1.uns['experiment'] = {'date': '2025-01-01', 'batch': 'A'}
adata2.uns['experiment'] = {'date': '2025-01-01', 'batch': 'B'}

# Using merge='unique' for uns
adata_combined = ad.concat([adata1, adata2], uns_merge='unique')
# 'date' is kept (same value), 'batch' might be excluded (different values)
```

## Lazy Concatenation (AnnCollection)

For very large datasets, use lazy concatenation that doesn't load all data:

```python
from anndata.experimental import AnnCollection

# Create collection from file paths (doesn't load data)
files = ['data1.h5ad', 'data2.h5ad', 'data3.h5ad']
collection = AnnCollection(
    files,
    join_obs='outer',
    join_vars='inner',
    label='dataset',
    keys=['dataset1', 'dataset2', 'dataset3']
)

# Access data lazily
print(collection.n_obs)  # Total observations
print(collection.obs.head())  # Metadata loaded, not X

# Convert to regular AnnData when needed (loads all data)
adata = collection.to_adata()
```

### Working with AnnCollection
```python
# Subset without loading data
subset = collection[collection.obs['cell_type'] == 'T cell']

# Iterate through datasets
for adata in collection:
    print(adata.shape)

# Access specific dataset
first_dataset = collection[0]
```

## Concatenation on Disk

For datasets too large for memory, concatenate directly on disk:

```python
from anndata.experimental import concat_on_disk

# Concatenate without loading into memory
concat_on_disk(
    ['data1.h5ad', 'data2.h5ad', 'data3.h5ad'],
    'combined.h5ad',
    join='outer'
)

# Load result in backed mode
adata = ad.read_h5ad('combined.h5ad', backed='r')
```

## Common Concatenation Patterns

### Combine technical replicates
```python
# Multiple runs of the same samples
replicates = [adata_run1, adata_run2, adata_run3]
adata_combined = ad.concat(
    replicates,
    label='technical_replicate',
    keys=['rep1', 'rep2', 'rep3'],
    join='inner'  # Keep only genes measured in all runs
)
```

### Combine batches from experiment
```python
# Different experimental batches
batches = [adata_batch1, adata_batch2, adata_batch3]
adata_combined = ad.concat(
    batches,
    label='batch',
    keys=['batch1', 'batch2', 'batch3'],
    join='outer'  # Keep all genes
)

# Later: apply batch correction
```

### Merge multi-modal data
```python
# Different measurement modalities (e.g., RNA + protein)
adata_rna = ad.AnnData(X=np.random.rand(100, 2000))
adata_protein = ad.AnnData(X=np.random.rand(100, 50))

# Concatenate along variables to combine modalities
adata_multimodal = ad.concat([adata_rna, adata_protein], axis=1)

# Add labels to distinguish modalities
adata_multimodal.var['modality'] = ['RNA'] * 2000 + ['protein'] * 50
```

## Best Practices

1. **Check compatibility before concatenating**
```python
# Verify shapes are compatible
print([adata.n_vars for adata in [adata1, adata2, adata3]])

# Check variable names match
print([set(adata.var_names) for adata in [adata1, adata2, adata3]])
```

2. **Use appropriate join type**
- `inner`: When you need the same features across all samples (most stringent)
- `outer`: When you want to preserve all features (most inclusive)

3. **Track data sources**
Always use `label` and `keys` to track which observations came from which dataset.

4. **Consider memory usage**
- For large datasets, use `AnnCollection` or `concat_on_disk`
- Consider backed mode for the result

5. **Handle batch effects**
Concatenation combines data but doesn't correct for batch effects. Apply batch correction after concatenation:
```python
# After concatenation, apply batch correction
import scanpy as sc
sc.pp.combat(adata_combined, key='batch')
```

6. **Validate results**
```python
# Check dimensions
print(adata_combined.shape)

# Check batch distribution
print(adata_combined.obs['batch'].value_counts())

# Verify metadata integrity
print(adata_combined.var.head())
print(adata_combined.obs.head())
```

---

## data_structure.md

# AnnData Object Structure

The AnnData object stores a data matrix with associated annotations, providing a flexible framework for managing experimental data and metadata.

## Core Components

### X (Data Matrix)
The primary data matrix with shape (n_obs, n_vars) storing experimental measurements.

```python
import anndata as ad
import numpy as np

# Create with dense array
adata = ad.AnnData(X=np.random.rand(100, 2000))

# Create with sparse matrix (recommended for large, sparse data)
from scipy.sparse import csr_matrix
sparse_data = csr_matrix(np.random.rand(100, 2000))
adata = ad.AnnData(X=sparse_data)
```

Access data:
```python
# Full matrix (caution with large datasets)
full_data = adata.X

# Single observation
obs_data = adata.X[0, :]

# Single variable across all observations
var_data = adata.X[:, 0]
```

### obs (Observation Annotations)
DataFrame storing metadata about observations (rows). Each row corresponds to one observation in X.

```python
import pandas as pd

# Create AnnData with observation metadata
obs_df = pd.DataFrame({
    'cell_type': ['T cell', 'B cell', 'Monocyte'],
    'treatment': ['control', 'treated', 'control'],
    'timepoint': [0, 24, 24]
}, index=['cell_1', 'cell_2', 'cell_3'])

adata = ad.AnnData(X=np.random.rand(3, 100), obs=obs_df)

# Access observation metadata
print(adata.obs['cell_type'])
print(adata.obs.loc['cell_1'])
```

### var (Variable Annotations)
DataFrame storing metadata about variables (columns). Each row corresponds to one variable in X.

```python
# Create AnnData with variable metadata
var_df = pd.DataFrame({
    'gene_name': ['ACTB', 'GAPDH', 'TP53'],
    'chromosome': ['7', '12', '17'],
    'highly_variable': [True, False, True]
}, index=['ENSG00001', 'ENSG00002', 'ENSG00003'])

adata = ad.AnnData(X=np.random.rand(100, 3), var=var_df)

# Access variable metadata
print(adata.var['gene_name'])
print(adata.var.loc['ENSG00001'])
```

### layers (Alternative Data Representations)
Dictionary storing alternative matrices with the same dimensions as X.

```python
# Store raw counts, normalized data, and scaled data
adata = ad.AnnData(X=np.random.rand(100, 2000))
adata.layers['raw_counts'] = np.random.randint(0, 100, (100, 2000))
adata.layers['normalized'] = adata.X / np.sum(adata.X, axis=1, keepdims=True)
adata.layers['scaled'] = (adata.X - adata.X.mean()) / adata.X.std()

# Access layers
raw_data = adata.layers['raw_counts']
normalized_data = adata.layers['normalized']
```

Common layer uses:
- `raw_counts`: Original count data before normalization
- `normalized`: Log-normalized or TPM values
- `scaled`: Z-scored values for analysis
- `imputed`: Data after imputation

### obsm (Multi-dimensional Observation Annotations)
Dictionary storing multi-dimensional arrays aligned to observations.

```python
# Store PCA coordinates and UMAP embeddings
adata.obsm['X_pca'] = np.random.rand(100, 50)  # 50 principal components
adata.obsm['X_umap'] = np.random.rand(100, 2)  # 2D UMAP coordinates
adata.obsm['X_tsne'] = np.random.rand(100, 2)  # 2D t-SNE coordinates

# Access embeddings
pca_coords = adata.obsm['X_pca']
umap_coords = adata.obsm['X_umap']
```

Common obsm uses:
- `X_pca`: Principal component coordinates
- `X_umap`: UMAP embedding coordinates
- `X_tsne`: t-SNE embedding coordinates
- `X_diffmap`: Diffusion map coordinates
- `protein_expression`: Protein abundance measurements (CITE-seq)

### varm (Multi-dimensional Variable Annotations)
Dictionary storing multi-dimensional arrays aligned to variables.

```python
# Store PCA loadings
adata.varm['PCs'] = np.random.rand(2000, 50)  # Loadings for 50 components
adata.varm['gene_modules'] = np.random.rand(2000, 10)  # Gene module scores

# Access loadings
pc_loadings = adata.varm['PCs']
```

Common varm uses:
- `PCs`: Principal component loadings
- `gene_modules`: Gene co-expression module assignments

### obsp (Pairwise Observation Relationships)
Dictionary storing sparse matrices representing relationships between observations.

```python
from scipy.sparse import csr_matrix

# Store k-nearest neighbor graph
n_obs = 100
knn_graph = csr_matrix(np.random.rand(n_obs, n_obs) > 0.95)
adata.obsp['connectivities'] = knn_graph
adata.obsp['distances'] = csr_matrix(np.random.rand(n_obs, n_obs))

# Access graphs
knn_connections = adata.obsp['connectivities']
distances = adata.obsp['distances']
```

Common obsp uses:
- `connectivities`: Cell-cell neighborhood graph
- `distances`: Pairwise distances between cells

### varp (Pairwise Variable Relationships)
Dictionary storing sparse matrices representing relationships between variables.

```python
# Store gene-gene correlation matrix
n_vars = 2000
gene_corr = csr_matrix(np.random.rand(n_vars, n_vars) > 0.99)
adata.varp['correlations'] = gene_corr

# Access correlations
gene_correlations = adata.varp['correlations']
```

### uns (Unstructured Annotations)
Dictionary storing arbitrary unstructured metadata.

```python
# Store analysis parameters and results
adata.uns['experiment_date'] = '2025-11-03'
adata.uns['pca'] = {
    'variance_ratio': [0.15, 0.10, 0.08],
    'params': {'n_comps': 50}
}
adata.uns['neighbors'] = {
    'params': {'n_neighbors': 15, 'method': 'umap'},
    'connectivities_key': 'connectivities'
}

# Access unstructured data
exp_date = adata.uns['experiment_date']
pca_params = adata.uns['pca']['params']
```

Common uns uses:
- Analysis parameters and settings
- Color palettes for plotting
- Cluster information
- Tool-specific metadata

### raw (Original Data Snapshot)
Optional attribute preserving the original data matrix and variable annotations before filtering.

```python
# Create AnnData and store raw state
adata = ad.AnnData(X=np.random.rand(100, 5000))
adata.var['gene_name'] = [f'Gene_{i}' for i in range(5000)]

# Store raw state before filtering
adata.raw = adata.copy()

# Filter to highly variable genes
highly_variable_mask = np.random.rand(5000) > 0.5
adata = adata[:, highly_variable_mask]

# Access original data
original_matrix = adata.raw.X
original_var = adata.raw.var
```

## Object Properties

```python
# Dimensions
n_observations = adata.n_obs
n_variables = adata.n_vars
shape = adata.shape  # (n_obs, n_vars)

# Index information
obs_names = adata.obs_names  # Observation identifiers
var_names = adata.var_names  # Variable identifiers

# Storage mode
is_view = adata.is_view  # True if this is a view of another object
is_backed = adata.isbacked  # True if backed by on-disk storage
filename = adata.filename  # Path to backing file (if backed)
```

## Creating AnnData Objects

### From arrays and DataFrames
```python
import anndata as ad
import numpy as np
import pandas as pd

# Minimal creation
X = np.random.rand(100, 2000)
adata = ad.AnnData(X)

# With metadata
obs = pd.DataFrame({'cell_type': ['A', 'B'] * 50}, index=[f'cell_{i}' for i in range(100)])
var = pd.DataFrame({'gene_name': [f'Gene_{i}' for i in range(2000)]}, index=[f'ENSG{i:05d}' for i in range(2000)])
adata = ad.AnnData(X=X, obs=obs, var=var)

# With all components
adata = ad.AnnData(
    X=X,
    obs=obs,
    var=var,
    layers={'raw': np.random.randint(0, 100, (100, 2000))},
    obsm={'X_pca': np.random.rand(100, 50)},
    uns={'experiment': 'test'}
)
```

### From DataFrame
```python
# Create from pandas DataFrame (genes as columns, cells as rows)
df = pd.DataFrame(
    np.random.rand(100, 50),
    columns=[f'Gene_{i}' for i in range(50)],
    index=[f'Cell_{i}' for i in range(100)]
)
adata = ad.AnnData(df)
```

## Data Access Patterns

### Vector extraction
```python
# Get observation annotation as array
cell_types = adata.obs_vector('cell_type')

# Get variable values across observations
gene_expression = adata.obs_vector('ACTB')  # If ACTB is in var_names

# Get variable annotation as array
gene_names = adata.var_vector('gene_name')
```

### Subsetting
```python
# By index
subset = adata[0:10, 0:100]  # First 10 obs, first 100 vars

# By name
subset = adata[['cell_1', 'cell_2'], ['ACTB', 'GAPDH']]

# By boolean mask
high_count_cells = adata.obs['total_counts'] > 1000
subset = adata[high_count_cells, :]

# By observation metadata
t_cells = adata[adata.obs['cell_type'] == 'T cell']
```

## Memory Considerations

The AnnData structure is designed for memory efficiency:
- Sparse matrices reduce memory for sparse data
- Views avoid copying data when possible
- Backed mode enables working with data larger than RAM
- Categorical annotations reduce memory for discrete values

```python
# Convert strings to categoricals (more memory efficient)
adata.obs['cell_type'] = adata.obs['cell_type'].astype('category')
adata.strings_to_categoricals()

# Check if object is a view (doesn't own data)
if adata.is_view:
    adata = adata.copy()  # Create independent copy
```

---

## io_operations.md

# Input/Output Operations

AnnData provides comprehensive I/O functionality for reading and writing data in various formats.

## Native Formats

### H5AD (HDF5-based)
The recommended native format for AnnData objects, providing efficient storage and fast access.

#### Writing H5AD files
```python
import anndata as ad

# Write to file
adata.write_h5ad('data.h5ad')

# Write with compression
adata.write_h5ad('data.h5ad', compression='gzip')

# Write with specific compression level (0-9, higher = more compression)
adata.write_h5ad('data.h5ad', compression='gzip', compression_opts=9)
```

#### Reading H5AD files
```python
# Read entire file into memory
adata = ad.read_h5ad('data.h5ad')

# Read in backed mode (lazy loading for large files)
adata = ad.read_h5ad('data.h5ad', backed='r')  # Read-only
adata = ad.read_h5ad('data.h5ad', backed='r+')  # Read-write

# Backed mode enables working with datasets larger than RAM
# Only accessed data is loaded into memory
```

#### Backed mode operations
```python
# Open in backed mode
adata = ad.read_h5ad('large_dataset.h5ad', backed='r')

# Access metadata without loading X into memory
print(adata.obs.head())
print(adata.var.head())

# Subset operations create views
subset = adata[:100, :500]  # View, no data loaded

# Load specific data into memory
X_subset = subset.X[:]  # Now loads this subset

# Convert entire backed object to memory
adata_memory = adata.to_memory()
```

### Zarr
Hierarchical array storage format, optimized for cloud storage and parallel I/O.

#### Writing Zarr
```python
# Write to Zarr store
adata.write_zarr('data.zarr')

# Write with specific chunks (important for performance)
adata.write_zarr('data.zarr', chunks=(100, 100))
```

#### Reading Zarr
```python
# Read Zarr store
adata = ad.read_zarr('data.zarr')
```

#### Remote Zarr access
```python
import fsspec

# Access Zarr from S3
store = fsspec.get_mapper('s3://bucket-name/data.zarr')
adata = ad.read_zarr(store)

# Access Zarr from URL
store = fsspec.get_mapper('https://example.com/data.zarr')
adata = ad.read_zarr(store)
```

## Alternative Input Formats

### CSV/TSV
```python
# Read CSV (genes as columns, cells as rows)
adata = ad.read_csv('data.csv')

# Read with custom delimiter
adata = ad.read_csv('data.tsv', delimiter='\t')

# Specify that first column is row names
adata = ad.read_csv('data.csv', first_column_names=True)
```

### Excel
```python
# Read Excel file
adata = ad.read_excel('data.xlsx')

# Read specific sheet
adata = ad.read_excel('data.xlsx', sheet='Sheet1')
```

### Matrix Market (MTX)
Common format for sparse matrices in genomics.

```python
# Read MTX with associated files
# Requires: matrix.mtx, genes.tsv, barcodes.tsv
adata = ad.read_mtx('matrix.mtx')

# Read with custom gene and barcode files
adata = ad.read_mtx(
    'matrix.mtx',
    var_names='genes.tsv',
    obs_names='barcodes.tsv'
)

# Transpose if needed (MTX often has genes as rows)
adata = adata.T
```

### 10X Genomics formats
```python
# Read 10X h5 format
adata = ad.read_10x_h5('filtered_feature_bc_matrix.h5')

# Read 10X MTX directory
adata = ad.read_10x_mtx('filtered_feature_bc_matrix/')

# Specify genome if multiple present
adata = ad.read_10x_h5('data.h5', genome='GRCh38')
```

### Loom
```python
# Read Loom file
adata = ad.read_loom('data.loom')

# Read with specific observation and variable annotations
adata = ad.read_loom(
    'data.loom',
    obs_names='CellID',
    var_names='Gene'
)
```

### Text files
```python
# Read generic text file
adata = ad.read_text('data.txt', delimiter='\t')

# Read with custom parameters
adata = ad.read_text(
    'data.txt',
    delimiter=',',
    first_column_names=True,
    dtype='float32'
)
```

### UMI tools
```python
# Read UMI tools format
adata = ad.read_umi_tools('counts.tsv')
```

### HDF5 (generic)
```python
# Read from HDF5 file (not h5ad format)
adata = ad.read_hdf('data.h5', key='dataset')
```

## Alternative Output Formats

### CSV
```python
# Write to CSV files (creates multiple files)
adata.write_csvs('output_dir/')

# This creates:
# - output_dir/X.csv (expression matrix)
# - output_dir/obs.csv (observation annotations)
# - output_dir/var.csv (variable annotations)
# - output_dir/uns.csv (unstructured annotations, if possible)

# Skip certain components
adata.write_csvs('output_dir/', skip_data=True)  # Skip X matrix
```

### Loom
```python
# Write to Loom format
adata.write_loom('output.loom')
```

## Reading Specific Elements

For fine-grained control, read specific elements from storage:

```python
from anndata import read_elem

# Read just observation annotations
obs = read_elem('data.h5ad/obs')

# Read specific layer
layer = read_elem('data.h5ad/layers/normalized')

# Read unstructured data element
params = read_elem('data.h5ad/uns/pca_params')
```

## Writing Specific Elements

```python
from anndata import write_elem
import h5py

# Write element to existing file
with h5py.File('data.h5ad', 'a') as f:
    write_elem(f, 'new_layer', adata.X.copy())
```

## Lazy Operations

For very large datasets, use lazy reading to avoid loading entire datasets:

```python
from anndata.experimental import read_elem_lazy

# Lazy read (returns dask array or similar)
X_lazy = read_elem_lazy('large_data.h5ad/X')

# Compute only when needed
subset = X_lazy[:100, :100].compute()
```

## Common I/O Patterns

### Convert between formats
```python
# MTX to H5AD
adata = ad.read_mtx('matrix.mtx').T
adata.write_h5ad('data.h5ad')

# CSV to H5AD
adata = ad.read_csv('data.csv')
adata.write_h5ad('data.h5ad')

# H5AD to Zarr
adata = ad.read_h5ad('data.h5ad')
adata.write_zarr('data.zarr')
```

### Load metadata without data
```python
# Backed mode allows inspecting metadata without loading X
adata = ad.read_h5ad('large_file.h5ad', backed='r')
print(f"Dataset contains {adata.n_obs} observations and {adata.n_vars} variables")
print(adata.obs.columns)
print(adata.var.columns)
# X is not loaded into memory
```

### Append to existing file
```python
# Open in read-write mode
adata = ad.read_h5ad('data.h5ad', backed='r+')

# Modify metadata
adata.obs['new_column'] = values

# Changes are written to disk
```

### Download from URL
```python
import anndata as ad

# Read directly from URL (for h5ad files)
url = 'https://example.com/data.h5ad'
adata = ad.read_h5ad(url, backed='r')  # Streaming access

# For other formats, download first
import urllib.request
urllib.request.urlretrieve(url, 'local_file.h5ad')
adata = ad.read_h5ad('local_file.h5ad')
```

## Performance Tips

### Reading
- Use `backed='r'` for large files you only need to query
- Use `backed='r+'` if you need to modify metadata without loading all data
- H5AD format is generally fastest for random access
- Zarr is better for cloud storage and parallel access
- Consider compression for storage, but note it may slow down reading

### Writing
- Use compression for long-term storage: `compression='gzip'` or `compression='lzf'`
- LZF compression is faster but compresses less than GZIP
- For Zarr, tune chunk sizes based on access patterns:
  - Larger chunks for sequential reads
  - Smaller chunks for random access
- Convert string columns to categorical before writing (smaller files)

### Memory management
```python
# Convert strings to categoricals (reduces file size and memory)
adata.strings_to_categoricals()
adata.write_h5ad('data.h5ad')

# Use sparse matrices for sparse data
from scipy.sparse import csr_matrix
if isinstance(adata.X, np.ndarray):
    density = np.count_nonzero(adata.X) / adata.X.size
    if density < 0.5:  # If more than 50% zeros
        adata.X = csr_matrix(adata.X)
```

## Handling Large Datasets

### Strategy 1: Backed mode
```python
# Work with dataset larger than RAM
adata = ad.read_h5ad('100GB_file.h5ad', backed='r')

# Filter based on metadata (fast, no data loading)
filtered = adata[adata.obs['quality_score'] > 0.8]

# Load filtered subset into memory
adata_memory = filtered.to_memory()
```

### Strategy 2: Chunked processing
```python
# Process data in chunks
adata = ad.read_h5ad('large_file.h5ad', backed='r')

chunk_size = 1000
results = []

for i in range(0, adata.n_obs, chunk_size):
    chunk = adata[i:i+chunk_size, :].to_memory()
    # Process chunk
    result = process(chunk)
    results.append(result)
```

### Strategy 3: Use AnnCollection
```python
from anndata.experimental import AnnCollection

# Create collection without loading data
adatas = [f'dataset_{i}.h5ad' for i in range(10)]
collection = AnnCollection(
    adatas,
    join_obs='inner',
    join_vars='inner'
)

# Process collection lazily
# Data is loaded only when accessed
```

## Common Issues and Solutions

### Issue: Out of memory when reading
**Solution**: Use backed mode or read in chunks
```python
adata = ad.read_h5ad('file.h5ad', backed='r')
```

### Issue: Slow reading from cloud storage
**Solution**: Use Zarr format with appropriate chunking
```python
adata.write_zarr('data.zarr', chunks=(1000, 1000))
```

### Issue: Large file sizes
**Solution**: Use compression and convert to sparse/categorical
```python
adata.strings_to_categoricals()
from scipy.sparse import csr_matrix
adata.X = csr_matrix(adata.X)
adata.write_h5ad('compressed.h5ad', compression='gzip')
```

### Issue: Cannot modify backed object
**Solution**: Either load to memory or open in 'r+' mode
```python
# Option 1: Load to memory
adata = adata.to_memory()

# Option 2: Open in read-write mode
adata = ad.read_h5ad('file.h5ad', backed='r+')
```

---

## manipulation.md

# Data Manipulation

Operations for transforming, subsetting, and manipulating AnnData objects.

## Subsetting

### By indices
```python
import anndata as ad
import numpy as np

adata = ad.AnnData(X=np.random.rand(1000, 2000))

# Integer indices
subset = adata[0:100, 0:500]  # First 100 obs, first 500 vars

# List of indices
obs_indices = [0, 10, 20, 30, 40]
var_indices = [0, 1, 2, 3, 4]
subset = adata[obs_indices, var_indices]

# Single observation or variable
single_obs = adata[0, :]
single_var = adata[:, 0]
```

### By names
```python
import pandas as pd

# Create with named indices
obs_names = [f'cell_{i}' for i in range(1000)]
var_names = [f'gene_{i}' for i in range(2000)]
adata = ad.AnnData(
    X=np.random.rand(1000, 2000),
    obs=pd.DataFrame(index=obs_names),
    var=pd.DataFrame(index=var_names)
)

# Subset by observation names
subset = adata[['cell_0', 'cell_1', 'cell_2'], :]

# Subset by variable names
subset = adata[:, ['gene_0', 'gene_10', 'gene_20']]

# Both axes
subset = adata[['cell_0', 'cell_1'], ['gene_0', 'gene_1']]
```

### By boolean masks
```python
# Create boolean masks
high_count_obs = np.random.rand(1000) > 0.5
high_var_genes = np.random.rand(2000) > 0.7

# Subset using masks
subset = adata[high_count_obs, :]
subset = adata[:, high_var_genes]
subset = adata[high_count_obs, high_var_genes]
```

### By metadata conditions
```python
# Add metadata
adata.obs['cell_type'] = np.random.choice(['A', 'B', 'C'], 1000)
adata.obs['quality_score'] = np.random.rand(1000)
adata.var['highly_variable'] = np.random.rand(2000) > 0.8

# Filter by cell type
t_cells = adata[adata.obs['cell_type'] == 'A']

# Filter by multiple conditions
high_quality_a_cells = adata[
    (adata.obs['cell_type'] == 'A') &
    (adata.obs['quality_score'] > 0.7)
]

# Filter by variable metadata
hv_genes = adata[:, adata.var['highly_variable']]

# Complex conditions
filtered = adata[
    (adata.obs['quality_score'] > 0.5) &
    (adata.obs['cell_type'].isin(['A', 'B'])),
    adata.var['highly_variable']
]
```

## Transposition

```python
# Transpose AnnData object (swap observations and variables)
adata_T = adata.T

# Shape changes
print(adata.shape)    # (1000, 2000)
print(adata_T.shape)  # (2000, 1000)

# obs and var are swapped
print(adata.obs.head())   # Observation metadata
print(adata_T.var.head()) # Same data, now as variable metadata

# Useful when data is in opposite orientation
# Common with some file formats where genes are rows
```

## Copying

### Full copy
```python
# Create independent copy
adata_copy = adata.copy()

# Modifications to copy don't affect original
adata_copy.obs['new_column'] = 1
print('new_column' in adata.obs.columns)  # False
```

### Shallow copy
```python
# View (doesn't copy data, modifications affect original)
adata_view = adata[0:100, :]

# Check if object is a view
print(adata_view.is_view)  # True

# Convert view to independent copy
adata_independent = adata_view.copy()
print(adata_independent.is_view)  # False
```

## Renaming

### Rename observations and variables
```python
# Rename all observations
adata.obs_names = [f'new_cell_{i}' for i in range(adata.n_obs)]

# Rename all variables
adata.var_names = [f'new_gene_{i}' for i in range(adata.n_vars)]

# Make names unique (add suffix to duplicates)
adata.obs_names_make_unique()
adata.var_names_make_unique()
```

### Rename categories
```python
# Create categorical column
adata.obs['cell_type'] = pd.Categorical(['A', 'B', 'C'] * 333 + ['A'])

# Rename categories
adata.rename_categories('cell_type', ['Type_A', 'Type_B', 'Type_C'])

# Or using dictionary
adata.rename_categories('cell_type', {
    'Type_A': 'T_cell',
    'Type_B': 'B_cell',
    'Type_C': 'Monocyte'
})
```

## Type Conversions

### Strings to categoricals
```python
# Convert string columns to categorical (more memory efficient)
adata.obs['cell_type'] = ['TypeA', 'TypeB'] * 500
adata.obs['tissue'] = ['brain', 'liver'] * 500

# Convert all string columns to categorical
adata.strings_to_categoricals()

print(adata.obs['cell_type'].dtype)  # category
print(adata.obs['tissue'].dtype)     # category
```

### Sparse to dense and vice versa
```python
from scipy.sparse import csr_matrix

# Dense to sparse
if not isinstance(adata.X, csr_matrix):
    adata.X = csr_matrix(adata.X)

# Sparse to dense
if isinstance(adata.X, csr_matrix):
    adata.X = adata.X.toarray()

# Convert layer
adata.layers['normalized'] = csr_matrix(adata.layers['normalized'])
```

## Chunked Operations

Process large datasets in chunks:

```python
# Iterate through data in chunks
chunk_size = 100
for chunk in adata.chunked_X(chunk_size):
    # Process chunk
    result = process_chunk(chunk)
```

## Extracting Vectors

### Get observation vectors
```python
# Get observation metadata as array
cell_types = adata.obs_vector('cell_type')

# Get gene expression across observations
actb_expression = adata.obs_vector('ACTB')  # If ACTB in var_names
```

### Get variable vectors
```python
# Get variable metadata as array
gene_names = adata.var_vector('gene_name')
```

## Adding/Modifying Data

### Add observations
```python
# Create new observations
new_obs = ad.AnnData(X=np.random.rand(100, adata.n_vars))
new_obs.var_names = adata.var_names

# Concatenate with existing
adata_extended = ad.concat([adata, new_obs], axis=0)
```

### Add variables
```python
# Create new variables
new_vars = ad.AnnData(X=np.random.rand(adata.n_obs, 100))
new_vars.obs_names = adata.obs_names

# Concatenate with existing
adata_extended = ad.concat([adata, new_vars], axis=1)
```

### Add metadata columns
```python
# Add observation annotation
adata.obs['new_score'] = np.random.rand(adata.n_obs)

# Add variable annotation
adata.var['new_label'] = ['label'] * adata.n_vars

# Add from external data
external_data = pd.read_csv('metadata.csv', index_col=0)
adata.obs['external_info'] = external_data.loc[adata.obs_names, 'column']
```

### Add layers
```python
# Add new layer
adata.layers['raw_counts'] = np.random.randint(0, 100, adata.shape)
adata.layers['log_transformed'] = np.log1p(adata.X)

# Replace layer
adata.layers['normalized'] = new_normalized_data
```

### Add embeddings
```python
# Add PCA
adata.obsm['X_pca'] = np.random.rand(adata.n_obs, 50)

# Add UMAP
adata.obsm['X_umap'] = np.random.rand(adata.n_obs, 2)

# Add multiple embeddings
adata.obsm['X_tsne'] = np.random.rand(adata.n_obs, 2)
adata.obsm['X_diffmap'] = np.random.rand(adata.n_obs, 10)
```

### Add pairwise relationships
```python
from scipy.sparse import csr_matrix

# Add nearest neighbor graph
n_obs = adata.n_obs
knn_graph = csr_matrix(np.random.rand(n_obs, n_obs) > 0.95)
adata.obsp['connectivities'] = knn_graph

# Add distance matrix
adata.obsp['distances'] = csr_matrix(np.random.rand(n_obs, n_obs))
```

### Add unstructured data
```python
# Add analysis parameters
adata.uns['pca'] = {
    'variance': [0.2, 0.15, 0.1],
    'variance_ratio': [0.4, 0.3, 0.2],
    'params': {'n_comps': 50}
}

# Add color schemes
adata.uns['cell_type_colors'] = ['#FF0000', '#00FF00', '#0000FF']
```

## Removing Data

### Remove observations or variables
```python
# Keep only specific observations
keep_obs = adata.obs['quality_score'] > 0.5
adata = adata[keep_obs, :]

# Remove specific variables
remove_vars = adata.var['low_count']
adata = adata[:, ~remove_vars]
```

### Remove metadata columns
```python
# Remove observation column
adata.obs.drop('unwanted_column', axis=1, inplace=True)

# Remove variable column
adata.var.drop('unwanted_column', axis=1, inplace=True)
```

### Remove layers
```python
# Remove specific layer
del adata.layers['unwanted_layer']

# Remove all layers
adata.layers = {}
```

### Remove embeddings
```python
# Remove specific embedding
del adata.obsm['X_tsne']

# Remove all embeddings
adata.obsm = {}
```

### Remove unstructured data
```python
# Remove specific key
del adata.uns['unwanted_key']

# Remove all unstructured data
adata.uns = {}
```

## Reordering

### Sort observations
```python
# Sort by observation metadata
adata = adata[adata.obs.sort_values('quality_score').index, :]

# Sort by observation names
adata = adata[sorted(adata.obs_names), :]
```

### Sort variables
```python
# Sort by variable metadata
adata = adata[:, adata.var.sort_values('gene_name').index]

# Sort by variable names
adata = adata[:, sorted(adata.var_names)]
```

### Reorder to match external list
```python
# Reorder observations to match external list
desired_order = ['cell_10', 'cell_5', 'cell_20', ...]
adata = adata[desired_order, :]

# Reorder variables
desired_genes = ['TP53', 'ACTB', 'GAPDH', ...]
adata = adata[:, desired_genes]
```

## Data Transformations

### Normalize
```python
# Total count normalization (CPM/TPM-like)
total_counts = adata.X.sum(axis=1)
adata.layers['normalized'] = adata.X / total_counts[:, np.newaxis] * 1e6

# Log transformation
adata.layers['log1p'] = np.log1p(adata.X)

# Z-score normalization
mean = adata.X.mean(axis=0)
std = adata.X.std(axis=0)
adata.layers['scaled'] = (adata.X - mean) / std
```

### Filter
```python
# Filter cells by total counts
total_counts = np.array(adata.X.sum(axis=1)).flatten()
adata.obs['total_counts'] = total_counts
adata = adata[adata.obs['total_counts'] > 1000, :]

# Filter genes by detection rate
detection_rate = (adata.X > 0).sum(axis=0) / adata.n_obs
adata.var['detection_rate'] = np.array(detection_rate).flatten()
adata = adata[:, adata.var['detection_rate'] > 0.01]
```

## Working with Views

Views are lightweight references to subsets of data that don't copy the underlying matrix:

```python
# Create view
view = adata[0:100, 0:500]
print(view.is_view)  # True

# Views allow read access
data = view.X

# Modifying view data affects original
# (Be careful!)

# Convert view to independent copy
independent = view.copy()

# Force AnnData to be a copy, not a view
adata = adata.copy()
```

## Merging Metadata

```python
# Merge external metadata
external_metadata = pd.read_csv('additional_metadata.csv', index_col=0)

# Join metadata (inner join on index)
adata.obs = adata.obs.join(external_metadata)

# Left join (keep all adata observations)
adata.obs = adata.obs.merge(
    external_metadata,
    left_index=True,
    right_index=True,
    how='left'
)
```

## Common Manipulation Patterns

### Quality control filtering
```python
# Calculate QC metrics
adata.obs['n_genes'] = (adata.X > 0).sum(axis=1)
adata.obs['total_counts'] = adata.X.sum(axis=1)
adata.var['n_cells'] = (adata.X > 0).sum(axis=0)

# Filter low-quality cells
adata = adata[adata.obs['n_genes'] > 200, :]
adata = adata[adata.obs['total_counts'] < 50000, :]

# Filter rarely detected genes
adata = adata[:, adata.var['n_cells'] >= 3]
```

### Select highly variable genes
```python
# Mark highly variable genes
gene_variance = np.var(adata.X, axis=0)
adata.var['variance'] = np.array(gene_variance).flatten()
adata.var['highly_variable'] = adata.var['variance'] > np.percentile(gene_variance, 90)

# Subset to highly variable genes
adata_hvg = adata[:, adata.var['highly_variable']].copy()
```

### Downsample
```python
# Random sampling of observations
np.random.seed(42)
n_sample = 500
sample_indices = np.random.choice(adata.n_obs, n_sample, replace=False)
adata_downsampled = adata[sample_indices, :].copy()

# Stratified sampling by cell type
from sklearn.model_selection import train_test_split
train_idx, test_idx = train_test_split(
    range(adata.n_obs),
    test_size=0.2,
    stratify=adata.obs['cell_type']
)
adata_train = adata[train_idx, :].copy()
adata_test = adata[test_idx, :].copy()
```

### Split train/test
```python
# Random train/test split
np.random.seed(42)
n_obs = adata.n_obs
train_size = int(0.8 * n_obs)
indices = np.random.permutation(n_obs)
train_indices = indices[:train_size]
test_indices = indices[train_size:]

adata_train = adata[train_indices, :].copy()
adata_test = adata[test_indices, :].copy()
```
