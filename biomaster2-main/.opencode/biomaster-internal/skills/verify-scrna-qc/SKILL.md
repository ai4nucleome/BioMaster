---
name: verify-scrna-qc
description: Verify scRNA-seq QC outputs and AnnData integrity.
compatibility: opencode
metadata:
  layer: verify
  output: scrna_qc
  discipline: scrnaseq
  status: active
---

# verify-scrna-qc

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
