---
name: "epigenomics-atac-seq"
description: "Bulk ATAC-seq processing: assay QC gates, MACS3 fragment-aware peak calling, consensus peak matrices, differential accessibility, and motif/footprint follow-up."
domain: "epigenomics"
primary_tool: "MACS3"
methods: ["macs3","samtools","deeptools","pysam"]
macro_tags: []
micro_tags: ["macs3","samtools","deeptools","pysam","qc","tss-enrichment","fragment-size","frip","version-check","peak-calling","bampe","tn5-shift","nomodel","consensus-peaks","count-matrix","bedtools","featurecounts","differential-accessibility","deseq2","edger","statistics","motif","footprinting","chromvar","tobias","downstream"]
source: "bioclaw/atac-seq"
status: "active"
enabled: true
custom: false
---

# Epigenomics Atac Seq
