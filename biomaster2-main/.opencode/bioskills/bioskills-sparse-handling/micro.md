## Sparsity Assessment & Format Conversion

_modules: sparsity, csr, csc, conversion, memory_

```python
import numpy as np
import scipy.sparse as sp
import pandas as pd

# Calculate sparsity (proportion of zeros)
def check_sparsity(counts):
    zeros = (counts == 0).sum().sum()
    total = counts.size
    sparsity = zeros / total
    print(f'Sparsity: {sparsity:.1%} ({zeros:,} / {total:,} zeros)')
    return sparsity

# Rule of thumb: use sparse if >50% zeros

# From pandas DataFrame to sparse
dense_df = pd.read_csv('counts.csv', index_col=0)
sparse_matrix = sp.csr_matrix(dense_df.values)

# Keep row/column names
gene_names = dense_df.index.tolist()
sample_names = dense_df.columns.tolist()

# CSR vs CSC
# CSR (Compressed Sparse Row): efficient row slicing, matrix-vector products
# CSC (Compressed Sparse Column): efficient column slicing
sparse_csr = sp.csr_matrix(dense_df.values)  # Row-oriented
sparse_csc = sp.csc_matrix(dense_df.values)  # Column-oriented

# Convert sparse back to dense
dense_array = sparse_matrix.toarray()
dense_df = pd.DataFrame(
    sparse_matrix.toarray(),
    index=gene_names,
    columns=sample_names
)

# Memory comparison
def compare_memory(dense, sparse):
    dense_mb = dense.nbytes / 1e6
    sparse_mb = (sparse.data.nbytes + sparse.indices.nbytes + sparse.indptr.nbytes) / 1e6
    ratio = dense_mb / sparse_mb
    print(f'Dense:  {dense_mb:.1f} MB')
    print(f'Sparse: {sparse_mb:.1f} MB')
    print(f'Ratio:  {ratio:.1f}x smaller')
    return ratio

sparse = sp.csr_matrix(counts.values)
compare_memory(counts.values, sparse)
```

## Sparse Persistence & I/O

_modules: io, npz, anndata, h5ad, 10x, mtx_

```python
import scipy.sparse as sp
import numpy as np
import anndata as ad
import pandas as pd
import scipy.io

# Save sparse matrix
sp.save_npz('counts_sparse.npz', sparse_matrix)

# Save with metadata
np.savez('counts_with_meta.npz',
    data=sparse_matrix.data,
    indices=sparse_matrix.indices,
    indptr=sparse_matrix.indptr,
    shape=sparse_matrix.shape,
    genes=np.array(gene_names),
    samples=np.array(sample_names))

# Load sparse matrix
sparse_matrix = sp.load_npz('counts_sparse.npz')

# Load with metadata
loaded = np.load('counts_with_meta.npz', allow_pickle=True)
sparse_matrix = sp.csr_matrix(
    (loaded['data'], loaded['indices'], loaded['indptr']),
    shape=tuple(loaded['shape']))
gene_names = loaded['genes'].tolist()

# Create AnnData with sparse matrix (cells/samples as rows, genes as columns)
adata = ad.AnnData(
    X=sp.csr_matrix(counts.T.values),  # Transpose for samples-as-rows
    obs=pd.DataFrame(index=counts.columns),
    var=pd.DataFrame(index=counts.index)
)

# Save (automatically handles sparse)
adata.write_h5ad('counts.h5ad')

# Load and check storage type
adata = ad.read_h5ad('counts.h5ad')
print(f'Matrix type: {type(adata.X)}')

# 10X Matrix format
matrix = scipy.io.mmread('matrix.mtx').T.tocsr()  # Transpose and convert to CSR
features = pd.read_csv('features.tsv', sep='\t', header=None)
barcodes = pd.read_csv('barcodes.tsv', sep='\t', header=None)
gene_names = features[1].tolist()  # Gene symbols
cell_barcodes = barcodes[0].tolist()

# Write 10X format
scipy.io.mmwrite('output_matrix.mtx', sparse_matrix)
```

## Sparse Operations & Subsetting

_modules: operations, filtering, subsetting, log-transform, arithmetic_

