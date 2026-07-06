# biomaster-start

Purpose: Start BioMaster workflow, select or create a project folder, and invoke Plan Agent for mode selection.

Usage: `/biomaster-start <user goal or empty>`

## Conversational owner

Always start and remain with `biomaster-plan` as the visible primary agent. Do not ask the user which skill to load.

## Skill loading (strict)

1. **Cold start** — load **only** `biomaster` (`--phase init`).
2. **After user states a goal** — Skill Finder `--phase mode_selection` still returns `biomaster` only; internal modules are not user choices.
3. **Do not** manually load `pipeline-*`, `discipline-*`, `plan-*`, `exec-*`, `verify-*`, `env-*`, or `debug-*` during mode selection.

## Fixed flow

Proceed only through:

```text
init -> mode_selection -> domain_anchoring -> pipeline_routing -> planning -> preflight
  -> step loop: Execute(step N) -> Debug(step N) -> Check(step N)
  -> reporting -> done
```

After operating mode and route are confirmed, Plan chooses or creates `projects/<project_slug>/`, writes `PLAN.yaml`, and coordinates visible worker subagents.

Use runtime bridge commands for deterministic state:

```bash
PYTHONPATH=.opencode/runtime python3 .opencode/runtime/biomaster/scripts/opencode_step.py projects --dataset "<dataset>" --goal "<user_goal>" --analysis-type "<analysis_type>"
PYTHONPATH=.opencode/runtime python3 .opencode/runtime/biomaster/scripts/opencode_step.py plan-context --project <project_slug> --request "<user_goal>" --include-optional --save-run-state
```

The project slug must be the same slug used later by Execute, Debug, and Check.

## Opening prompt

Use the standard Plan opening in English with a concise academic tone. The opening must remain in English and must not be translated into Chinese. Explain that BioMaster has been loaded as an integrated SQLite-governed workflow system, keep Plan as the conversation owner, and ask the user to choose test/formal/custom mode.

## OpenCode option selector

After the opening card, invoke OpenCode's native option selector / QuestionTool for mode selection. Do not continue with route search or project selection until the user has selected one of:

- `Test mode`
- `Formal analysis`
- `Custom objective`

If the native selector is unavailable, show these same options as a short numbered fallback and explicitly say that the native selector was unavailable.
