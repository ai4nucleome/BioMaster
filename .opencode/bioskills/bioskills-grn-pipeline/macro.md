# Bioskills Grn Pipeline

## Overview

This pipeline infers gene regulatory networks (GRNs) from processed single-cell data and simulates transcription factor perturbations. It accepts a QC'd, normalized, clustered AnnData object as input and supports two inference paths selected by data modality: RNA-only data follows the pySCENIC workflow (GRNBoost2 -> RcisTarget -> AUCell), while paired RNA + ATAC Multiome data follows the SCENIC+ workflow (cisTopic -> pycistarget -> eGRN construction). Either path produces a set of motif-supported regulons and a per-cell regulon activity matrix. The pipeline then feeds the inferred GRN into CellOracle to simulate TF knockouts and predict cell-state shifts.

Outputs include TF-target adjacencies, pruned regulons, an AUCell/eGRN activity matrix embedded in the AnnData (adata.obsm['X_aucell']), and per-cell perturbation scores. Use this skill when the goal is to discover master regulators of cell types or to predict the phenotypic consequence of perturbing a transcription factor. Inputs must already be preprocessed (QC, normalization, clustering); raw counts should be retained in adata.raw for GRN inference. Typical regulon yields are 50-500; datasets larger than ~50k cells should be subsampled for GRNBoost2 to avoid memory errors. Reference versions: anndata 0.10+, pandas 2.2+, scanpy 1.10+, scipy 1.12+; if installed versions differ, introspect the package API and adapt rather than retrying on ImportError/AttributeError/TypeError.

## Data Preparation & Path Selection

Load the processed AnnData and extract the raw count expression matrix that GRN inference requires. Load the species-appropriate transcription factor list from cisTarget resources and restrict it to genes present in the data. Select the inference path based on available modalities: RNA-only data uses pySCENIC (GRNBoost2 -> RcisTarget -> AUCell), while paired Multiome data uses SCENIC+ (cisTopic -> pycistarget -> eGRN). Verify package versions (anndata 0.10+, scanpy 1.10+, scipy 1.12+) before running, and introspect APIs if ImportErrors or TypeErrors arise.

## GRN Inference

Infer the initial transcription factor to target gene network. For the RNA-only path, GRNBoost2 computes gradient-boosted importance scores between every TF and every gene, producing a TF-target adjacency table. For the Multiome path, cisTopic performs LDA topic modeling on the ATAC fragment matrix to identify co-accessible region sets (topics); test a range of topic counts around twice the expected number of cell types and select the best model by log-likelihood. For large datasets (>50k cells), subsample before GRNBoost2 to avoid memory errors.

## Regulon Pruning & Motif Enrichment

Refine the initial network into high-confidence regulons using cis-regulatory motif evidence. For the RNA-only path, build TF modules from the adjacencies (top targets per TF, minimum 10 targets), then prune them with RcisTarget against cisTarget motif ranking databases (use both 500bp and 10kbp upstream databases); an NES threshold of 3.0 is standard, lowered to 2.5 for a more permissive run. For the Multiome path, binarize cisTopic topics to define accessible region sets and run pycistarget motif enrichment on them to map enhancers to TFs. The output is a set of motif-supported regulons (or enhancer-TF mappings) ready for activity scoring.

## Regulon Activity Scoring & GRN QC

Quantify per-cell regulon activity and validate the inferred GRN. For the RNA-only path, AUCell scores each cell against every regulon by ranking genes and computing AUC over the top fraction (auc_threshold 0.05); store the resulting matrix in adata.obsm['X_aucell']. For the Multiome path, construct the SCENICPLUS object from RNA, cisTopic, and motif enrichment results, then build enhancer-driven eGRNs. After scoring, run GRN QC gates: expect 50-500 regulons, confirm known lineage TFs are present (e.g., PAX6 in neurons, GATA1 in erythroid), and verify that AUCell scores separate known cell types via differential activity testing. If regulon counts are off, adjust the NES threshold or verify the TF list species.

## CellOracle Perturbation Simulation & QC

Use the inferred GRN to simulate transcription factor perturbations and predict cell-state shifts. Import the GRN (pySCENIC adjacencies or SCENIC+ eGRNs) into a CellOracle Oracle object along with the AnnData, then perform PCA and KNN imputation (k=30) to estimate TF-target expression relationships. Simulate a TF knockout by setting its expression to zero and propagating the signal (n_propagation=3), then estimate transition probabilities and calculate the embedding shift. Finally, validate the perturbation: perturbation scores should show directional shifts consistent with known biology, and if an expected affected cluster is known, confirm it ranks among the top shifted clusters. If no shift is observed, verify the perturbed TF is expressed in the target cells and that the GRN is sufficiently strong.
