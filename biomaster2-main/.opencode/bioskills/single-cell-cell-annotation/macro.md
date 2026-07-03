# Single Cell Cell Annotation

## Overview

Annotate single-cell RNA-seq clusters or individual cells with biological cell type labels by combining automated reference-based transfer (CellTypist) with marker-guided, confidence-aware curation. The default stance is to inspect markers first, run reference-based annotation, keep uncertainty explicit, and export both the raw predicted labels and a curated final label column.

Use this skill when clusters already exist and need biological labels, when the dataset has a relevant reference atlas or known marker panels, or when the user wants CellTypist or similar automated annotation. Do not use it to fix unstable or QC-driven clusters — fix preprocessing first.

Expected inputs: a processed h5ad object with clusters (e.g. leiden) and embeddings (UMAP), marker gene lists or known lineage markers, and an optional reference atlas or CellTypist model.

Expected outputs: results/annotated.h5ad, results/cell_labels.tsv (per-cell raw + final + confidence), results/cluster_annotation_summary.tsv, figures/umap_cell_types.pdf, and figures/marker_dotplot.pdf.

Key principles: never accept automated labels without checking marker expression; keep per-cell predictions and cluster-level curated labels separate; use Unknown, Uncertain, or Ambiguous when evidence is weak; and always document the reference model or atlas used.

## Pre-annotation marker inspection

Before running any automated annotation, inspect canonical lineage markers on UMAP, dotplots, or heatmaps to confirm that clusters support a plausible biological separation. If clusters are unstable or clearly QC-driven, fix preprocessing before annotation rather than locking in labels. This step establishes the biological ground truth that automated predictions will be checked against.

## Annotation level selection

Decide the granularity of labels based on reference quality and dataset noise. Use broad lineage labels when the reference is imperfect or atlas mismatch is severe; use fine-grained labels only when markers and reference agree; use cluster-level labels for noisy or sparse datasets where single-cell predictions are unstable. This decision drives which CellTypist model is selected and how aggressively fine categories are later collapsed.

## Reference-based annotation

Run CellTypist (or another compatible reference transfer method) against the chosen model with majority voting enabled so that noisy single-cell predictions are aggregated to the cluster level. Store the raw predicted label, the confidence score, and the model name so the original prediction is never lost and can always be recovered for review.

## Marker-guided curation

Review the top markers per cluster and compare them against the predicted labels. Rename or collapse fine categories that are not robust, and assign Unknown, Uncertain, or Ambiguous when evidence is weak. Apply confidence thresholds: a conf_score above 0.5 is usually comfortable for a provisional label, 0.2 to 0.5 should be manually reviewed against markers, and below 0.2 should usually remain Unknown unless markers are compelling. Every final label should have either marker support, reference support, or both.

## Export and visualization

Export both raw and curated labels alongside the annotated object, plus a cluster-level annotation summary that maps each cluster to its dominant final label. Generate a UMAP colored by final cell types and a marker dotplot to complete the figure set. Keep cell_type_raw, cell_type_confidence, and cell_type_final as separate columns so the original prediction is never overwritten.
