# biomaster-plan

Purpose: Enter planning: Skill Finder + Plan Agent → PLAN.yaml

Usage: `/biomaster-plan <args>`

## Rule

This command is orchestrated by `biomaster-plan`. The visible conversation remains with Plan.

Only run after these phases are complete:

```text
init -> mode_selection -> domain_anchoring -> pipeline_routing
```

Then advance through project selection and write `projects/<project_slug>/PLAN.yaml`.

Project slug must be semantic: derive it from dataset, analysis type, and user goal, for example `maynard2020-3k-tumor-scrnaseq-heterogeneity`. Do not create new numeric project names such as `001` or `002`.

Before writing a new plan, always scan `projects/` for candidate folders. For every candidate, inspect `PLAN.yaml`, `PROJECT_LOG.yaml`, and `CHECK_REPORT.yaml` when present. If a matching project already exists, summarize the candidates, then invoke OpenCode's native option selector / QuestionTool with:

- `Continue existing project`
- `Create new suffixed project`
- `Review existing results`

Do not ask this as plain prose unless the native selector is unavailable.

Before writing `PLAN.yaml`, gather deterministic SQLite evidence with:

```bash
PYTHONPATH=.opencode/runtime python3 .opencode/runtime/biomaster/scripts/opencode_step.py plan-context --project <project_slug> --request "<user_request>" --include-optional --save-run-state
```

Use the returned `selected_route_id`, `selected_skill_ids`, route candidates, IO contract, and manifests as the planning basis. Do not create `PLAN.yaml` from prompt memory alone.

After `PLAN.yaml` is written or updated, Plan must rebuild the visible task checklist from `PLAN.yaml.steps`:

```text
Step <step_id>: <objective> — Execute -> Debug -> Check
```

The visible task count must equal `len(PLAN.yaml.steps)`. Do not keep the pre-plan phase checklist.

Do not load exec/debug/env skills. Do not generate shell commands.
