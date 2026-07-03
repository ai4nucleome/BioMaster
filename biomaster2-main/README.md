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
    agents/                        # Intake, Plan, Execute, Debug, Check prompts
    commands/                      # biomaster-* command behavior
    skills/biomaster/SKILL.md      # the only public skill
    biomaster-internal/skills/     # internal phase-specific skills
    knowledge/
      workflows/                   # numbered workflow knowledge records
      tasks/                       # numbered task/tool knowledge records
      biomaster_skills.db          # generated locally, not committed
    runtime/biomaster/             # Python backend used by commands/tests
  examples/                        # small fixtures and demo requests
  tests/                           # developer test suite
  runs/                            # generated run artifacts, ignored
```

## Workflow

BioMaster follows a strict SQLite-governed workflow:

```text
init -> mode_selection -> domain_anchoring -> pipeline_routing
  -> planning -> preflight
  -> Execute(step N) -> Debug(step N) -> Check(step N)
       pass -> step N+1
       fail -> retry/debug current step only
  -> reporting -> done
```

Hard gates:

- Planning must select a route from SQLite `pipeline_routes`.
- Each step must resolve required skills from SQLite `skills` before script generation.
- Later step scripts are not generated until the current step passes Debug and Check.
- Numbered workflow/task records in `knowledge_records` are retrieval context only; they do not bypass route or skill gates.
- Worker calls should stay visible in OpenCode as `@biomaster-plan`, `@biomaster-execute`, `@biomaster-debug`, and `@biomaster-check`.

## Quick Start

```bash
python3 -m pip install -r requirements.txt
make knowledge-seed
make test
```

`make knowledge-seed` builds `.opencode/knowledge/biomaster_skills.db` from tracked source files:

- `.opencode/skills`
- `.opencode/biomaster-internal/skills`
- `.opencode/knowledge/workflows`
- `.opencode/knowledge/tasks`
- seeded `pipeline_routes`

Generated files are ignored by Git:

- `.opencode/knowledge/biomaster_skills.db`
- `runs/[0-9][0-9][0-9]/`
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
| `biomaster-intake` | user-facing coordinator and phase gatekeeper |
| `biomaster-plan` | generates `PLAN.yaml` after SQLite route selection |
| `biomaster-execute` | executes exactly one approved plan step |
| `biomaster-debug` | validates execution and proposes bounded retries |
| `biomaster-check` | verifies outputs and maintains `CHECK_REPORT.yaml` |

The Python serial orchestrator in `.opencode/runtime/biomaster/runtime/step_orchestrator.py` is for tests and implementation support. It is not a replacement for visible OpenCode worker subagent calls.

## Knowledge Queries

```bash
make knowledge-seed

PYTHONPATH=.opencode/runtime python3 .opencode/runtime/biomaster/knowledge/query_skills.py --list-skills
PYTHONPATH=.opencode/runtime python3 .opencode/runtime/biomaster/knowledge/query_skills.py --list-routes
PYTHONPATH=.opencode/runtime python3 .opencode/runtime/biomaster/knowledge/query_skills.py --list-workflows
PYTHONPATH=.opencode/runtime python3 .opencode/runtime/biomaster/knowledge/query_skills.py --list-tasks
PYTHONPATH=.opencode/runtime python3 .opencode/runtime/biomaster/knowledge/query_skills.py --search-knowledge "DESeq2" --record-type task
```

## Adding Internal Skills

Use the scaffold command so metadata and phase selection stay consistent:

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

## Release Notes

- `.opencode/` is the BioMaster OpenCode package.
- Root-level files support development and testing.
- Add a `LICENSE` file before public release if you want explicit reuse terms.
