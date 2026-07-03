# Bioskills Cell Annotation

## Overview

This workflow performs automated cell type annotation on a preprocessed single-cell dataset (AnnData in Python or Seurat in R). It expects a normalized, clustered object as input and assigns biologically meaningful cell type identities by mapping cells against reference atlases or trained classifiers. The pipeline supports multiple complementary tools — CellTypist (Python), SingleR, Azimuth, and scPred (R) — and writes per-cell labels together with confidence scores back into the object metadata. Downstream stages filter low-confidence calls, build a single consensus label across methods via majority voting, and validate assignments against canonical marker genes and inter-method agreement metrics (ARI, NMI, confusion matrices). Use this skill when you already have a processed dataset and want to assign cell type labels automatically rather than manually; it is not a preprocessing or clustering pipeline. Typical inputs: a normalized AnnData (.h5ad) or Seurat (.rds) object. Typical outputs: per-cell predicted labels, confidence scores, a consensus label, and validation plots/tables.

## Input Preparation

Load the preprocessed single-cell object (AnnData .h5ad in Python or Seurat .rds in R) that has already been normalized and clustered. This step establishes the input contract: a normalized expression matrix with cells as observations. Before running downstream tools, verify that installed package versions (pandas 2.2+, scanpy 1.10+, scikit-learn 1.4+ for Python; Seurat, SingleR, scPred for R) match the reference examples. If versions differ, introspect the actual API signatures (pip show / help() in Python; packageVersion() / ?fn in R) and adapt the examples rather than retrying on Import/Attribute/TypeErrors.

## Reference-Based Annotation

Assign cell types by mapping query cells onto pre-built reference atlases using off-the-shelf models. CellTypist applies a pre-trained logistic regression classifier with optional majority voting for cluster-level consensus and writes conf_score into AnnData. SingleR correlates each cell's expression against curated references (e.g. HumanPrimaryCellAtlas, Blueprint/ENCODE, MonacoImmune, ImmGen for mouse) using Wilcoxon-derived marker genes and prunes low-confidence calls; fine-grained labels and multi-reference combinations are also supported. Azimuth maps query cells onto a Seurat reference atlas (e.g. pbmcref, bonemarrowref, lungref) and transfers labels with a prediction score. Each tool records predictions and confidence metrics in the object metadata for downstream filtering.

## Custom Model Annotation

When pre-built references do not cover the biological context of the query, train a domain-specific classifier on a labeled reference dataset. CellTypist trains a logistic regression model (optionally with SGD and feature selection) on labeled reference data and saves it as a .pkl for reuse on query data. scPred extracts informative PCA features from a labeled Seurat reference, trains an SVM/random forest classifier, inspects training probabilities and performance, and predicts cell types on the query. This stage is optional and is used when off-the-shelf atlases are insufficient.

## Confidence Filtering

Filter or flag low-confidence predictions using each tool's native score so that downstream analysis can exclude or inspect uncertain cells. CellTypist uses conf_score (e.g. >0.5 high confidence, <0.3 flagged uncertain). SingleR provides pruned.labels in which low-quality calls are set to NA, which can be relabeled as Unknown. Azimuth uses predicted.celltype.l2.score (e.g. >0.7 retained, otherwise Low_confidence). The output is a per-cell confidence flag and a high-confidence subset.

## Consensus Annotation

Combine predictions from multiple annotation tools into a single consensus label per cell using majority voting. Cells where at least two methods agree receive the consensus label; cells where all methods disagree are flagged Ambiguous. Aggregating across tools reduces tool-specific bias and yields a more robust final annotation for downstream analyses such as cell-cell communication or trajectory inference.

## Validation & Comparison

Quantitatively assess annotation quality and biological plausibility. Compute the adjusted Rand index (ARI) and normalized mutual information (NMI) between label sets to measure agreement, and build a confusion matrix (crosstab) to inspect correspondences between methods or against a manual annotation. Finally, validate predicted types against canonical marker genes (e.g. CD3D/CD3E/CD4/CD8A for T cells, CD19/MS4A1/CD79A for B cells, CD14/LYZ/S100A8 for monocytes, NKG7/GNLY/NCAM1 for NK cells) using dot plots to confirm that expected markers are expressed in the predicted populations.
