# Plan Scrnaseq Tumor Heterogeneity

## Overview

Generate PLAN.yaml for tumor scRNA-seq heterogeneity and trajectory analysis.

## Legacy BioMaster Control Notes

# Plan: Tumor scRNA-seq Heterogeneity

## Purpose
Generate structured PLAN.yaml only. Read IO_CONTRACT.md and manifests/ before planning.

## Workflow steps
1. data preflight
2. cell and gene QC
3. doublet removal
4. batch correction
5. clustering and annotation
6. inferCNVpy malignancy
7. Palantir trajectory
8. cNMF modules
9. report generation

## PLAN.yaml rules
- declare step_id, objective, required_execute_skills or required_report_skills, and required_verify_skills
- use `required_report_skills` for `09_report_generation`; do not put `report-*` skills in `required_execute_skills`
- declare expected_outputs and acceptance_criteria
- never embed shell commands

## Boundaries
No execution, no environment install, no debugging.
