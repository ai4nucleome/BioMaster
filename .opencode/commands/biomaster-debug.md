# biomaster-debug

Purpose: Inspect script execution evidence via Debug Agent.

Usage: `/biomaster-debug <args>`

## Rule

This command is orchestrated by `biomaster-plan`; `@biomaster-debug` is a worker subagent only.

Run after Execute for execution-level validation.

Advance to `debugging`, query SQLite, and load only the bounded `debug-*`, `env-*`, and necessary `exec-*` skills for the failed/current step.

Debug must not replan the workflow, broaden the biological question, check biological expected outputs, or change unrelated steps. Return execution status, error evidence, and bounded retry advice to `@biomaster-execute`.

If the script ran with `exit_code: 0` and `execution_status: success`, Debug returns `status: pass` and the step can proceed to Check. Otherwise it returns `status: fail` and `next_action: retry_execute`.

## Fixed runtime bridge call

Debug worker must run exactly:

```bash
PYTHONPATH=.opencode/runtime python3 .opencode/runtime/biomaster/scripts/opencode_step.py debug-step --project <project_slug> --step-id <step_id>
```

Use the command output as the source of truth for `execution_status`, `exit_code`, stdout/stderr, and retry advice. Do not infer pass/fail from chat text alone.
