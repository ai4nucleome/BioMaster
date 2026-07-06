# biomaster-check

Purpose: Check step outputs via Check Agent, verify skills, and update the project log.

Usage: `/biomaster-check <args>`

## Rule

This command is orchestrated by `biomaster-plan`; `@biomaster-check` is a worker subagent only.

Only run after Debug passes execution-level validation for a specific PLAN step. Advance to `checking`, load only `verify-*`, and return a structured `check_result`.

Check Agent must not fix outputs, rewrite commands, change PLAN.yaml, or talk directly with the user as the main agent.

## Fixed runtime bridge call

Check worker must run exactly:

```bash
PYTHONPATH=.opencode/runtime python3 .opencode/runtime/biomaster/scripts/opencode_step.py check-step --project <project_slug> --step-id <step_id>
```

Use the command output as the source of truth. Do not manually check invented paths.

For every checked step:

- Query SQLite for `required_verify_skills`.
- Compare actual files against `PLAN.yaml.expected_outputs`.
- Check `step_result.yaml` and generated `scripts/<step_id>/run.sh`.
- Write output-level evidence into `projects/<project_slug>/CHECK_REPORT.yaml`.
- Append the audited step record to `projects/<project_slug>/PROJECT_LOG.yaml`.
- Regenerate `projects/<project_slug>/REPORT.md` from `PROJECT_LOG.yaml`.
- Refresh `projects/<project_slug>/OPENCODE_VIEW.md`.
- Mark missing outputs as `fail`; do not silently pass incomplete steps.

Canonical paths:

- Step result: `projects/<project_slug>/steps/<step_id>/step_result.yaml`
- Report: `projects/<project_slug>/REPORT.md`
- OpenCode view: `projects/<project_slug>/OPENCODE_VIEW.md`

Invalid paths include `steps/<step_id>/REPORT.md`, `steps/<step_id>/OPENCODE_VIEW.md`, and `step_<number>_result.yaml`.
