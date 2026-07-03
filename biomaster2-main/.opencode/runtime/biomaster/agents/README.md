# Agents & Runtime

OpenCode agent definitions live in `.opencode/agents/`.
Slash command behavior lives in `.opencode/commands/`.
The Python backend lives in `.opencode/runtime/biomaster/`.

## Collaboration Flow

```text
Intake (mode_selection)
  → Plan (PLAN.yaml + manifests)
  → Step loop:
      Execute(step N) → Debug(step N) → Check(step N)
      pass → Execute(step N+1)
      fail → Debug/Retry(step N)
  → Report (REPORT.md)
```

Agents exchange structured messages through `.opencode/runtime/biomaster/a2a/`; worker handoffs should not rely on unstructured natural-language state.

## Python Modules

| Module | Purpose |
|---|---|
| `.opencode/runtime/biomaster/knowledge/skill_finder.py` | route matching and agent/phase filtering |
| `.opencode/runtime/biomaster/knowledge/prompt_assembler.py` | skill-body and manifest assembly |
| `.opencode/runtime/biomaster/knowledge/state_manager.py` | `run_states` CRUD |
| `.opencode/runtime/biomaster/a2a/` | message construction and validation |
| `.opencode/runtime/biomaster/runtime/` | run directories and step execution helpers |
| `.opencode/runtime/biomaster/compliance/plan_audit.py` | release compliance checks |

## Quick Validation

```bash
make knowledge-seed
PYTHONPATH=.opencode/runtime python3 .opencode/runtime/biomaster/knowledge/skill_finder.py \
  "tumor heterogeneity and state trajectory analysis" --agent biomaster-plan --phase planning
make compliance
```

See the root [README.md](../../../../README.md) for setup and release checks.
