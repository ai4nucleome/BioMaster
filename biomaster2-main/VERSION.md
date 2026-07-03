# Version Notes

This repository contains the active BioMaster OpenCode MVP.

## Scope

- Installable OpenCode package root: `.opencode/`.
- One public OpenCode skill: `biomaster`.
- Four active OpenCode agents: Plan primary plus Execute, Debug, Check workers. `biomaster-intake.md` is retained only as compatibility documentation.
- SQLite-first route and skill selection.
- Serial step loop: Execute -> Debug -> Check.
- Extensible internal skill roots for `plan-*`, `exec-*`, `verify-*`, `debug-*`, and `report-*` skills.

## Release Check

```bash
make test
make compliance
```
