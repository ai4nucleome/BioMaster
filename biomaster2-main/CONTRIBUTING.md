# Contributing

BioMaster is organized as a single OpenCode package, `.opencode/`, plus root-level developer tooling. Keep runtime changes inside `.opencode` whenever possible.

## Source Areas

- `.opencode/skills/biomaster`: the only public user-facing skill.
- `.opencode/biomaster-internal/skills`: internal planning, execution, verification, debugging, environment, and reporting skills.
- `.opencode/knowledge`: numbered workflow/task knowledge records used for retrieval context.
- `.opencode/runtime/biomaster/knowledge`: SQLite schema, sync, route selection, and phase policy.
- `.opencode/runtime/biomaster/runtime`: run directory helpers, execution/debug/check helpers, and OpenCode artifact views.
- `.opencode/runtime/biomaster/a2a`: structured worker-agent messages.
- `examples` and `tests`: developer fixtures and regression tests.

## Local Setup

```bash
python3 -m pip install -r requirements.txt
make knowledge-seed
make test
```

`make knowledge-seed` generates `.opencode/knowledge/biomaster_skills.db` from tracked source files. Do not commit the generated DB.

## Adding Internal Skills

Use the scaffold command so metadata stays consistent:

```bash
make skill-add ARGS='my-skill --target execute --description "Execute my tool" --metadata-value my-tool'
make knowledge-seed
```

Internal skills are discoverable through SQLite and phase filters. They should not be exposed as public OpenCode skills.

## Knowledge Records

Numbered workflow/task records under `.opencode/knowledge/workflows` and `.opencode/knowledge/tasks` are retrieval context. They must not bypass `pipeline_routes`, phase policy, or step-level skill gates.

## Path Policy

- End-user installation should only require `.opencode/`.
- Python imports should assume `PYTHONPATH=.opencode/runtime`.
- Do not introduce a second root-level runtime package.
- Do not commit generated SQLite DBs, run directories, logs, or Python caches.

## Release Check

Before opening a PR or publishing:

```bash
make clean
make test
make clean
```

The final `make clean` keeps the repository free of generated DBs, run artifacts, and test outputs.
