# biomaster-run

Purpose: Execute the next eligible PLAN.yaml step via Execute Agent.

Usage: `/biomaster-run <args>`

## Rule

This command is orchestrated by `biomaster-plan`; `@biomaster-execute` is a worker subagent only.

The step loop must use visible OpenCode worker subagent calls. Do not run `run_step_cycle()`, `run_plan_serial()`, ad hoc Python scripts, or shell snippets from Plan as a replacement for worker agents.

Only run after an approved `PLAN.yaml` exists and the run state has passed:

```text
planning -> preflight -> execution
```

Execute one planned step at a time. Do not generate or run scripts for later steps until the current step has passed Debug and Check. Do not replan, change analysis goals, or load debug skills unless a bounded debug retry has been issued.

Ask for user confirmation once before starting or resuming the step loop. Do not show an option selector before every normal step. After a step passes Check, continue to the next planned step automatically while showing concise status. Ask again only after failure, plan change, risky environment mutation, or explicit user request for manual gating.

Before generating any step script, Execute must query SQLite `skills` for the current step's `required_execute_skills` / `required_report_skills` through the runtime bridge.

Write generated scripts and step-local results under:

```text
projects/<project_slug>/scripts/<step_id>/
projects/<project_slug>/steps/<step_id>/
```

`step_result.yaml` must include `sqlite_skill_query`, `execution_status`, `exit_code`, `script_path`, `stdout_path`, and `stderr_path`.

For OpenCode browsing, refresh `projects/<project_slug>/OPENCODE_VIEW.md` after Check. Do not create a separate `outputs/` directory unless a specific external tool requires that exact path.

After execution, route the step to Debug before Check:

```text
@biomaster-execute step N
  -> @biomaster-debug execution review
  -> @biomaster-check secondary review
  -> @biomaster-execute step N+1 only after Check passes
```

If Debug fails, retry Execute for the same step instead of calling Check.

If Check passes, return to Plan so it can request the next step. If Check fails, route evidence back through Debug/Execute for the same step.

The visible task checklist is plan-step based. Mark `Step <step_id>` complete only after `@biomaster-check` returns `pass`. Do not mark a task complete after Execute or Debug alone.

## Fixed runtime bridge calls

When Plan calls workers, include the exact project slug and canonical step ID from `PLAN.yaml`.

Execute worker must run:

```bash
PYTHONPATH=.opencode/runtime python3 .opencode/runtime/biomaster/scripts/opencode_step.py execute-step --project <project_slug> --step-id <step_id>
```

Debug worker must run:

```bash
PYTHONPATH=.opencode/runtime python3 .opencode/runtime/biomaster/scripts/opencode_step.py debug-step --project <project_slug> --step-id <step_id>
```

Check worker must run:

```bash
PYTHONPATH=.opencode/runtime python3 .opencode/runtime/biomaster/scripts/opencode_step.py check-step --project <project_slug> --step-id <step_id>
```

Do not invent paths. `REPORT.md`, `PROJECT_LOG.yaml`, `CHECK_REPORT.yaml`, and `OPENCODE_VIEW.md` are project-root files. Step evidence is always `projects/<project_slug>/steps/<step_id>/step_result.yaml`.
