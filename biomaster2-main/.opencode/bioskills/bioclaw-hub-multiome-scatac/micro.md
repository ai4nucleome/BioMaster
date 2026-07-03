## QC both modalities

_modules: qc, rna-qc, atac-qc, filtering_

```python
# RNA QC
import scanpy as sc

sc.pp.filter_cells(adata_rna, min_genes=200)
sc.pp.filter_genes(adata_rna, min_cells=3)
adata_rna.var['mt'] = adata_rna.var_names.str.startswith('MT-')
sc.pp.calculate_qc_metrics(adata_rna, qc_vars=['mt'], percent_top=None, log1p=False)

# Filter RNA cells by mitochondrial percent (e.g. < 20%)
adata_rna = adata_rna[adata_rna.obs['pct_counts_mt'] < 20, :].copy()

# ATAC QC
# Compute ATAC QC metrics: n_fragments, TSS_enrichment, FRiP
sc.pp.calculate_qc_metrics(adata_atac, qc_vars=[])
# Filter ATAC cells by log10(n_fragments) and TSS_enrichment thresholds
# e.g. min log10(n_fragments) > 3.0, min TSS_enrichment > 2.0
```

## Create harmonized features

_modules: feature-engineering, gene-activity, peak-matrix, harmonization_

```python
# Compute gene activity scores from ATAC peaks
# Using scanpy or custom approach
# For multiome data, peaks are mapped to gene bodies + promoter regions

# Example: create a gene activity matrix from peak-by-cell counts
# gene_activity = sum of peak counts overlapping each gene's body + 2kb upstream

# Store in adata.obsm or as a separate layer
# adata.obsm['gene_activity'] = gene_activity_matrix

# Ensure RNA and ATAC gene indices are aligned
# common_genes = intersect(adata_rna.var_names, gene_activity.columns)
```

## Integrate modalities

_modules: integration, multimodal, latent-space, multiVI, wnn_

```python
# Option 1: scvi-tools MultiVI (paired multiome)
import scvi

# Setup anndata with both modalities
scvi.model.MULTIVI.setup_anndata(
    adata,
    batch_key='batch' if 'batch' in adata.obs else None,
    rna_layer=None,
    protein_expression_obsm_key='gene_activity'
)
model = scvi.model.MULTIVI(adata)
model.train(max_epochs=200, early_stopping=True)

# Extract joint latent representation
latent_representation = model.get_latent_representation()
adata.obsm['X_multivi'] = latent_representation

# Option 2: Weighted Nearest Neighbor (WNN) with Seurat/scanpy
# sc.pp.neighbors(adata_rna)
# sc.pp.neighbors(adata_atac)
# Combine via weighted nearest neighbor approach
```

## Interpret regulatory signals

_modules: regulatory, motif, peak-to-gene, linkage, gene-activity_

```python
# Motif enrichment in cluster-specific peaks
# Use gimmemotifs, HOMER, or pycisTopic

# Peak-to-gene linkage
# For each peak, correlate accessibility with expression of nearby genes
# Store significant links (e.g. |correlation| > 0.3, FDR < 0.05)

# Gene activity vs expression correlation
# sc.pp.correlation(adata, groupby='cluster')

# Export motif-by-peak and peak-by-gene matrices for downstream analysis
```

## Export multimodal state summaries

_modules: export, serialization, visualization, umap_

```python
# Save integrated anndata object
adata.write('results/multiome_integrated.h5ad')

# Export QC summaries
adata_rna.obs[['n_genes_by_counts', 'total_counts', 'pct_counts_mt']].to_csv('qc/rna_qc_metrics.csv')
adata_atac.obs[['n_fragments', 'TSS_enrichment', 'FRiP']].to_csv('qc/atac_qc_metrics.csv')

# Export regulatory tables
# motif_enrichment_results.to_csv('results/motif_enrichment.csv')
# peak_gene_links.to_csv('results/peak_gene_links.csv')

# Generate UMAP plots
sc.pp.neighbors(adata, use_rep='X_multivi')
sc.tl.umap(adata)
sc.pl.umap(adata, color=['modality', 'cluster', 'n_genes_by_counts'], save='_multiome_integrated')
```
