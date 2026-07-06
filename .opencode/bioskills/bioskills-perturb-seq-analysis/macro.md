# Bioskills Perturb Seq Analysis

## Overview

This skill analyzes single-cell pooled CRISPR perturbation screens — Perturb-seq, CROP-seq, Perturb-CITE-seq, ECCITE-seq, Perturb-multiome, and Replogle-style genome-wide CRISPRi — from raw counts to ranked perturbation effects.

Inputs: a scRNA-seq AnnData of raw counts carrying a per-cell sgRNA counts layer (cells × sgRNAs) and a perturbation metadata column that includes a non-targeting control (NTC) label. Outputs: per-cell sgRNA assignments, an escaper-filtered knockout (KO) cell set, per-gene-per-perturbation differential expression with calibrated FDR, and perturbations ranked by molecular effect with optional latent-factor decomposition.

Use this skill whenever a pooled CRISPR screen is read out by single-cell RNA-seq and you need to call perturbation effects. Primary tools: pertpy (Python, unified Mixscape + DE + factor framework), sceptre (R, the only DE method with calibrated FDR on low-MOI sparse scRNA-seq per Barry 2024 Genome Biol), and scanpy (preprocessing).

Key design decisions encoded in the workflow: target MOI ~0.3 so most infected cells carry a single sgRNA; assign sgRNAs at ≥10 reads per cell; remove doublets before sgRNA assignment to avoid spurious multiplets; filter escapers with Mixscape but skip it for weak-phenotype perturbations (logFC > -0.5) where it over-filters; use SCEPTRE rather than MAST/Wilcoxon for low-MOI DE because parametric tools over-call hits on zero-inflated data; require 500–1,000 cells per perturbation for stable DE (Replogle 2022). For multiomic Perturb-seq (RNA + ATAC), integrate modalities via muon/MuData and run joint differential analysis.

## Preprocessing & QC

Standard scRNA-seq preprocessing on the raw count matrix before any perturbation logic. Filter cells by detected gene count (≥500–1,000 genes/cell) and mitochondrial percentage (<15–20%). Normalize total counts to 1e4, apply log1p, and identify highly variable genes (top ~2,000). Run doublet detection (Scrublet or scDblFinder) independently of sgRNA assignment so that doublets can be removed before perturbation identity is assigned. The output is a normalized, QC'd AnnData with a doublet flag in .obs, ready for sgRNA assignment. This step is shared with conventional scRNA-seq preprocessing; the perturbation-specific work begins once cells are clean.

## sgRNA Assignment

Assign a single perturbation identity to every cell from the per-cell sgRNA counts matrix. The central technical challenge is ensuring each cell carries exactly one sgRNA: at MOI 0.3, ~26% of cells receive ≥1 sgRNA but ~4% receive ≥2, and multi-sgRNA cells must be filtered or treated as combinatorial perturbations. Threshold per-cell sgRNA reads at ≥10 (Pertpy/direct-capture convention): cells exceeding the threshold for exactly one sgRNA are assigned that perturbation; cells with multiple sgRNAs above threshold are flagged as 'multiplet' (filter or analyze combinatorially); cells with none are 'none'. Remove doublets (flagged in the previous step) BEFORE assignment so droplet doublets are not misread as genuine multi-perturbation cells. The goal is a single perturbation identity (or 'multiplet'/'none') per cell in .obs['sgrna_assignment']. Expected post-filter multiplet rate is <5% on 10X 3' chemistry; a higher rate signals over-loading and should be addressed by reducing cell input.

## Escaper Filtering (Mixscape)

Not all sgRNA-positive cells actually edit: 30–60% may receive the sgRNA but fail to undergo knockdown ('escapers'), which dilutes the perturbation signal. Mixscape (Papalexi 2021) addresses this. For each perturbed cell it computes a perturbation signature = the cell's expression minus the mean of its K nearest non-targeting-control (NTC) cells, isolating the perturbation effect from cell-state variation. Cells whose signature resembles the NTC distribution are classified as escapers (NP, non-perturbed); the rest as true knockouts (KO). Keep only KO cells plus NTC controls for downstream differential expression. Caveat: Mixscape assumes a detectable signal and can over-filter weak-phenotype perturbations (logFC > -0.5 collapses into the NTC null); for those, trust the raw assignment without filtering, and verify Cas9/CRISPRi expression first.

## Differential Expression

Fit per-gene differential expression conditioned on perturbation. For low-MOI single-cell data, use SCEPTRE (R, Katsevich lab): a negative-binomial GLM with conditional resampling (1,000+ permutations) that maintains calibrated FDR where MAST and Wilcoxon over-call hits because they assume Gaussian/simpler nulls on sparse, zero-inflated data (Barry 2024 benchmark). SCEPTRE is not wrapped by pertpy and must be invoked from R directly. For pseudobulk / high-throughput workflows, use pertpy with a PyDESeq2 backend on the KO cell set. Always include technical covariates (n_genes, n_umi, batch/channel) in the model; channel batch effects are a common source of inconsistent gene effects between replicates. Output: per-gene-per-perturbation p-value, log-fold-change, and FDR.

## Perturbation Ranking & Factor Analysis

Rank perturbations by their molecular effect (number of DE genes, magnitude of log-fold-change) and decompose complex perturbation responses into shared latent factors. FR-Perturb (Factor-Regularized Perturb-seq) decomposes per-cell perturbation effects into shared factors so that similar perturbations share loadings, revealing gene-program organization in the spirit of Replogle 2022's cluster-based analysis of genome-wide screens. For multiomic Perturb-seq (RNA + ATAC, e.g. Perturb-multiome), integrate the two modalities via muon/MuData and run joint differential analysis across modalities, using ArchR or Signac for the ATAC side and pertpy for the RNA side. This step turns the per-gene DE table into an interpretable, ranked view of perturbation biology.
