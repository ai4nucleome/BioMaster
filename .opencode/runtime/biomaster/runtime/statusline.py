from __future__ import annotations

from pathlib import Path
import json
import sqlite3
import sys
from typing import Any

import yaml

from biomaster.knowledge import DEFAULT_DB_PATH, PROJECT_ROOT


DB_PATH = DEFAULT_DB_PATH
PROJECTS_ROOT = PROJECT_ROOT / "projects"


def _read_json_stdin() -> dict[str, Any]:
    try:
        raw = sys.stdin.read()
        return json.loads(raw) if raw.strip() else {}
    except json.JSONDecodeError:
        return {}


def _read_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return data if isinstance(data, dict) else {}


def _latest_run_from_db() -> dict[str, Any] | None:
    if not DB_PATH.exists():
        return None
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    try:
        row = connection.execute(
            "SELECT * FROM run_states ORDER BY updated_at DESC, id DESC LIMIT 1"
        ).fetchone()
        return dict(row) if row else None
    except sqlite3.Error:
        return None
    finally:
        connection.close()


def _latest_project_from_files() -> str | None:
    if not PROJECTS_ROOT.exists():
        return None
    candidates = sorted(
        (path for path in PROJECTS_ROOT.iterdir() if path.is_dir()),
        key=lambda path: path.stat().st_mtime,
    )
    return candidates[-1].name if candidates else None


def _step_counts(run_dir: Path) -> tuple[int, int, str]:
    plan = _read_yaml(run_dir / "PLAN.yaml")
    steps = [str(step.get("step_id")) for step in plan.get("steps", []) if step.get("step_id")]
    report = _read_yaml(run_dir / "CHECK_REPORT.yaml")
    passed = {
        str(item.get("step_id"))
        for item in report.get("checks", [])
        if item.get("status") == "pass"
    }
    total = len(steps)
    done = len([step_id for step_id in steps if step_id in passed])
    current = next((step_id for step_id in steps if step_id not in passed), "")
    return total, done, current


def build_status(payload: dict[str, Any]) -> str:
    cwd = Path(str(payload.get("cwd") or payload.get("workspace", {}).get("current_dir") or ""))
    if cwd and PROJECT_ROOT not in [cwd, *cwd.parents] and cwd not in PROJECT_ROOT.parents:
        return ""

    run_state = _latest_run_from_db()
    run_id = str(run_state.get("run_id")) if run_state else (_latest_project_from_files() or "")
    if not run_id:
        return "BioMaster: no active project"

    phase = str(run_state.get("phase") or "unknown") if run_state else "unknown"
    run_dir = PROJECTS_ROOT / run_id
    total, done, current = _step_counts(run_dir)
    remaining = max(total - done, 0)
    if total:
        progress = f"{done}/{total} steps complete, {remaining} remaining"
        current_text = f", current: {current}" if current else ""
    else:
        progress = "PLAN not registered"
        current_text = ""

    return f"BioMaster project {run_id} | phase: {phase} | {progress}{current_text}"


def main() -> None:
    status = build_status(_read_json_stdin())
    if status:
        print(status)


if __name__ == "__main__":
    main()
