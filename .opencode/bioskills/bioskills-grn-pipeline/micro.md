## Data Preparation & Path Selection

_modules: data-loading, path-selection, version-check_

```python
import scanpy as sc
import pandas as pd

# Load processed AnnData (QC'd, normalized, clustered)
adata = sc.read_h5ad('processed.h5ad')

# Extract raw count matrix (GRNBoost2 recommends raw counts)
expr_matrix = pd.DataFrame(
    adata.raw.X.toarray() if hasattr(adata.raw.X, 'toarray') else adata.raw.X,
    index=adata.obs_names, columns=adata.raw.var_names
)

# Load species-appropriate TF list from cisTarget resources
# Human: https://resources.aertslab.org/cistarget/tf_lists/
tf_names = pd.read_csv('allTFs_hg38.txt', header=None)[0].tolist()
tf_names = [tf for tf in tf_names if tf in expr_matrix.columns]

# Path selection:
#   RNA-only  -> pySCENIC  (GRNBoost2 -> RcisTarget -> AUCell)
#   Multiome  -> SCENIC+   (cisTopic -> pycistarget -> eGRN)
```

## GRN Inference

_modules: grnboost2, cistopic, grn-inference_

```python
# --- Path A: RNA-only -- GRNBoost2 ---
from arboreto.algo import grnboost2

adjacencies = grnboost2(expr_matrix, tf_names=tf_names, seed=42, verbose=True)
adjacencies.to_csv('adjacencies.tsv', sep='\t', index=False, header=False)

# --- Path B: Multiome -- cisTopic topic modeling ---
from pycisTopic.cistopic_class import create_cistopic_object
from pycisTopic.lda_models import run_cgs_models, evaluate_models

cistopic_obj = create_cistopic_object(
    fragment_matrix=adata_atac.X,
    cell_names=adata_atac.obs_names.tolist(),
    region_names=adata_atac.var_names.tolist()
)
# Test topic counts around 2x expected cell types
models = run_cgs_models(
    cistopic_obj,
    n_topics=[10, 20, 30, 40, 50],
    n_cpu=8, n_iter=300, random_state=42
)
model = evaluate_models(models, select_model=True)
cistopic_obj.add_LDA_model(model)
```

## Regulon Pruning & Motif Enrichment

_modules: rcistarget, pycistarget, motif-enrichment, regulon-pruning_

```python
# --- Path A: RNA-only -- RcisTarget pruning ---
from pyscenic.prune import prune2df, df2regulons
from ctxcore.rnkdb import FeatherRankingDatabase
from ctxcore.genesig import GeneSignature

# cisTarget databases (~10 GB each, download once)
dbs = [FeatherRankingDatabase(db) for db in [
    'hg38_500bp_up_100bp_down.genes_vs_motifs.rankings.feather',
    'hg38_10kbp_up_10kbp_down.genes_vs_motifs.rankings.feather'
]]
motif_annotations = 'motifs-v10nr_clust-nr.hgnc-m0.001-o0.0.tbl'

# Build modules: top targets per TF, require >= 10 targets
modules = [GeneSignature(name=tf, gene2weight=dict(zip(grp['target'], grp['importance'])))
           for tf, grp in adjacencies.groupby('TF') if len(grp) >= 10]

# Prune by motif enrichment (NES 3.0 standard, 2.5 permissive)
df_motifs = prune2df(dbs, modules, motif_annotations, num_workers=8)
regulons = df2regulons(df_motifs)
print(f'Discovered {len(regulons)} regulons')

# --- Path B: Multiome -- pycistarget enhancer-TF mapping ---
from pycistarget.utils import region_names_to_coordinates
from pycistarget.motif_enrichment_cistarget import run_cistarget
from pycisTopic.topic_binarization import binarize_topics

region_bin = binarize_topics(cistopic_obj, method='otsu')
region_sets = {topic: region_bin[topic] for topic in region_bin}

cistarget_results = run_cistarget(
    region_sets=region_sets,
    species='homo_sapiens',
    auc_threshold=0.005,
    nes_threshold=3.0,
    rank_threshold=0.05,
    n_cpu=8
)
```

## Regulon Activity Scoring & GRN QC

_modules: aucell, scenicplus, egrn, qc, validation_

