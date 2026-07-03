from __future__ import annotations

from pathlib import Path
from datetime import datetime, timezone
import yaml

from biomaster.knowledge import PROJECT_ROOT


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def new_run_id(prefix: str = "run", *, runs_root: Path | None = None) -> str:
    root = runs_root or PROJECT_ROOT / "runs"
    root.mkdir(parents=True, exist_ok=True)
    used: set[int] = set()
    for path in root.iterdir():
        if path.is_dir() and path.name.isdigit():
            used.add(int(path.name))
    next_id = 1
    while next_id in used:
        next_id += 1
    return f"{next_id:03d}"


class RunContext:
    def __init__(self, run_id: str, root: Path | None = None) -> None:
        self.run_id = run_id
        self.root = root or PROJECT_ROOT / "runs" / run_id
        self.root.mkdir(parents=True, exist_ok=True)
        (self.root / "steps").mkdir(exist_ok=True)
        (self.root / "a2a").mkdir(exist_ok=True)
        (self.root / "logs").mkdir(exist_ok=True)
        (self.root / "scripts").mkdir(exist_ok=True)

    @property
    def plan_path(self) -> Path:
        return self.root / "PLAN.yaml"

    @property
    def check_report_path(self) -> Path:
        return self.root / "CHECK_REPORT.yaml"

    def step_dir(self, step_id: str) -> Path:
        path = self.root / "steps" / step_id
        path.mkdir(parents=True, exist_ok=True)
        return path

    def write_plan(self, plan: dict) -> Path:
        self.plan_path.write_text(yaml.safe_dump(plan, sort_keys=False, allow_unicode=True), encoding="utf-8")
        return self.plan_path

    def write_step_result(self, step_id: str, result: dict) -> Path:
        path = self.step_dir(step_id) / "step_result.yaml"
        path.write_text(yaml.safe_dump(result, sort_keys=False, allow_unicode=True), encoding="utf-8")
        return path

    def write_check_report(self, report: dict) -> Path:
        self.check_report_path.write_text(yaml.safe_dump(report, sort_keys=False, allow_unicode=True), encoding="utf-8")
        return self.check_report_path
