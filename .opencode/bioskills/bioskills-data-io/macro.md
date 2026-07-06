# Bioskills Data Io

## Overview

This workflow handles reading, writing, and creating single-cell data objects for downstream analysis in both Python (Scanpy/AnnData) and R (Seurat). It covers loading 10X Genomics Cell Ranger output (MTX directories and h5 files), constructing objects from raw count matrices, reading and writing native serialization formats (h5ad, RDS, CSV, Loom), manipulating cell/gene metadata and subsetting objects, and converting between Seurat and AnnData formats via the h5Seurat bridge.

Inputs are count matrices or Cell Ranger output directories; outputs are in-memory AnnData or Seurat objects plus serialized files (h5ad, RDS). Use this skill at the very start of any single-cell analysis to get data into a workable object before preprocessing, clustering, or annotation.

Reference versions: Cell Ranger 8.0+, anndata 0.10+, numpy 1.26+, pandas 2.2+, scanpy 1.10+, Seurat v5. Before using the code patterns, verify installed versions match (Python: `pip show <package>` then `help(module.function)`; R: `packageVersion('<pkg>')` then `?function_name`). If code throws ImportError, AttributeError, or TypeError, introspect the installed package and adapt the example to the actual API rather than retrying.

Common data formats: 10X MTX (folder, Cellranger output, both tools), 10X h5 (.h5, Cellranger HDF5, both), h5ad (.h5ad, AnnData native, Scanpy), RDS (.rds, R serialized, Seurat), Loom (.loom, HDF5-based, both), h5Seurat (.h5seurat, Seurat HDF5, Seurat).

Related skills: preprocessing (QC filtering and normalization after loading), clustering (dimensionality reduction and clustering), markers-annotation (find marker genes and annotate cell types).

## Reading 10X Genomics Data

Load 10X Genomics Cell Ranger output into single-cell objects. Both Scanpy and Seurat can read the filtered_feature_bc_matrix directory (the barcodes/features/matrix tsv.gz triplet) or the bundled .h5 HDF5 file directly. The result is an expression matrix indexed by cell barcodes and gene annotations, ready for QC and preprocessing. Always use the filtered (not raw) matrix for analysis. Seurat's CreateSeuratObject applies basic gene/cell filters (min.cells, min.features) at creation time; Scanpy leaves filtering to a later QC step.

## Creating Objects from Matrices

Build single-cell objects from raw count matrices when starting from non-10X data (simulated data, exported CSVs, or custom pipelines). Understand the object structure so downstream steps can address the right slot. AnnData stores X (expression matrix, cells x genes), obs (cell metadata DataFrame), var (gene metadata DataFrame), uns (unstructured dict), obsm/varm (cell/gene embeddings), obsp (cell-cell graphs), and layers (alternative matrices such as raw counts or normalized values). Seurat v5 uses layers (counts, data, scale.data) instead of slots, plus meta.data, reductions, and graphs.

## Reading and Writing Native Formats

Serialize and reload single-cell objects using each ecosystem's native format. AnnData uses h5ad (HDF5-based); Seurat uses RDS (R serialization). Both can also read CSV/TSV, Loom, and plain text. Use gzip compression for large h5ad files. These formats preserve metadata, layers, and embeddings across sessions, so they are the standard way to checkpoint an analysis between steps.

## Metadata, Subsetting, and Raw Counts

Annotate cells and genes with metadata, subset objects by boolean masks or feature lists, and preserve raw counts before normalization. In AnnData, metadata lives in obs/var and unstructured annotations in uns; raw counts can be stored in adata.raw (a frozen copy) or adata.layers['counts']. In Seurat, metadata is in meta.data (add via the $ operator or AddMetaData) and raw counts live in the counts layer. Subsetting uses boolean indexing on AnnData and the subset() function on Seurat objects.

## Merging and Format Conversion

Combine multiple single-cell objects (e.g. per-sample Seurat objects) into one and convert between Seurat (R) and AnnData (Python) formats. Seurat's merge() concatenates objects with unique cell prefixes via add.cell.ids; in v5 call JoinLayers afterward to unify the split count layers that merge produces. Cross-language conversion uses SeuratDisk's h5Seurat format as a bridge: save Seurat as h5Seurat then Convert to h5ad (or vice versa), then load the result in the other language.
