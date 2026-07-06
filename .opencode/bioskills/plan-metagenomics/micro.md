# Plan Metagenomics

## Operational Notes

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
- declare step_id, objective, required_execute_skills or required_report_skills, and required_verify_skills
- use `required_report_skills` for final report-only steps; do not put `report-*` skills in `required_execute_skills`
- declare expected_outputs and acceptance_criteria
- never embed shell commands

## Boundaries
No execution, no environment install, no debugging.
