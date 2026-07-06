# biomaster-resume

Purpose: Resume an interrupted project from run_states or project files.

Usage: `/biomaster-resume <args>`

## Rule

Resume through `biomaster-plan` as the visible primary agent. First scan `projects/`, then read each candidate's `PLAN.yaml`, `PROJECT_LOG.yaml`, and `CHECK_REPORT.yaml` when present. Summarize the current phase and checked steps to the user, then continue only through the next legal phase transition.

For a selected project, use the runtime bridge for a deterministic status summary:

```bash
PYTHONPATH=.opencode/runtime python3 .opencode/runtime/biomaster/scripts/opencode_step.py status --project <project_slug>
```

Do not jump directly to Plan/Execute/Check/Debug unless the project state proves all previous phases are complete. If the user wants a new task instead of continuing, create a new suffixed project folder.

When multiple candidate projects exist, summarize them in a short table and invoke OpenCode's native option selector / QuestionTool with:

- `Resume selected project`
- `Review completed results`
- `Create new suffixed project`

Do not proceed until the user selects one option.
