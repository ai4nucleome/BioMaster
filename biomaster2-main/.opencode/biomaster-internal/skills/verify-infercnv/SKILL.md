---
name: verify-infercnv
description: Verify inferCNVpy outputs and malignancy calls.
compatibility: opencode
metadata:
  layer: verify
  output: infercnv
  discipline: scrnaseq
  status: active
---

# verify-infercnv

## Output format
```
status: pass | fail
failed_check:
reason:
suggested_debug_skills:
next_action:
```

## Boundaries
Check only — never repair outputs or rewrite commands.
