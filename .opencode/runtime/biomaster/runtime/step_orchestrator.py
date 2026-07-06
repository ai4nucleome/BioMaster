from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from biomaster.knowledge import DEFAULT_DB_PATH
from biomaster.runtime.checker import check_step
from biomaster.runtime.debugger import debug_step
from biomaster.runtime.executor import execute_step
from biomaster.runtime.run_context import RunContext


def _plan_step_ids(plan: dict) -> list[str]:
    return [str(step["step_id"]) for step in plan.get("steps", [])]


def _read_check_report(run: RunContext) -> dict[str, Any]:
    if not run.check_report_path.exists():
        return {"checks": []}
    data = yaml.safe_load(run.check_report_path.read_text(encoding="utf-8"))
    return data if isinstance(data, dict) else {"checks": []}


def _passed_step_ids(run: RunContext) -> set[str]:
    report = _read_check_report(run)
    return {
        str(item.get("step_id"))
        for item in report.get("checks", [])
        if item.get("status") == "pass"
    }


def assert_upstream_steps_passed(run: RunContext, plan: dict, step_id: str) -> None:
    step_ids = _plan_step_ids(plan)
    if step_id not in step_ids:
        raise KeyError(f"unknown step_id: {step_id}")
    required = step_ids[: step_ids.index(step_id)]
    passed = _passed_step_ids(run)
    missing = [item for item in required if item not in passed]
    if missing:
        raise RuntimeError(
            "cannot execute step before upstream checks pass: " + ", ".join(missing)
        )


def run_step_cycle(
    run: RunContext,
    plan: dict,
    step_id: str,
    *,
    db_path: Path = DEFAULT_DB_PATH,
) -> dict[str, Any]:
    """Run exactly one Execute -> Debug -> Check cycle.

    A passing Check is the only condition that allows the next step to start.
    """

    assert_upstream_steps_passed(run, plan, step_id)
    execution = execute_step(run, plan, step_id, db_path=db_path)
    debug = debug_step(run, plan, step_id, db_path=db_path)
    if debug["status"] != "pass":
        return {
            "step_id": step_id,
            "status": "blocked",
            "blocked_at": "debug",
            "next_action": debug.get("next_action", "retry_execute"),
            "execution": execution,
            "debug": debug,
        }

    check = check_step(run, step_id, plan=plan, db_path=db_path)
    if check["status"] != "pass":
        post_check_debug = debug_step(run, plan, step_id, db_path=db_path)
        return {
            "step_id": step_id,
            "status": "blocked",
            "blocked_at": "check",
            "next_action": "debug",
            "execution": execution,
            "debug": debug,
            "check": check,
            "post_check_debug": post_check_debug,
        }

    return {
        "step_id": step_id,
        "status": "pass",
        "next_action": "execution",
        "execution": execution,
        "debug": debug,
        "check": check,
    }


def run_plan_serial(
    run: RunContext,
    plan: dict,
    *,
    db_path: Path = DEFAULT_DB_PATH,
) -> dict[str, Any]:
    cycles: list[dict[str, Any]] = []
    for step_id in _plan_step_ids(plan):
        cycle = run_step_cycle(run, plan, step_id, db_path=db_path)
        cycles.append(cycle)
        if cycle["status"] != "pass":
            return {
                "run_id": run.run_id,
                "status": "blocked",
                "blocked_step": step_id,
                "blocked_at": cycle["blocked_at"],
                "next_action": cycle["next_action"],
                "completed_steps": [item["step_id"] for item in cycles if item["status"] == "pass"],
                "cycles": cycles,
            }

    return {
        "run_id": run.run_id,
        "status": "pass",
        "next_action": "reporting",
        "completed_steps": [item["step_id"] for item in cycles],
        "cycles": cycles,
    }
