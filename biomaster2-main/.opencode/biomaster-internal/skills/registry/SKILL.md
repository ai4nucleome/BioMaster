---
name: registry
description: Route user requests to domain, discipline, and candidate tumor scRNA-seq pipelines via SQLite pipeline routes.
compatibility: opencode
metadata:
  layer: registry
  domain: bioinformatics
  status: active
---

# BioMaster Skill Registry

## Purpose

Identify the user's analysis direction and return a candidate pipeline route. Do not execute analysis or write shell commands.

## When to use

- **Do not load at cold start**. `init` and `mode_selection` use only the public `biomaster` entry skill.
- Use this internal registry only after Intake advances to `domain_anchoring` / `pipeline_routing`.

## Procedure

1. Parse the user goal and data hints.
2. Query SQLite pipeline routes at `.opencode/knowledge/biomaster_skills.db` via Skill Finder or `query_skills.py --search-routes`.
3. Decide whether the request belongs to tumor research and scRNA-seq.
4. If tumor heterogeneity / trajectory / inferCNV / Palantir / cNMF is mentioned, candidate pipeline is `tumor_scrnaseq_heterogeneity` via route `tumor_scrnaseq_heterogeneity`.
5. Record missing information but do not ask for data paths before operating mode is chosen (see `domain-guide-tumor`).

## Skill loading policy

`next_skill_candidates` is a routing recommendation, not a load instruction.

Actual loading must still be controlled by Skill Finder and the current phase:

- `init` / `mode_selection`: load only `biomaster`
- `domain_anchoring`: registry may be selected internally with matched `domain-guide-*`
- later phases: load only the layers allowed for that phase

## Inputs

- user natural language goal
- optional data type hints (h5ad, 10x, FASTQ unrelated requests should lower confidence)

## Outputs

Return exactly these fields:

```yaml
domain:
discipline:
candidate_pipeline:
confidence:
missing_information:
next_skill_candidates:
```

Example (mode_selection after tumor route match):

```yaml
domain: tumor
discipline: scrnaseq
candidate_pipeline: tumor_scrnaseq_heterogeneity
confidence: high
missing_information:
  - operating_mode
next_skill_candidates:
  - domain-guide-tumor
  - discipline-scrnaseq
  - biomaster
  - pipeline-scrnaseq-tumor
  - plan-scrnaseq-tumor-heterogeneity
  - report-tumor-scrnaseq
  - exec-scanpy
  - exec-infercnvpy
  - exec-palantir
  - exec-cnmf
  - verify-scrna-qc
  - verify-infercnv
  - verify-trajectory
  - verify-cnmf
  - env-python-scrnaseq
  - debug-conda
```

Cold start example (`init`, before user goal):

```yaml
domain:
discipline:
candidate_pipeline:
confidence: low
missing_information:
  - user_goal
next_skill_candidates: []
```

## Boundaries

- Do not generate PLAN.yaml.
- Do not load exec-*, verify-*, debug-*, or env-* skills during routing.
- Do not emit shell commands.

## Validation

Routing is valid when all six required output fields are present and `next_skill_candidates` lists candidates without causing cross-phase loading.
