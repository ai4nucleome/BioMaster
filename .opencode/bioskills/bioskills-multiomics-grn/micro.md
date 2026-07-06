## Input Preparation

_modules: data-loading, qc, scanpy_

```python
import scanpy as sc
import pycisTopic
from pycisTopic.cistopic_class import create_cistopic_object_from_fragments

# Load RNA from CellRanger ARC output
adata_rna = sc.read_10x_h5('filtered_feature_bc_matrix.h5', gex_only=True)
adata_rna.var_names_make_unique()
sc.pp.filter_cells(adata_rna, min_genes=200)
sc.pp.filter_genes(adata_rna, min_cells=3)

# Load ATAC fragments
fragments_file = 'atac_fragments.tsv.gz'
```

## Peak Calling & Topic Modeling

_modules: peak-calling, macs3, topic-modeling, cistopic, lda_

```python
import subprocess
from pycisTopic.cistopic_class import create_cistopic_object_from_fragments
from pycisTopic.lda_models import run_cgs_models, evaluate_models

# Call peaks from fragments file for region universe
subprocess.run([
    'macs3', 'callpeak',
    '-t', 'atac_fragments.tsv.gz',
    '-f', 'BEDPE',
    '--nomodel', '--shift', '-75', '--extsize', '150',
    '-g', 'hs',
    '--keep-dup', 'all',
    '-n', 'multiome_peaks',
    '--outdir', 'macs3_output'
], check=True)

# Create binary accessibility matrix from fragments
path_to_regions = 'macs3_output/multiome_peaks_peaks.narrowPeak'
cistopic_obj = create_cistopic_object_from_fragments(
    path_to_fragments=fragments_file,
    path_to_regions=path_to_regions,
    path_to_blacklist='hg38-blacklist.v2.bed',
    n_cpu=8
)

# Run LDA topic modeling; test multiple topic numbers, select by model metrics
models = run_cgs_models(cistopic_obj, n_topics=[10, 20, 30, 40, 50],
                        n_cpu=8, n_iter=300, random_state=42)

# Select best model (highest coherence, lowest perplexity)
model = evaluate_models(models, return_model=True)
cistopic_obj.add_LDA_model(model)
```

## SCENIC+ eRegulon Inference

_modules: scenicplus, motif-enrichment, region-to-gene, tf-to-region, eregulon_

```python
import scenicplus
from scenicplus.scenicplus_class import SCENICPLUS
from scenicplus.wrappers.run_scenicplus import run_scenicplus

# Prepare SCENIC+ object
scplus_obj = SCENICPLUS(
    adata_rna,           # scRNA-seq AnnData
    cistopic_obj,        # cisTopic object with topics
    menr=None            # will be computed
)

# Run complete SCENIC+ pipeline:
# motif enrichment, region-to-gene linking, eRegulon assembly
run_scenicplus(
    scplus_obj,
    variable=['GeneExpressionLevel'],
    species='hsapiens',
    assembly='hg38',
    tf_file='allTFs_hg38.txt',
    save_path='scenicplus_output/',
    biomart_host='http://www.ensembl.org',
    upstream=[1000, 150000],    # search space upstream of TSS
    downstream=[1000, 150000],  # search space downstream of TSS
    calculate_TF_eGRN_correlation=True,
    calculate_DEGs_DARs=True,
    export_to_loom_file=True,
    export_to_UCSC_file=True,
    n_cpu=8
)
```

## eRegulon Interpretation & Scoring

_modules: eregulon, activity-scoring, aucell, interpretation_

```python
import pandas as pd
from scenicplus.eregulon_enrichment import score_eRegulons

# eRegulons link TFs -> enhancers -> target genes
eregulons = scplus_obj.uns['eRegulon_metadata']
print(f'Found {eregulons["Region_signature_name"].nunique()} eRegulons')

# Summarize eRegulons per TF
ereg_summary = eregulons.groupby('TF').agg(
    n_regions=('Region', 'nunique'),
    n_genes=('Gene', 'nunique')
).sort_values('n_genes', ascending=False)
print(ereg_summary.head(20))

# Activating vs repressive eRegulons
# (+) suffix = activating (TF expression positively correlated with targets)
# (-) suffix = repressive (TF expression negatively correlated with targets)
activating = eregulons[eregulons['Region_signature_name'].str.contains(r'\(\+\)')]
repressive = eregulons[eregulons['Region_signature_name'].str.contains(r'\(-\)')]
print(f'Activating: {activating["TF"].nunique()}, Repressive: {repressive["TF"].nunique()}')

# Score eRegulon activity per cell (like AUCell but for eRegulons)
score_eRegulons(scplus_obj, ranking_key='eRegulon_AUC', enrichment_type='region')
score_eRegulons(scplus_obj, ranking_key='eRegulon_AUC_gene', enrichment_type='gene')

# eRegulon AUC matrix
ereg_auc = scplus_obj.uns['eRegulon_AUC']['Gene_based'].copy()
```

## Visualization

_modules: visualization, dotplot, heatmap, network-plot_

```python
import matplotlib.pyplot as plt
from scenicplus.plotting.dotplot import heatmap_dotplot
from scenicplus.plotting.grn_plot import plot_eRegulon

# eRegulon activity heatmap by cell type
heatmap_dotplot(
    scplus_obj,
    size_matrix=scplus_obj.uns['eRegulon_AUC']['Gene_based'],
    color_matrix=scplus_obj.uns['eRegulon_AUC']['Region_based'],
    group_variable='cell_type',
    save='eregulon_dotplot.pdf'
)

# Network visualization of top eRegulon
plot_eRegulon(scplus_obj, tf_name='PAX5', save='pax5_eregulon.pdf')
```

## FigR Alternative (R)

_modules: figr, dorc, peak-gene-correlation, r, alternative_

```r
library(FigR)
library(Seurat)
library(Signac)

# Load Seurat object with RNA and ATAC assays (from Signac)
seurat_obj <- readRDS('multiome_seurat.rds')

# Step 1: compute peak-gene correlations
peak_gene_cors <- runGenePeakcorr(
    ATAC.se = seurat_obj@assays$ATAC,
    RNAmat = seurat_obj@assays$RNA@data,
    genome = 'hg38',
    nCores = 8,
    p.cut = 0.05  # significance threshold for peak-gene links
)

# Step 2: infer TF-gene regulation scores (DORC-based)
fig_results <- runFigR(
    ATAC.se = seurat_obj@assays$ATAC,
    dorcTab = peak_gene_cors,
    genome = 'hg38',
    dorcMat = getDORCScores(seurat_obj@assays$ATAC, peak_gene_cors),
    rnaMat = seurat_obj@assays$RNA@data,
    nCores = 8
)

# Top regulatory TF-gene links
top_links <- fig_results[order(abs(fig_results$Score), decreasing = TRUE), ]
head(top_links, 20)
```
