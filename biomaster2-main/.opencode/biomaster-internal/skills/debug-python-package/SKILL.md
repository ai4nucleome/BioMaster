---
name: debug-python-package
description: Diagnose and repair missing Python package.
compatibility: opencode
metadata:
  layer: debug
  failure: missing_Python_package
  status: active
---

# debug-python-package

## Purpose
Bounded repair for: missing Python package.

## Boundaries
Fix only the failed step. Do not replan the workflow.
