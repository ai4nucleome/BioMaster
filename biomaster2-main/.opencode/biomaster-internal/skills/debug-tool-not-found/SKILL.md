---
name: debug-tool-not-found
description: Diagnose and repair missing CLI tool.
compatibility: opencode
metadata:
  layer: debug
  failure: missing_CLI_tool
  status: active
---

# debug-tool-not-found

## Purpose
Bounded repair for: missing CLI tool.

## Boundaries
Fix only the failed step. Do not replan the workflow.
