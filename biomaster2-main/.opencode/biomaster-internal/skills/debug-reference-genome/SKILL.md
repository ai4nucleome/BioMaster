---
name: debug-reference-genome
description: Diagnose and repair reference genome or annotation mismatch.
compatibility: opencode
metadata:
  layer: debug
  failure: reference_genome_or_annotation_mismatch
  status: active
---

# debug-reference-genome

## Purpose
Bounded repair for: reference genome or annotation mismatch.

## Boundaries
Fix only the failed step. Do not replan the workflow.
