# biomaster-run

Purpose: Execute the next eligible PLAN.yaml step via Execute Agent.

Usage: `/biomaster-run <args>`

## Rule

This command is orchestrated by `biomaster-intake`; `@biomaster-execute` is a worker subagent only.

The step loop must use visible OpenCode worker subagent calls. Do not run `run_step_cycle()`, `run_plan_serial()`, ad hoc Python scripts, or shell snippets from Intake as a replacement for worker agents.

Only run after an approved `PLAN.yaml` exists and the run state has passed:

```text
planning -> preflight -> execution
```

Execute one planned step at a time. Do not generate or run scripts for later steps until the current step has passed Debug and Check. Do not replan, change analysis goals, or load debug skills unless a bounded debug retry has been issued.

Before generating any step script, query SQLite `skills` for the current step's `required_execute_skills` / `required_report_skills`.

Write generated scripts and step-local results under:

```text
runs/<plan_id>/scripts/<step_id>/
runs/<plan_id>/steps/<step_id>/
```

`step_result.yaml` must include `sqlite_skill_query`.

For OpenCode browsing, refresh `runs/<plan_id>/OPENCODE_VIEW.md` after Check. Do not create a separate `outputs/` directory unless a specific external tool requires that exact path.

After execution, route the step to Debug before Check:

```text
@biomaster-execute step N
  -> @biomaster-debug execution review
  -> @biomaster-check secondary review
  -> @biomaster-execute step N+1 only after Check passes
```

If Debug fails, retry Execute for the same step instead of calling Check.

If Check passes, return to Intake so it can request the next step. If Check fails, route back to Debug for the same step.

The visible task checklist is plan-step based. Mark `Step <step_id>` complete only after `@biomaster-check` returns `pass`. Do not mark a task complete after Execute or Debug alone.
