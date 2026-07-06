---
name: sciagent-popv-cell-annotation
description: "Consensus cell type annotation: runs 10+ algorithms (KNN-Harmony/BBKNN/Scanorama/scVI, CellTypist, ONCLASS, Random Forest, SCANVI, SVM, XGBoost) on a labeled reference and transfers labels via majority voting. Outputs per-method labels, consensus, agreement score. Use when single-method annotation is insufficient or you need ensemble uncertainty for novel states."
domain: "single-cell"
primary_tool: ""
methods:
  - "celltypist"
  - "harmony"
  - "bbknn"
  - "scanorama"
  - "scvi"
  - "scanvi"
macro_tags:
  - "single-cell"
  - "annotation"
  - "integration"
micro_tags:
  - "celltypist"
  - "harmony"
  - "bbknn"
  - "scanorama"
  - "scvi"
  - "scanvi"
source: "sciagent/popv-cell-annotation"
status: active
---

# Sciagent Popv Cell Annotation
