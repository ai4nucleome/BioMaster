# BioMaster OpenCode Skill

BioMaster is packaged as a single OpenCode directory: `.opencode/`. The public surface is one skill, `biomaster`; planning, execution, checking, debugging, knowledge retrieval, and SQLite control logic live inside the same `.opencode` package.

## Install Model

For end users, the installable unit is:

```text
.opencode/
```

The repository root contains developer conveniences such as `README.md`, `Makefile`, `tests/`, `examples/`, and CI. The runtime required by BioMaster itself is under `.opencode/runtime/biomaster`.

```text
biomaster-skill/
  .opencode/
    opencode.json                  # OpenCode agent configuration
    agents/                        # Plan primary plus Execute, Debug, Check workers
    commands/                      # biomaster-* command behavior
    skills/biomaster/SKILL.md      # the only public skill
    bioskills/                     # unified BioSkills library and control skills
    knowledge/
      biomaster_skills.db          # generated SQLite cache, not committed
    runtime/biomaster/             # Python backend used by commands/tests
  examples/                        # small fixtures and demo requests
  tests/                           # developer test suite
  projects/                        # generated project artifacts, ignored
```

## Workflow

BioMaster follows a strict SQLite-governed workflow:

```text
init -> mode_selection -> domain_anchoring -> pipeline_routing
  -> project_selection -> planning -> preflight
  -> Execute(step N) -> Debug(step N) -> Check(step N)
       pass -> step N+1
       fail -> retry/debug current step only
  -> reporting -> done
```

Hard gates:

- Planning must select a route from SQLite `pipeline_routes`.
- Each step must resolve required skills from SQLite `skills` before script generation.
- Later step scripts are not generated until the current step passes Debug and Check.
- BioSkills under `.opencode/bioskills` are the single knowledge source. SQLite tables are rebuilt from that folder and do not have a separate hand-maintained knowledge corpus.
- `biomaster-plan` is the visible primary agent. Worker calls should stay visible in OpenCode as `@biomaster-execute`, `@biomaster-debug`, and `@biomaster-check`.
- New work is stored under `projects/<project_slug>/`; matching projects should be summarized so the user can choose resume or a new suffixed project folder.
- Project slugs are semantic and should be derived from dataset, analysis type, and goal, for example `maynard2020-3k-tumor-scrnaseq-heterogeneity`.
- Before planning, BioMaster scans existing `projects/` folders and reads `PLAN.yaml`, `PROJECT_LOG.yaml`, and `CHECK_REPORT.yaml` when available.
- User decisions such as mode selection and project resume/new-project choices should use OpenCode's native option selector when available, with a concise numbered fallback only if the selector is unavailable.
- User-facing progress is concise by default; detailed execution evidence is written to `PROJECT_LOG.yaml`, `REPORT.md`, and `OPENCODE_VIEW.md`.

## Quick Start

```bash
python3 -m pip install -r requirements.txt
make knowledge-seed
make test
```

`make knowledge-seed` builds `.opencode/knowledge/biomaster_skills.db` from tracked BioSkills and seeded routes:

- `.opencode/bioskills`
- seeded `pipeline_routes`

Generated files are ignored by Git:

- `.opencode/knowledge/biomaster_skills.db`
- `.opencode/node_modules/` and `.opencode/package*.json`
- `projects/*/`
- `test_output.h5ad`
- `examples/results/*`
- Python cache files

## OpenCode Usage

Start from the public skill or command:

```text
/biomaster-start tumor heterogeneity and state trajectory analysis
```

Only `biomaster` should be visible as a public skill. Internal skills are selected by BioMaster through SQLite and phase rules.

## Agents

| Agent | Role |
|---|---|
| `biomaster-plan` | primary user-facing coordinator, project selector, SQLite route gate, and `PLAN.yaml` author |
| `biomaster-execute` | generates and executes exactly one approved plan step |
| `biomaster-debug` | inspects script execution status, logs, exit code, and retry advice |
| `biomaster-check` | verifies outputs and maintains `CHECK_REPORT.yaml`, `PROJECT_LOG.yaml`, and `REPORT.md` |

The Python serial orchestrator in `.opencode/runtime/biomaster/runtime/step_orchestrator.py` is for tests and implementation support. It is not a replacement for visible OpenCode worker subagent calls.

## Knowledge Queries

```bash
make knowledge-seed

PYTHONPATH=.opencode/runtime python3 .opencode/runtime/biomaster/knowledge/query_skills.py --list-skills
PYTHONPATH=.opencode/runtime python3 .opencode/runtime/biomaster/knowledge/query_skills.py --list-routes
```

## Adding BioSkills

Use the scaffold command or the BioSkills Library UI so metadata and phase selection stay consistent:

```bash
make skill-add ARGS='spatial-routing --target plan --description "Plan spatial transcriptomics routing" --metadata-value spatial-transcriptomics'
make skill-add ARGS='xenium-qc --target execute --description "Execute Xenium QC" --metadata-value xenium-qc'
make knowledge-seed
```

Skill names are normalized to the correct prefix: `plan-*`, `exec-*`, `verify-*`, `debug-*`, or `report-*`.

## Developer Checks

```bash
make validate
make compliance
make pytest
make clean
```

The GitHub Actions workflow in `.github/workflows/ci.yml` runs `make test`. See [CONTRIBUTING.md](CONTRIBUTING.md) for development guidance.

Run `make clean` before publishing to remove generated SQLite databases, project artifacts, temporary AnnData files, OpenCode package-manager files, and Python caches.

## Release Notes

- `.opencode/` is the BioMaster OpenCode package.
- Root-level files support development and testing.
- Add a `LICENSE` file before public release if you want explicit reuse terms.
