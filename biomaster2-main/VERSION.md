# Version Notes

This repository contains the active BioMaster OpenCode MVP.

## Scope

- Installable OpenCode package root: `.opencode/`.
- One public OpenCode skill: `biomaster`.
- Five OpenCode agents: Intake, Plan, Execute, Debug, Check.
- SQLite-first route and skill selection.
- Serial step loop: Execute -> Debug -> Check.
- Extensible internal skill roots for `plan-*`, `exec-*`, `verify-*`, `debug-*`, and `report-*` skills.

## Release Check

```bash
make test
make compliance
```
