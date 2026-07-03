# Bioskills Atlas Mapping

## Overview

This workflow maps query scRNA-seq data onto a pre-trained reference atlas using scArches transfer learning (scVI / scANVI). It performs "architectural surgery" — surgical fine-tuning that updates only query-specific parameters (weight_decay=0.0) — to obtain a shared latent embedding and transfer cell type labels from the reference to the query, without retraining the reference model.

**Inputs:** a pre-trained reference scVI/scANVI model (or a labeled reference AnnData to build one) and a query AnnData with raw counts. The query must be subset to the reference gene set before mapping.

**Outputs:** query AnnData annotated with a shared latent representation (X_scVI / X_scANVI), predicted cell type labels, prediction confidence scores, and a joint UMAP of reference + query cells for integration assessment.

**When to use:** when you have query cells and want to assign them cell types defined in an established reference atlas (e.g. Human Lung Cell Atlas, Tabula Sapiens, Mouse Cell Atlas) rather than clustering and annotating from scratch. Prefer this over de-novo annotation when a high-quality matched reference exists.

**Reference compatibility:** examples target anndata 0.10+, scanpy 1.10+, scvi-tools 1.1+. If code throws ImportError/AttributeError/TypeError, introspect the installed package (`pip show <package>`, `help(module.function)`) and adapt to the actual API rather than retrying.

**Pre-trained reference atlases:** Human Lung Cell Atlas (scANVI, cellxgene.cziscience.com), Tabula Sapiens (scVI, tabula-sapiens-portal.ds.czbiohub.org), Mouse Cell Atlas (scVI, bis.zju.edu.cn/MCA).

## Reference & Query Preparation

Load the pre-trained reference model together with its reference AnnData, then prepare the query AnnData by subsetting to the reference gene set and aligning layer/batch conventions. This guarantees the query is compatible with the reference model before surgical fine-tuning. Verify that installed versions of anndata / scanpy / scvi-tools match the reference; if APIs differ, introspect the installed package and adapt the calls rather than retrying.

## scVI Surgical Mapping

Load the query into the reference scVI model via surgical fine-tuning, training only query-specific parameters with weight_decay=0.0 so the reference weights are preserved. Extract the shared latent representation (X_scVI) for downstream analysis. Surgical training typically needs fewer epochs (100-200) than a full retrain (200-400); enable early stopping to prevent overfitting.

## scANVI Label Transfer

Build a semi-supervised scANVI model from the labeled reference by converting a trained scVI model with cell type labels, then map the query via surgical fine-tuning and predict cell type labels. This transfers the reference's cell type ontology onto query cells. If a pre-trained scANVI reference already exists, skip the reference training block and load it directly.

## Prediction Confidence

Extract soft prediction probabilities from the scANVI model to assess the reliability of transferred labels. Flag cells whose maximum confidence falls below a threshold (e.g. 0.5) as potential novel cell types or poor mappings that warrant manual review.

## Joint Embedding Visualization

Concatenate reference and query datasets, compute neighbors and UMAP from the shared latent representation, and color by dataset and cell type to assess integration quality and the consistency of transferred labels across the joint embedding.
