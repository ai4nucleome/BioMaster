# biomaster-check

Purpose: Check step outputs via Check Agent and verify skills.

Usage: `/biomaster-check <args>`

## Rule

This command is orchestrated by `biomaster-intake`; `@biomaster-check` is a worker subagent only.

Only run after Debug passes execution-level validation for a specific PLAN step. Advance to `checking`, load only `verify-*`, and return a structured `check_result`.

Check Agent must not fix outputs, rewrite commands, change PLAN.yaml, or talk directly with the user as the main agent.

For every checked step:

- Query SQLite for `required_verify_skills`.
- Compare actual files against `PLAN.yaml.expected_outputs`.
- Check `step_result.yaml` and generated `scripts/<step_id>/run.sh`.
- Write output-level evidence into `runs/<run_id>/CHECK_REPORT.yaml`.
- Mark missing outputs as `fail`; do not silently pass incomplete steps.
