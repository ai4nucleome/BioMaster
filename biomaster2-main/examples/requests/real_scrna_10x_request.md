# Complex Example Request: scRNA-seq 10x Matrix QC

## Goal

Please inspect the 10x-style single-cell RNA-seq matrix and produce a lightweight QC summary.

## Data Paths

- MatrixMarket file: `./examples/real_data/10x_matrix_subset.mtx`
- Barcodes: `./examples/real_data/10x_barcodes_subset.tsv`
- Genes: `./examples/real_data/10x_genes_subset.tsv`

## Analysis Parameters

- Input type: 10x-like sparse matrix bundle
- Gene annotation file: two-column gene ID and gene symbol table
- Cell barcode file: one barcode per row

## Execution Permission

Execution is allowed for lightweight parsing, validation, and summary generation.

## Expected Outputs

- Validate that matrix dimensions match the gene and barcode files.
- Summarize genes, cells, nonzero entries, and simple per-cell count totals.
- Report whether the input is structurally suitable for downstream Scanpy or Seurat workflows.
- Save summary outputs under `./examples/results/scrna_10x/`.
