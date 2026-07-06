---
name: "bioskills-umi-processing"
description: "Deduplicate UMI-tagged sequencing reads: extract UMIs from FASTQ, align, collapse PCR duplicates, and count molecules per gene/cell using UMI-tools."
domain: "single-cell"
primary_tool: "umi_tools"
methods: ["umi_tools","star","samtools","fastp","pandas"]
macro_tags: ["umi","deduplication","workflow","counting","pcr-duplicates"]
micro_tags: ["umi_tools","extract","dedup","count","group","star","samtools","fastp","pandas"]
source: "bioskills-umi-processing"
status: "active"
enabled: true
---

# Bioskills Umi Processing
