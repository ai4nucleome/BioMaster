---
name: debug-missing-files
description: Diagnose and repair missing input or reference files.
compatibility: opencode
metadata:
  layer: debug
  failure: missing_input_or_reference_files
  status: active
---

# debug-missing-files

## Purpose
Bounded repair for: missing input or reference files.

## Boundaries
Fix only the failed step. Do not replan the workflow.
