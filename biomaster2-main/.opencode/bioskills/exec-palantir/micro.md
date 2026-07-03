# Exec Palantir

## Operational Notes

# exec-palantir

## Purpose
Provide command templates, parameter conventions, log paths, and output conventions for palantir.

## Procedure
1. Validate inputs against step contract.
2. Write script under `projects/<project_slug>/steps/<step_id>/`.
3. Execute with logged stdout/stderr.
4. Emit `step_result.yaml`.

## Boundaries
Do not replan workflow or modify PLAN objectives.
