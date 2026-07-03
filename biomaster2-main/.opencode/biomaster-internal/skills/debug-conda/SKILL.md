---
name: debug-conda
description: Diagnose and repair conda environment errors.
compatibility: opencode
metadata:
  layer: debug
  failure: conda_environment_errors
  status: active
---

# debug-conda

## Purpose
Bounded repair for: conda environment errors.

## Boundaries
Fix only the failed step. Do not replan the workflow.
