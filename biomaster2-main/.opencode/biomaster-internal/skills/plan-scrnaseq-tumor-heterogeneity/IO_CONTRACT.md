# IO Contract: tumor_scrnaseq_heterogeneity

## Inputs
- test mode: demo dataset `maynard2020_3k` (Scanpy built-in or project subset)
- formal mode: h5ad or 10x matrix + sample metadata table

## Outputs
- QC AnnData (`adata_qc.h5ad`)
- annotated AnnData (`adata_annotated.h5ad`)
- inferCNV outputs (`infercnv/`)
- Palantir outputs (`palantir/`)
- cNMF outputs (`cnmf/`)
- final report (`REPORT.md`)
