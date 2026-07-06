## Data Loading & Chain QC

_modules: data-io, qc, chain-qc_

```python
import scirpy as ir
import scanpy as sc

# Load existing scRNA-seq AnnData
adata = sc.read_h5ad('scrnaseq.h5ad')

# Attach VDJ annotations from 10x filtered_contig_annotations.csv
ir.io.read_10x_vdj(adata, 'filtered_contig_annotations.csv')

# Alternatively, load from AIRR-format rearrangement table
# ir.io.read_airr(adata, 'airr_rearrangement.tsv')

# Receptor chain QC: categorizes cells as multichain (doublet),
# orphan (single chain), extra, or ambiguous pairings
ir.tl.chain_qc(adata)

# Visualize chain-pairing categories by receptor subtype
ir.pl.group_abundance(adata, groupby='chain_pairing', target_col='receptor_subtype')
```

## Clonotype Definition

_modules: clonotype, ir-dist, cdr3_

```python
# Compute CDR3 distance matrix using amino-acid identity (cutoff=0 => exact match)
ir.pp.ir_dist(
    adata,
    metric='identity',
    sequence='aa',
    cutoff=0,
)

# Define clonotypes requiring all receptor arms to match,
# using only the primary VDJ/VJ chain per locus
ir.tl.define_clonotypes(adata, receptor_arms='all', dual_ir='primary_only')

# Sanity check: number of unique clonotypes
print(f"Unique clonotypes: {adata.obs['clone_id'].nunique()}")
```

## Clonal Expansion Analysis

_modules: clonal-expansion, expansion_

```python
# Assign expansion category per cell: 1 (singleton), 2, 3-10, >10
ir.tl.clonal_expansion(adata)

# Plot expansion categories stratified by cell type
ir.pl.clonal_expansion(adata, groupby='cell_type')
```

## Repertoire Diversity & Comparison

_modules: diversity, repertoire-overlap, alpha-diversity_

```python
# Repertoire overlap (Jaccard) of clonotypes between samples
diversity = ir.tl.repertoire_overlap(
    adata,
    groupby='sample',
    target_col='clone_id',
    metric='jaccard',
)

# Alpha diversity per sample
ir.tl.alpha_diversity(adata, groupby='sample', target_col='clone_id')

# Clonotype sharing across conditions (top clonotypes)
ir.pl.group_abundance(
    adata,
    groupby='clone_id',
    target_col='condition',
    max_cols=20,
)

# Repertoire overlap heatmap between samples
ir.pl.repertoire_overlap(adata, groupby='sample', target_col='clone_id')
```

## V(D)J Gene Usage

_modules: vdj-usage, spectratype, gene-usage_

```python
# V gene usage for TRA and TRB chains
ir.pl.vdj_usage(
    adata,
    vdj_cols=['v_call_TRA', 'v_call_TRB'],
    full_names=False,
)

# CDR3 length distribution (spectratype) for TRB, stratified by cell type
ir.pl.spectratype(adata, chain='TRB', target_col='cell_type')
```

## Gene Expression Integration

_modules: integration, gene-expression, rank-genes, umap_

```python
# Subset to cells with a detected immune receptor
adata_tcr = adata[adata.obs['has_ir'] == 'True'].copy()

# Define expanded vs non-expanded label
adata_tcr.obs['is_expanded'] = adata_tcr.obs['clonal_expansion'].isin(['3-10', '>10'])

# Differential expression: expanded vs non-expanded
sc.tl.rank_genes_groups(adata_tcr, groupby='is_expanded')
sc.pl.rank_genes_groups(adata_tcr, n_genes=20)

# UMAP colored by cell type and clonal expansion
sc.pl.umap(adata_tcr, color=['cell_type', 'clonal_expansion'])
```

## Export for Downstream Analysis

_modules: export, airr, data-io_

```python
# Export clonotype summary table
clonotypes = adata.obs[['clone_id', 'IR_VDJ_1_junction_aa', 'IR_VJ_1_junction_aa',
                        'IR_VDJ_1_v_call', 'IR_VDJ_1_j_call']].drop_duplicates()
clonotypes.to_csv('clonotypes.csv')

# Export AIRR-format rearrangement table for VDJtools / other tools
ir.io.write_airr(adata, 'scirpy_airr.tsv')
```
