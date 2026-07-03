# biomaster-plan

Purpose: Enter planning: Skill Finder + Plan Agent → PLAN.yaml

Usage: `/biomaster-plan <args>`

## Rule

This command is orchestrated by `biomaster-intake`. The visible conversation remains with Intake.

Only run after these phases are complete:

```text
init -> mode_selection -> domain_anchoring -> pipeline_routing
```

Then advance to `planning` and call `@biomaster-plan` via A2A `planning_request`.

After `PLAN.yaml` is written or updated, Intake must rebuild the visible task checklist from `PLAN.yaml.steps`:

```text
Step <step_id>: <objective> — Execute -> Debug -> Check
```

The visible task count must equal `len(PLAN.yaml.steps)`. Do not keep the pre-plan phase checklist.

Do not load exec/debug/env skills. Do not generate shell commands.