```python
# --- Path A: RNA-only -- AUCell scoring ---
from pyscenic.aucell import aucell

auc_matrix = aucell(expr_matrix, regulons, num_workers=8)
adata.obsm['X_aucell'] = auc_matrix.loc[adata.obs_names].values
adata.uns['regulon_names'] = [r.name for r in regulons]

# --- Path B: Multiome -- SCENIC+ eGRN construction ---
from scenicplus.scenicplus_class import create_SCENICPLUS_object
from scenicplus.grn_builder.gsea_approach import build_grn

scplus_obj = create_SCENICPLUS_object(
    adata_rna=adata_rna,
    cistopic_obj=cistopic_obj,
    menr=cistarget_results
)
build_grn(
    scplus_obj,
    min_target_genes=10,
    adj_pval_thr=0.1,
    min_regions_per_gene=0
)
print(f'eGRNs: {len(scplus_obj.uns["eRegulon_AUC"].columns)} enhancer-driven regulons')

# --- GRN QC gates ---
import scipy.stats as stats

def validate_grn(regulons, auc_matrix, adata, cell_type_key='cell_type'):
    n_regulons = len(regulons)
    regulon_names = [r.name for r in regulons]
    # Gate 1: regulon count (50-500 typical)
    if n_regulons < 50:
        print(f'WARNING: Only {n_regulons} regulons. Lower NES threshold or check TF list.')
    elif n_regulons > 500:
        print(f'WARNING: {n_regulons} regulons. Consider stricter pruning (NES 3.5).')
    else:
        print(f'OK: {n_regulons} regulons in expected range (50-500)')
    # Gate 2: known lineage TFs present
    known_tfs = ['PAX6', 'SOX2', 'GATA1', 'SPI1', 'FOXP3', 'TBX21', 'EBF1']
    found = [tf for tf in known_tfs if tf in regulon_names]
    print(f'Known lineage TFs found: {found}')
    # Gate 3: AUCell separates cell types
    cell_types = adata.obs[cell_type_key].unique()
    if len(cell_types) >= 2:
        ct1_idx = adata.obs[cell_type_key] == cell_types[0]
        ct2_idx = adata.obs[cell_type_key] == cell_types[1]
        n_differential = 0
        for i, rname in enumerate(regulon_names[:min(50, len(regulon_names))]):
            stat, pval = stats.mannwhitneyu(
                auc_matrix.values[ct1_idx, i], auc_matrix.values[ct2_idx, i]
            )
            if pval < 0.01:
                n_differential += 1
        print(f'Differentially active regulons between top 2 types: {n_differential}/50')
    return n_regulons

validate_grn(regulons, auc_matrix, adata)
```

## CellOracle Perturbation Simulation & QC

_modules: celloracle, perturbation-simulation, knn-imputation, qc_

```python
import celloracle as co

oracle = co.Oracle()
oracle.import_anndata_as_raw_count(
    adata=adata,
    cluster_column_name='cell_type',
    embedding_name='X_umap'
)

# Import GRN (from pySCENIC adjacencies or SCENIC+ eGRNs)
links = co.utility.load_links(adjacencies)
oracle.addTFinfo_dictionary(links)

oracle.perform_PCA()
oracle.knn_imputation(k=30)

# Simulate TF knockout (e.g., MYC -> 0)
oracle.simulate_shift(perturb_condition={'MYC': 0.0}, n_propagation=3)
oracle.estimate_transition_prob(n_neighbors=200, knn_random=True, sampled_fraction=1)
oracle.calculate_embedding_shift(sigma_corr=0.05)
gradient = oracle.gradient_fitting(n_jobs=8)

# --- Perturbation QC ---
def validate_perturbation(oracle, perturbed_tf, expected_affected_cluster=None):
    ps = oracle.perturbation_scores
    mean_shift = ps.groupby(oracle.adata.obs['cell_type']).mean()
    print(f'Mean perturbation scores by cell type after {perturbed_tf} KO:')
    print(mean_shift.sort_values(ascending=False))
    if expected_affected_cluster:
        if expected_affected_cluster in mean_shift.index[:3]:
            print(f'OK: {expected_affected_cluster} among top affected clusters')
        else:
            print(f'WARNING: {expected_affected_cluster} not among top affected')
    return mean_shift

validate_perturbation(oracle, 'MYC')
```
