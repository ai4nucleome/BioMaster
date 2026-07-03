## Guide Assignment & Annotation

_modules: guide-assignment, annotation, crispr_

```python
import scanpy as sc
import pandas as pd

# Load expression matrix
adata = sc.read_h5ad('perturb_seq.h5ad')

# Parse Cell Ranger CRISPR Guide Capture output
guides = pd.read_csv('crispr_analysis/protospacer_calls_per_cell.csv')
guides['cell_barcode'] = guides['cell_barcode'].str.replace('-1', '')
guides = guides[guides['num_features'] == 1]  # Single guide per cell

# Merge guide metadata into AnnData
adata.obs = adata.obs.merge(
    guides[['cell_barcode', 'feature_call', 'target_gene']],
    left_index=True,
    right_on='cell_barcode',
    how='left'
)

# Map guide identity and target gene (if not already from feature_call)
adata.obs['guide_id'] = guides.set_index('cell_barcode')['feature_call'].reindex(adata.obs_names)
adata.obs['target_gene'] = guides.set_index('cell_barcode')['target_gene'].reindex(adata.obs_names)

# Mark non-targeting controls
adata.obs['is_control'] = adata.obs['target_gene'] == 'non-targeting'
```

## Guide Quality Control

_modules: qc, guide-filtering, moi_

```python
import scanpy as sc

# Check guide representation
guide_counts = adata.obs['target_gene'].value_counts()
print(f'Guides per target: {guide_counts.mean():.1f}')
print(f'Cells per guide: {adata.obs.groupby("guide_id").size().mean():.1f}')

# Filter low-representation guides (standard: keep guides with >= 100 cells)
min_cells = 100
valid_guides = guide_counts[guide_counts >= min_cells].index
adata = adata[adata.obs['target_gene'].isin(valid_guides)]

# Check for guide bias
sc.pl.violin(adata, keys='n_genes_by_counts', groupby='target_gene', rotation=90)

# Handle multi-guide cells (MOI > 1)
multi_guide = adata.obs[adata.obs['num_guides'] > 1]
print(f'Multi-guide cells: {len(multi_guide) / len(adata):.1%}')

# Option 1: Remove multi-guide cells
adata = adata[adata.obs['num_guides'] == 1]
# Option 2: Keep only cells where guides target same gene
# Option 3: Analyze combinatorial effects
```

QC metric thresholds:
| Metric | Good | Acceptable | Poor |
|--------|------|------------|------|
| Cells per guide | >200 | 100-200 | <100 |
| Guide detection rate | >90% | 80-90% | <80% |
| Non-targeting cells | 5-15% | 15-25% | >25% |
| Mixscape KO fraction | >50% | 30-50% | <30% |

## Perturbation Differential Expression & Signatures

_modules: differential-expression, pseudobulk, perturbation-signature_

```python
import pertpy as pt
from pertpy.tools import PseudobulkDE

# Pseudobulk differential expression per perturbation vs control
pb = PseudobulkDE(adata)
pb.fit(
    groupby='target_gene',
    control='non-targeting',
    method='deseq2',  # or 'edger', 'wilcoxon'
    min_cells=50,
    n_threads=8
)
results = pb.results()

# Filter significant genes
sig_results = results[results['pval_adj'] < 0.05]

# Get DE for a specific perturbation
tp53_de = pb.results('TP53')
sig_genes = tp53_de[tp53_de['padj'] < 0.05].sort_values('log2FoldChange')

# Perturbation signatures (effect sizes)
ps = pt.tl.PerturbationSignature(adata)
ps.compute(groupby='target_gene', control='non-targeting')
signatures = ps.get_signature_matrix()
```

## Perturbation Embedding & Clustering

_modules: embedding, clustering, phenotype_

```python
import pertpy as pt

# Compute perturbation-level embeddings
pt.tl.perturbation_embedding(adata, groupby='target_gene', method='mean')

# Cluster perturbations by phenotype
pt.tl.cluster_perturbations(adata, resolution=0.5)

# Find functionally related perturbations
pt.pl.perturbation_heatmap(adata, groupby='perturbation_cluster')
```

## Mixscape Classification (Seurat v5)

_modules: mixscape, classification, seurat_

```r
library(Seurat)
library(SeuratObject)

# Load Perturb-seq data and add perturbation metadata
seurat <- Read10X('filtered_feature_bc_matrix/')
seurat <- CreateSeuratObject(seurat)
seurat <- AddMetaData(seurat, metadata = perturbation_calls)

# Standard preprocessing
seurat <- NormalizeData(seurat)
seurat <- FindVariableFeatures(seurat)
seurat <- ScaleData(seurat)
seurat <- RunPCA(seurat)
seurat <- RunUMAP(seurat, dims = 1:30)

# Compute per-cell perturbation signatures vs non-targeting controls
seurat <- CalcPerturbSig(
    seurat,
    assay = 'RNA',
    slot = 'data',
    new.assay.name = 'PRTB',
    gd.class = 'gene',
    nt.cell.class = 'NT',
    num.neighbors = 20,
    reduction = 'pca',
    ndims = 15
)

# Run Mixscape mixture model classification
seurat <- RunMixscape(
    seurat,
    assay = 'PRTB',
    slot = 'scale.data',
    labels = 'gene',
    nt.class.name = 'NT',
    min.de.genes = 5,
    iter.num = 10,
    de.assay = 'RNA',
    prtb.type = 'KO'
)

# View classification results
table(seurat$mixscape_class.global)
```

## Visualization & Pathway Enrichment

_modules: visualization, lda, pathway-enrichment_

```r
# Mixscape visualization (Seurat)
DimPlot(seurat, reduction = 'umap', group.by = 'mixscape_class', label = TRUE)
VlnPlot(seurat, features = 'mixscape_class_p_ko', group.by = 'gene')
MixscapeHeatmap(seurat, ident.1 = 'TP53', ident.2 = 'NT', balanced = TRUE)

# LDA projection separating perturbed from control cells
seurat <- MixscapeLDA(seurat, labels = 'gene', nt.class.name = 'NT')
LDAPlot(seurat)
```

```python
# Pathway enrichment with decoupler (Python)
import decoupler as dc

# Get DE genes per perturbation from PseudobulkDE
de_results = pb.results()

# Run over-representation analysis against MSigDB
dc.run_ora(
    mat=de_results,
    net=dc.get_resource('MSigDB'),
    source='geneset',
    target='gene'
)

# Visualize top pathways per perturbation
dc.plot_barplot(de_results, 'TP53', top_n=20)
```
