---
name: verify-trajectory
description: Verify Palantir trajectory outputs.
compatibility: opencode
metadata:
  layer: verify
  output: trajectory
  discipline: scrnaseq
  status: active
---

# verify-trajectory

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
