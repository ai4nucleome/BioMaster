---
name: "bioskills-normalization"
description: "Normalize raw RNA-seq count matrices: pre-filter genes, estimate between-sample size factors (RLE/TMM), compute TPM, variance-stabilize for visualization, correct GC/length bias, and normalize single-cell data."
domain: "single-cell"
primary_tool: "DESeq2"
methods: ["DESeq2","edgeR","limma-voom","scanpy","scran","EDASeq","cqn"]
macro_tags: ["normalization","rna-seq","size-factors","variance-stabilization","composition-bias"]
micro_tags: ["DESeq2","edgeR","scran","scanpy","EDASeq","cqn","TMM","RLE","VST","rlog","TPM","log-CPM"]
source: "bioskills-normalization"
status: "active"
enabled: true
---

# Bioskills Normalization
