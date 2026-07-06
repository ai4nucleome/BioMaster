# Version Notes

This repository contains the BioMaster v0.5 deployment release.

## Scope

- Project root: repository root.
- BioMaster OpenCode configuration root: `.opencode/`.
- Embedded OpenCode engine: `opencode/`.
- One public OpenCode skill: `biomaster`.
- Core workflow agents: `biomaster-plan`, `biomaster-execute`, `biomaster-debug`, and `biomaster-check`.
- Skill-management agents: `biomaster-skiller`, `biomaster-skill-author`, and `biomaster-skill-creator`.
- SQLite-first route and skill selection.
- Serial step loop: Execute -> Debug -> Check.
- Canonical BioSkills source: `.opencode/bioskills/`.
- Generated SQLite cache: `.opencode/knowledge/biomaster_skills.db`.
- Single browser-facing deployment port through `./run.sh`; backend API remains internal and is proxied by the frontend.

## Release Check

```bash
make validate
make index
make test
make compliance
```
