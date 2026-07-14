# Version Notes

This repository contains the BioMaster 2.0-alpha1 OpenCode-integrated alpha release.

The associated peer-reviewed article is published in *Patterns*:
<https://doi.org/10.1016/j.patter.2026.101611>.

## Scope

- Project root: repository root.
- BioMaster OpenCode configuration root: `.opencode/`.
- Embedded OpenCode engine: `BioMaster/`.
- One public OpenCode skill: `biomaster`.
- Core workflow agents: `biomaster-plan`, `biomaster-execute`, `biomaster-debug`, and `biomaster-check`.
- Skill-management agents: `biomaster-skiller`, `biomaster-skill-author`, and `biomaster-skill-creator`.
- SQLite-first route and skill selection.
- Serial step loop: Execute -> Debug -> Check.
- Role-isolated workflow and execution Skill access.
- Runtime Hard Gates and validated atomic YAML output.
- Canonical BioSkills source: `.opencode/bioskills/`.
- Generated SQLite cache: `.opencode/knowledge/biomaster_skills.db`.
- Single OpenCode server process through `./run.sh`; the same port serves the Web UI, API, SSE, WebSocket, and BioSkills routes.

## Release Check

```bash
make validate
make index
make test
make compliance
```
