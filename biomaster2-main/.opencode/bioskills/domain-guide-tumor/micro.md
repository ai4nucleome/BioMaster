# Domain Guide Tumor

## Operational Notes

# Tumor Domain Guide

## Purpose
Define tumor research conversation entry, operating modes, and supported pipeline families.

## When to use
Load during intake before collecting detailed sample metadata.

## First interaction rule
Ask only for operating mode on the first turn:
1. test mode — run built-in demo data end-to-end
2. formal analysis — user supplies real data paths and sample metadata
3. custom request — user describes the task in free text

Do not mix mode selection with data path, cancer type, or sample questions.

## Outputs
```
domain: tumor
mode: test | formal | custom
candidate_pipelines:
  - tumor_scrnaseq_heterogeneity
missing_information:
next_skill_candidates:
  - discipline-scrnaseq
  - biomaster
  - pipeline-scrnaseq-tumor
  - plan-scrnaseq-tumor-heterogeneity
```

## Boundaries
Do not execute commands, generate PLAN.yaml, or load exec/debug skills.
