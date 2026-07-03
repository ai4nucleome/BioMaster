# biomaster-start

Purpose: Start BioMaster workflow, create run_id, invoke Intake Agent for mode selection.

Usage: `/biomaster-start <user goal or empty>`

## Conversational owner

Always start and remain with `biomaster-intake` as the visible primary agent. Do not ask the user which skill to load.

## Skill loading (strict)

1. **Cold start** — load **only** `biomaster` (`--phase init`).
2. **After user states a goal** — Skill Finder `--phase mode_selection` still returns `biomaster` only; internal modules are not user choices.
3. **Do not** manually load `pipeline-*`, `discipline-*`, `plan-*`, `exec-*`, `verify-*`, `env-*`, or `debug-*` during Intake.

## Fixed flow

Proceed only through:

```text
init -> mode_selection -> domain_anchoring -> pipeline_routing -> planning -> preflight
  -> step loop: Execute(step N) -> Debug(step N) -> Check(step N)
  -> reporting -> done
```

After operating mode and route are confirmed, Intake sends A2A `planning_request` to `@biomaster-plan`.

## Opening prompt

Use the standard Intake opening in English with a concise academic tone. The opening must remain in English and must not be translated into Chinese. Explain that BioMaster has been loaded as an integrated SQLite-governed workflow system, keep Intake as the conversation owner, and ask the user to choose test/formal/custom mode.
