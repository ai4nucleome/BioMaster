from __future__ import annotations

from pathlib import Path

from biomaster.runtime.run_context import RunContext
from biomaster.runtime.yaml_io import load_yaml_mapping, validate_plan


def load_plan(plan_path: Path) -> dict:
    return load_yaml_mapping(plan_path, document_name="PLAN.yaml", validator=validate_plan)


def get_step(plan: dict, step_id: str) -> dict:
    for step in plan["steps"]:
        if step.get("step_id") == step_id:
            return step
    raise KeyError(f"unknown step_id: {step_id}")


def save_plan_from_template(run: RunContext, template_path: Path) -> Path:
    plan = load_plan(template_path)
    plan["plan_id"] = run.run_id
    plan["run_id"] = run.run_id
    plan["run_dir"] = run.root.as_posix()
    return run.write_plan(plan)
