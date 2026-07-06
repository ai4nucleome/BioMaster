# Bioclaw Cell Annotation

## Overview

This workflow annotates single-cell RNA-seq clusters with cell type labels by combining reference-based automated annotation (via CellTypist) with marker gene review. It produces confidence-aware labels that distinguish high-confidence predictions from uncertain or unknown cells. The pipeline expects a processed AnnData object with existing clusters (e.g. Leiden) and embeddings (e.g. UMAP), and optionally a reference atlas or known marker panels. It outputs an annotated h5ad file, a per-cell labels TSV, a cluster-level annotation summary, and UMAP/dotplot figures. Use this skill when clusters already exist and need biological labels, when a relevant reference atlas or known marker panels are available, or when automated annotation via CellTypist is desired. The workflow enforces that raw automated predictions are never overwritten, that uncertainty is made explicit, and that every final label has either marker support, reference support, or both.

## Inspect Markers Before Automation

Check canonical lineage markers on UMAP, dotplots, or heatmaps before running automated annotation. For every major cluster, verify at least one positive marker and one exclusion marker when possible. If clusters do not support a plausible biological separation, do not lock in labels yet — revisit preprocessing instead.

## Choose Annotation Level

Decide between broad lineage labels, fine-grained labels, or cluster-level labels based on reference quality and marker support. Use broad labels when the atlas is from a different tissue or disease context, cluster markers support lineage but not subtype identity, or confidence scores are modest. Use fine labels only when cluster markers support the proposed subtype and the reference atlas is closely matched. Use cluster-level labels for noisy or sparse datasets. Document the chosen strategy in annotation_notes.

## Run Reference-Based Annotation

Use CellTypist to transfer labels from a pre-trained reference model to the query dataset with majority voting. Store the raw predicted label, confidence score, and model name for downstream curation. The majority voting mode smooths per-cell predictions using a kNN classifier on the reference model's cell-type probability space.

## Curate with Markers and Cluster Context

Review top markers per cluster and compare them against predicted labels. Rename or collapse labels if fine categories are not robust. Apply confidence thresholds: conf_score > 0.5 is comfortable for a provisional label; 0.2–0.5 should be manually reviewed against markers; < 0.2 should usually remain Unknown or Uncertain unless markers are compelling. Generate UMAP and dotplot figures colored by final labels and confidence.

## Export Labels

Export both raw predicted labels and curated final labels to tab-separated files. At minimum keep cell_type_raw, cell_type_confidence, cell_type_final, annotation_notes, and annotation_model columns. Also generate a cluster-level annotation summary that records the majority final label per cluster.
