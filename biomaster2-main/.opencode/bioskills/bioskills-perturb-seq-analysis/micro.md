## Preprocessing & QC

_modules: qc, normalization, doublet-detection, hvg_

import scanpy as sc
import pertpy as pt

# adata: raw-counts AnnData with .layers['sgrna_counts'] (cells x sgRNAs)
# --- QC ---
sc.pp.filter_cells(adata, min_genes=500)            # >=500-1000 genes/cell
adata.var['mt'] = adata.var_names.str.startswith('MT-')
sc.pp.calculate_qc_metrics(adata, qc_vars=['mt'], percent_top=None, log1p=False, inplace=True)
adata = adata[adata.obs['pct_counts_mt'] < 20].copy()  # <15-20% mt%

# --- Normalize ---
sc.pp.normalize_total(adata, target_sum=1e4)
sc.pp.log1p(adata)
sc.pp.highly_variable_genes(adata, n_top_genes=2000)

# --- Doublet detection (independent of sgRNA assignment) ---
sc.external.scrublet(adata)   # writes .obs['predicted_doublet'] / doublet_score
# Alternative: scDblFinder via pertpy/scanpy.tl

## sgRNA Assignment

_modules: sgrna-assignment, multiplet-detection, moi_

import numpy as np

def assign_sgrna(adata, sgrna_counts_layer='sgrna_counts', threshold=10):
    '''Per-cell sgRNA assignment. Returns single assignment or 'multiplet'/'none'.'''
    counts = adata.layers[sgrna_counts_layer]          # cells x sgRNAs
    above_thresh = counts >= threshold
    n_sgrna_per_cell = above_thresh.sum(axis=1)
    assignments = np.where(
        n_sgrna_per_cell == 0, 'none',
        np.where(n_sgrna_per_cell == 1,
                  [adata.var_names[i] for i in counts.argmax(axis=1)],
                  'multiplet'))
    adata.obs['sgrna_assignment'] = assignments
    return adata

# Remove doublets BEFORE assignment to avoid spurious multiplets
adata = adata[~adata.obs['predicted_doublet']].copy()
assign_sgrna(adata, threshold=10)
# Sanity check: multiplet rate should be <5% on 10X 3' chemistry

## Escaper Filtering (Mixscape)

_modules: mixscape, escaper-filtering, perturbation-signature_

import pertpy as pt

# adata: scRNA-seq AnnData with .obs['sgrna_assignment'] ('NTC' = non-targeting control)
mixscape = pt.tl.Mixscape()

# 1) Perturbation signature = cell expr - mean(K nearest NTC cells)
mixscape.perturbation_signature(
    adata=adata,
    pert_key='sgrna_assignment',   # .obs column with sgRNA target per cell
    control='NTC',                 # name of non-targeting control
    n_neighbors=20,                # K neighbors for KNN-NTC subtraction
)  # writes .layers['X_pert']

# 2) Classify perturbed cells as KO (true perturbation) or NP (escaper)
mixscape.mixscape(
    adata=adata,
    pert_key='sgrna_assignment',   # pert_key (not 'labels') in modern pertpy
    control='NTC',
    new_class_name='mixscape_class',  # .obs column to write
)  # defaults to layer='X_pert'

# 3) Keep KO cells + NTC controls for downstream DE
adata_ko = adata[adata.obs['mixscape_class'].isin(['KO', 'NTC'])].copy()
print(f'KO cells: {adata_ko.n_obs} ({adata_ko.n_obs/adata.n_obs:.1%} of perturbed)')
# Note: skip Mixscape for weak-phenotype perturbations (logFC > -0.5)

## Differential Expression

_modules: differential-expression, sceptre, nb-glm, permutation-test, pydeseq2_

# --- Option A: SCEPTRE (R) for calibrated low-MOI single-cell DE ---
# library(sceptre)
# results <- run_sceptre_low_moi(
#     expression_matrix     = gene_expr,        # genes x cells
#     grouping_var          = pert_indicator,   # 0 = NTC, 1 = perturbed
#     technical_factors     = covariates_df,    # n_genes, n_umi, batch
#     response_grouping_var = 'gene_id',
#     n_permutations        = 1000
# )
# Output: per-gene-per-pert p-value, logFC, FDR (calibrated; Barry 2024)

# --- Option B: pertpy pseudobulk DE (PyDESeq2 backend) ---
import pertpy as pt

de = pt.tl.PyDESeq2(adata_ko, design='~perturbation')
de.fit()
results_df = de.test_contrasts(contrast=('perturbation', 'GENE_X', 'NTC'))
# Add channel/batch as covariate to absorb cross-replicate batch effects.

## Perturbation Ranking & Factor Analysis

_modules: perturbation-ranking, factor-analysis, fr-perturb, multiome_

import pertpy as pt

# FR-Perturb: decompose perturbation effects into shared latent factors
fr = pt.tl.FRPerturb()
factors = fr.fit(adata, pert_key='perturbation', n_factors=20)
# Output: per-perturbation factor loadings; similar perturbations share factors

# Rank perturbations by effect size using the DE table from the previous step
# (aggregate n_DE_genes and mean |logFC| per perturbation; sort descending)

# --- Multiomic Perturb-seq (RNA + ATAC) ---
import muon as mu
mdata = mu.MuData({'rna': adata_rna, 'atac': adata_atac})
# Joint differential analysis across modalities:
#   ATAC side -> ArchR or Signac
#   RNA  side -> pertpy
