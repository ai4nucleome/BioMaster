---
name: plan-metagenomics
description: Generate PLAN.yaml for detailed metagenomic analysis using R phyloseq-based functions.
compatibility: opencode
metadata:
  layer: plan
  domain: bioinformatics
  discipline: metagenomics
  analysis: metagenomics
  status: active
---

# Plan: Detailed Metagenomic Analysis

## Purpose
Generate structured PLAN.yaml only. Read IO_CONTRACT.md and manifests/ before planning.

## Workflow steps
1. load main function and packages (00.func_v2.R)
2. create_phyloseq — build phyloseq-class object from OTU/taxonomy/metadata
3. plot_detection_prevalence — core microbiota detection and prevalence filtering
4. plot_comp — taxonomic composition bar plots
5. cal_alpha — alpha diversity indices and group comparison
6. cal_pca — principal components analysis
7. cal_dist — dissimilarity matrix, ANOSIM, PERMANOVA
8. cal_ordination — constrained/unconstrained ordination (DCA, CCA, RDA, NMDS, PCoA)
9. cal_marker — differential abundance marker discovery (LEfSe, DESeq2, edgeR, ANCOM-BC, etc.)

## PLAN.yaml rules
- declare step_id, objective, required_execute_skills, required_verify_skills
- declare expected_outputs and acceptance_criteria
- never embed shell commands

## Boundaries
No execution, no environment install, no debugging.
