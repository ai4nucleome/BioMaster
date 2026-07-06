---
name: "bioskills-multiome-pipeline"
description: "Complete 10X Multiome (joint scRNA + scATAC) analysis workflow using Seurat and Signac: load joint data, modality-specific QC and dimensionality reduction, WNN integration, clustering, markers, and gene-peak linkage."
domain: "single-cell"
primary_tool: "Seurat/Signac"
methods: ["Seurat","Signac","SCTransform","TF-IDF","LSI","WNN","FindClusters","LinkPeaks"]
macro_tags: ["multiome","scRNA","scATAC","integration","wnn","workflow"]
micro_tags: ["Seurat","Signac","SCTransform","TF-IDF","LSI","WNN","data-io","chromatin-assay","qc","pca","tss-enrichment","nucleosome-signal","integration","umap","clustering","visualization","marker-genes","differential-peaks","gene-peak-linkage","coverage-plot","cis-regulatory"]
source: "bioskills-multiome-pipeline"
status: "active"
enabled: true
---

# Bioskills Multiome Pipeline
