---
name: discipline-scrnaseq
description: Define scRNA-seq input requirements and generic analysis conventions.
compatibility: opencode
metadata:
  layer: discipline
  discipline: scrnaseq
  domain: bioinformatics
  status: active
---

# scRNA-seq Discipline Guide

## Purpose
Define scRNA-seq input formats, QC norms, and generic workflow stages without binding a tumor-specific pipeline.

## Inputs
- h5ad AnnData
- 10x matrix bundle (matrix.mtx, genes.tsv, barcodes.tsv)
- filtered feature-barcode matrix

## Generic stages
data loading → QC → normalization → HVG → PCA/UMAP → clustering → annotation

## Boundaries
Do not bind inferCNVpy, Palantir, or cNMF unless pipeline-scrnaseq-tumor is selected.
