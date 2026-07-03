---
name: exec-cnmf
description: Run cNMF co-expression module analysis.
compatibility: opencode
metadata:
  layer: execute
  tool: cnmf
  discipline: scrnaseq
  domain: tumor
  status: active
---

# exec-cnmf

## Purpose
Provide command templates, parameter conventions, log paths, and output conventions for cnmf.

## Procedure
1. Validate inputs against step contract.
2. Write script under `runs/<run_id>/steps/<step_id>/`.
3. Execute with logged stdout/stderr.
4. Emit `step_result.yaml`.

## Boundaries
Do not replan workflow or modify PLAN objectives.
