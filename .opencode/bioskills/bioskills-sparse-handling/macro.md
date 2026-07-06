# Bioskills Sparse Handling

## Overview

This skill provides memory-efficient storage, manipulation, and normalization of zero-heavy expression matrices — the norm in single-cell RNA-seq, where most entries are zero. It covers assessing whether a matrix is sparse enough to benefit from sparse storage, converting between dense (numpy/pandas) and sparse (CSR/CSC) representations, persisting sparse data to disk (.npz, H5AD, 10X mtx), performing common operations (sums, filtering, subsetting, log transforms) directly on sparse matrices, applying CPM/log normalization while preserving sparsity, and scaling to datasets too large for memory via AnnData backed mode and chunked processing.

Inputs: a count matrix from CSV, Market Matrix (.mtx), or H5AD. Outputs: a sparse-stored matrix (CSR/CSC, .npz, or AnnData/H5AD) ready for downstream analysis.

Use whenever working with single-cell or other high-sparsity expression data where dense storage would waste memory. Reference examples were tested with numpy 1.26+ and pandas 2.2+; if code throws ImportError, AttributeError, or TypeError, introspect the installed package (e.g. `pip show <package>` then `help(module.function)`) and adapt the example to the actual API rather than retrying.

## Sparsity Assessment & Format Conversion

Determine whether a count matrix is sparse enough to benefit from sparse storage (rule of thumb: more than 50% zeros), then convert between dense (numpy array or pandas DataFrame) and sparse (CSR/CSC) representations while preserving gene and sample names. CSR (Compressed Sparse Row) is row-oriented and efficient for row slicing and matrix-vector products; CSC (Compressed Sparse Column) is column-oriented and efficient for column slicing. Compare the dense and sparse memory footprints to confirm the benefit before committing to sparse storage.

## Sparse Persistence & I/O

Save and load sparse matrices efficiently using scipy's npz format, optionally bundling metadata (gene and sample names) alongside the sparse data arrays so they can be reconstructed on load. Wrap sparse matrices in AnnData objects with cells as rows and genes as columns, then persist as H5AD, which handles sparse storage automatically. Read and write 10X-style Market Matrix files (matrix.mtx paired with features.tsv and barcodes.tsv), transposing and converting to CSR on read.

## Sparse Operations & Subsetting

Perform common matrix operations directly on sparse matrices without densifying: compute row and column sums for QC, filter genes or cells by total counts, apply log1p transforms in-place on the nonzero data array, and subset by gene or sample indices and boolean masks. Be cautious with sparse-dense arithmetic, which can return a deprecated numpy.matrix type rather than a regular array — always wrap results with np.asarray to avoid downstream issues.

## Sparse Normalization

Apply CPM normalization and log transformation to a sparse count matrix while keeping it sparse. Compute library sizes from column sums, broadcast per-cell scaling factors via sparse multiply for CPM, then transform only the nonzero data array in-place with log1p. Monitor sparsity before and after transformation, because normalization can move zeros to non-zero values; if sparsity drops below roughly 50%, convert back to dense format since the sparse index overhead then outweighs the benefit of skipping zeros.

## Large-Scale Backed Processing

Handle H5AD files too large to fit in memory by opening them in backed mode, where only accessed slices are loaded from disk on demand. Be aware of backed-mode limitations: only the X matrix supports backed access (obs and var are fully loaded), very large sparse H5AD files above roughly 35 GB can still cause memory issues, write mode (backed='r+') only supports updates to X, and many scanpy functions require in-memory data — use .to_memory() to materialize subsets. For datasets exceeding backed-mode limits, process in cell chunks by iterating over row ranges, materializing each chunk, applying a function, and concatenating results.
