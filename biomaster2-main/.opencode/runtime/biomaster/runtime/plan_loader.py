from __future__ import annotations

from pathlib import Path
import yaml

from biomaster.runtime.run_context import RunContext


def load_plan(plan_path: Path) -> dict:
    data = yaml.safe_load(plan_path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"PLAN.yaml must be a mapping: {plan_path}")
    if "steps" not in data or not isinstance(data["steps"], list):
        raise ValueError("PLAN.yaml must contain a steps list")
    return data


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