```python
import numpy as np
import scipy.sparse as sp

# Row sums (gene totals)
row_sums = np.array(sparse_matrix.sum(axis=1)).flatten()

# Column sums (sample totals)
col_sums = np.array(sparse_matrix.sum(axis=0)).flatten()

# Filter rows by sum (keep genes with >10 total counts)
keep_mask = row_sums > 10
sparse_filtered = sparse_matrix[keep_mask, :]

# Filter columns (keep samples with >1000 counts)
keep_cols = col_sums > 1000
sparse_filtered = sparse_matrix[:, keep_cols]

# Log transform (operate on nonzero data only)
sparse_log = sparse_matrix.copy()
sparse_log.data = np.log1p(sparse_log.data)

# Select specific genes
gene_idx = [gene_names.index(g) for g in ['TP53', 'BRCA1', 'MYC'] if g in gene_names]
subset = sparse_matrix[gene_idx, :]

# Select specific samples
sample_idx = [sample_names.index(s) for s in ['sample1', 'sample2']]
subset = sparse_matrix[:, sample_idx]

# Boolean indexing
expressed = row_sums > 0
sparse_expressed = sparse_matrix[expressed, :]

# Sparse-Dense arithmetic gotcha: adding a dense array to a sparse matrix
# can return a deprecated numpy.matrix. Always convert explicitly.
result_good = np.asarray((sparse_matrix + dense_array))
```

## Sparse Normalization

_modules: normalization, cpm, log1p, sparsity-monitoring_

```python
import numpy as np
import scipy.sparse as sp
import scanpy as sc

def normalize_sparse_cpm(sparse_matrix):
    '''CPM normalization for sparse matrix.'''
    lib_sizes = np.array(sparse_matrix.sum(axis=0)).flatten()
    scaling_factors = 1e6 / lib_sizes
    normalized = sparse_matrix.multiply(scaling_factors)  # Broadcasts across columns
    return normalized

def normalize_sparse_log1p(sparse_matrix):
    '''Log1p transform sparse matrix in place.'''
    result = sparse_matrix.copy()
    result.data = np.log1p(result.data)
    return result

cpm = normalize_sparse_cpm(sparse_matrix)
log_cpm = normalize_sparse_log1p(cpm)

# Monitor sparsity before and after transformation
def check_sparsity_after_transform(sparse_matrix, transform_name='original'):
    nnz = sparse_matrix.nnz
    total = sparse_matrix.shape[0] * sparse_matrix.shape[1]
    sparsity = 1 - (nnz / total)
    print(f'{transform_name}: {sparsity:.1%} sparse ({nnz:,} nonzero / {total:,} total)')
    return sparsity

check_sparsity_after_transform(adata.X, 'raw')
sc.pp.normalize_total(adata, target_sum=1e4)
sc.pp.log1p(adata)
check_sparsity_after_transform(adata.X, 'after log1p')

# Rule of thumb: if sparsity drops below ~50% after transformation,
# convert back to dense -- the sparse index overhead outweighs the benefit.
```

## Large-Scale Backed Processing

_modules: backed-mode, chunking, large-data, memory_

```python
import scanpy as sc
import anndata as ad
import numpy as np

# Read-only backed mode -- data stays on disk, loaded on demand
adata = sc.read_h5ad('large_dataset.h5ad', backed='r')
print(f'Shape: {adata.shape}, Type: {type(adata.X)}')

# Only the accessed slice is loaded into memory
subset = adata[adata.obs['cell_type'] == 'T_cell', :].to_memory()

# Backed mode limitations:
# - Only the X matrix supports backed access; obs/var are fully loaded
# - Very large sparse H5AD files (>35 GB) can still cause memory issues
# - Write mode (backed='r+') only supports updates to X, not obs/var
# - Many scanpy functions require in-memory data; use .to_memory() for subsets

# For datasets too large for backed mode, process in chunks
def process_in_chunks(h5ad_path, chunk_size=10000, func=None):
    '''Process large H5AD file in cell chunks.'''
    adata = sc.read_h5ad(h5ad_path, backed='r')
    n_cells = adata.shape[0]
    results = []
    for start in range(0, n_cells, chunk_size):
        end = min(start + chunk_size, n_cells)
        chunk = adata[start:end].to_memory()
        if func:
            chunk = func(chunk)
        results.append(chunk)
    return ad.concat(results)
```
