# biomaster-debug

Purpose: Debug failed step via Debug Agent.

Usage: `/biomaster-debug <args>`

## Rule

This command is orchestrated by `biomaster-intake`; `@biomaster-debug` is a worker subagent only.

Run after Execute for execution-level validation, or after Check returns failed `check_result`.

Advance to `debugging`, query SQLite, and load only the bounded `debug-*`, `env-*`, `verify-*`, and necessary `exec-*` skills for the failed/current step.

Debug must not replan the workflow, broaden the biological question, or change unrelated steps. Return a bounded retry plan to `@biomaster-execute`.

If execution logs and required outputs are valid, Debug returns `status: pass` and the step can proceed to Check. Otherwise it returns `status: fail` and `next_action: retry_execute`.
