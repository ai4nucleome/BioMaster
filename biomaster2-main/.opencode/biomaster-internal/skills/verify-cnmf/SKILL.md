---
name: verify-cnmf
description: Verify cNMF module outputs.
compatibility: opencode
metadata:
  layer: verify
  output: cnmf
  discipline: scrnaseq
  status: active
---

# verify-cnmf

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
