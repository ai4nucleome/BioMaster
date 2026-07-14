from __future__ import annotations

from pathlib import Path
from datetime import datetime, timezone
import re
import yaml

from biomaster.knowledge import PROJECT_ROOT
from biomaster.runtime.yaml_io import (
    atomic_write_yaml,
    validate_check_report,
    validate_plan,
    validate_project_log,
)


PROJECTS_ROOT = PROJECT_ROOT / "projects"


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def slugify_project_name(value: str | None, *, default: str = "biomaster-project") -> str:
    raw = (value or default).strip().lower()
    slug = re.sub(r"[^a-z0-9]+", "-", raw).strip("-")
    return slug or default


def semantic_project_slug(
    *,
    dataset: str | None = None,
    goal: str | None = None,
    analysis_type: str | None = None,
    default: str = "biomaster-project",
) -> str:
    parts: list[str] = []
    for value in (dataset, analysis_type, goal):
        slug = slugify_project_name(value, default="")
        if slug:
            parts.extend(piece for piece in slug.split("-") if piece)
    seen: list[str] = []
    for part in parts:
        if part not in seen:
            seen.append(part)
    if not seen:
        return default
    return "-".join(seen[:10])


def list_project_dirs(*, projects_root: Path | None = None) -> list[Path]:
    root = projects_root or PROJECTS_ROOT
    if not root.exists():
        return []
    return sorted(path for path in root.iterdir() if path.is_dir())


def summarize_project_dir(path: Path) -> dict[str, object]:
    def read_yaml(name: str) -> dict:
        target = path / name
        if not target.exists():
            return {}
        data = yaml.safe_load(target.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}

    plan = read_yaml("PLAN.yaml")
    project_log = read_yaml("PROJECT_LOG.yaml")
    check_report = read_yaml("CHECK_REPORT.yaml")
    steps = plan.get("steps") or []
    logged_steps = project_log.get("steps") or []
    passed = [
        str(item.get("step_id"))
        for item in logged_steps
        if (item.get("check") or {}).get("status") == "pass"
    ]
    return {
        "project_id": path.name,
        "project_dir": str(path),
        "dataset": plan.get("dataset") or project_log.get("dataset", ""),
        "analysis_type": plan.get("analysis_type") or project_log.get("analysis_type", ""),
        "selected_route_id": plan.get("selected_route_id") or project_log.get("selected_route_id", ""),
        "total_steps": len(steps),
        "passed_steps": len(passed),
        "last_step": str(logged_steps[-1].get("step_id")) if logged_steps else "",
        "overall_status": check_report.get("overall_status", ""),
        "has_plan": bool(plan),
        "has_project_log": bool(project_log),
    }


def find_matching_projects(
    *,
    dataset: str | None = None,
    goal: str | None = None,
    analysis_type: str | None = None,
    projects_root: Path | None = None,
) -> list[dict[str, object]]:
    query_parts = set(semantic_project_slug(dataset=dataset, goal=goal, analysis_type=analysis_type, default="").split("-"))
    matches: list[dict[str, object]] = []
    for path in list_project_dirs(projects_root=projects_root):
        summary = summarize_project_dir(path)
        haystack = " ".join(
            str(summary.get(key, ""))
            for key in ("project_id", "dataset", "analysis_type", "selected_route_id")
        )
        hay_parts = set(slugify_project_name(haystack, default="").split("-"))
        if not query_parts or query_parts.intersection(hay_parts):
            matches.append(summary)
    return sorted(matches, key=lambda item: (str(item.get("dataset")), str(item.get("project_id"))))


def _next_suffixed_slug(base_slug: str, root: Path) -> str:
    used = {path.name for path in list_project_dirs(projects_root=root)}
    if base_slug not in used:
        return base_slug
    index = 2
    while f"{base_slug}-{index:03d}" in used:
        index += 1
    return f"{base_slug}-{index:03d}"


def new_project_id(project_name: str | None = None, *, projects_root: Path | None = None, force_new: bool = True) -> str:
    root = projects_root or PROJECTS_ROOT
    root.mkdir(parents=True, exist_ok=True)
    base_slug = slugify_project_name(project_name)
    if not force_new and (root / base_slug).exists():
        return base_slug
    return _next_suffixed_slug(base_slug, root)


def new_semantic_project_id(
    *,
    dataset: str | None = None,
    goal: str | None = None,
    analysis_type: str | None = None,
    projects_root: Path | None = None,
    force_new: bool = True,
) -> str:
    return new_project_id(
        semantic_project_slug(dataset=dataset, goal=goal, analysis_type=analysis_type),
        projects_root=projects_root,
        force_new=force_new,
    )


def new_run_id(prefix: str = "biomaster-project", *, runs_root: Path | None = None) -> str:
    """Compatibility alias for project slug generation."""

    return new_project_id(prefix, projects_root=runs_root or PROJECTS_ROOT, force_new=True)


def resolve_project_dir(project_id: str, *, projects_root: Path | None = None) -> Path:
    return (projects_root or PROJECTS_ROOT) / slugify_project_name(project_id)


class RunContext:
    def __init__(self, run_id: str, root: Path | None = None) -> None:
        self.run_id = run_id
        self.root = root or resolve_project_dir(run_id)
        self.root.mkdir(parents=True, exist_ok=True)
        (self.root / "steps").mkdir(exist_ok=True)
        (self.root / "a2a").mkdir(exist_ok=True)
        (self.root / "logs").mkdir(exist_ok=True)
        (self.root / "scripts").mkdir(exist_ok=True)
        (self.root / "artifacts").mkdir(exist_ok=True)

    @property
    def plan_path(self) -> Path:
        return self.root / "PLAN.yaml"

    @property
    def check_report_path(self) -> Path:
        return self.root / "CHECK_REPORT.yaml"

    @property
    def project_log_path(self) -> Path:
        return self.root / "PROJECT_LOG.yaml"

    @property
    def report_path(self) -> Path:
        return self.root / "REPORT.md"

    def step_dir(self, step_id: str) -> Path:
        path = self.root / "steps" / step_id
        path.mkdir(parents=True, exist_ok=True)
        return path

    def write_plan(self, plan: dict) -> Path:
        plan = dict(plan)
        plan.setdefault("project_id", self.run_id)
        plan.setdefault("project_name", self.run_id)
        plan["run_id"] = self.run_id
        plan["plan_id"] = self.run_id
        plan["run_dir"] = self.root.as_posix()
        plan["project_dir"] = self.root.as_posix()
        return atomic_write_yaml(self.plan_path, plan, validator=validate_plan)

    def write_step_result(self, step_id: str, result: dict) -> Path:
        path = self.step_dir(step_id) / "step_result.yaml"
        path.write_text(yaml.safe_dump(result, sort_keys=False, allow_unicode=True), encoding="utf-8")
        return path

    def write_check_report(self, report: dict) -> Path:
        return atomic_write_yaml(self.check_report_path, report, validator=validate_check_report)

    def write_project_log(self, project_log: dict) -> Path:
        return atomic_write_yaml(self.project_log_path, project_log, validator=validate_project_log)
