from __future__ import annotations

from pathlib import Path
import argparse
import json
import re
from datetime import datetime, timezone

from biomaster.knowledge import (
    DEFAULT_DB_PATH,
    PROJECT_ROOT,
    REQUIRED_TABLES,
    connect,
    ensure_schema,
    json_dumps,
    json_loads,
    row_to_dict,
    table_exists,
)
from biomaster.knowledge.phases import validate_phase_transition


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def slugify_project_name(value: str | None, *, default: str = "biomaster-project") -> str:
    raw = (value or default).strip().lower()
    slug = re.sub(r"[^a-z0-9]+", "-", raw).strip("-")
    return slug or default


def new_run_id(connection=None) -> str:
    used: set[str] = set()
    if connection is not None:
        rows = connection.execute("SELECT run_id FROM run_states").fetchall()
        for row in rows:
            used.add(str(row["run_id"]))
    projects_root = PROJECT_ROOT / "projects"
    projects_root.mkdir(parents=True, exist_ok=True)
    existing_projects = {path.name for path in projects_root.iterdir() if path.is_dir()}
    candidate = "biomaster-project"
    if candidate in existing_projects:
        index = 2
        while f"biomaster-project-{index:03d}" in existing_projects:
            index += 1
        candidate = f"biomaster-project-{index:03d}"
    if candidate not in used:
        return candidate
    index = 2
    while f"biomaster-project-{index:03d}" in used:
        index += 1
    return f"biomaster-project-{index:03d}"


def create_run(
    connection,
    *,
    run_id: str | None = None,
    phase: str = "init",
    mode: str | None = None,
    domain: str | None = None,
    discipline: str | None = None,
    pipeline: str | None = None,
    selected_route_id: str | None = None,
    selected_skill_ids: list[str] | None = None,
    disabled_skill_ids: list[str] | None = None,
    state_json: dict | None = None,
) -> dict:
    run_id = slugify_project_name(run_id or new_run_id(connection))
    if selected_route_id:
        raise ValueError("selected_route_id must come from SQLite Skill Finder after pipeline_routing, not create_run")
    errors = validate_phase_transition(None, phase)
    if errors:
        raise ValueError("; ".join(errors))
    now = utc_now()
    connection.execute(
        """
        INSERT INTO run_states (
          run_id, phase, mode, domain, discipline, pipeline, selected_route_id,
          selected_skill_ids, disabled_skill_ids, state_json, created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            run_id,
            phase,
            mode,
            domain,
            discipline,
            pipeline,
            selected_route_id,
            json_dumps(selected_skill_ids or []),
            json_dumps(disabled_skill_ids or []),
            json_dumps(state_json or {}),
            now,
            now,
        ),
    )
    connection.commit()
    return get_run(connection, run_id)


def get_run(connection, run_id: str) -> dict:
    row = connection.execute("SELECT * FROM run_states WHERE run_id = ?", (run_id,)).fetchone()
    if row is None:
        raise KeyError(f"unknown run: {run_id}")
    return row_to_dict(row)


def _assert_sqlite_ready(connection) -> None:
    integrity = connection.execute("PRAGMA quick_check").fetchone()
    if integrity is None or str(integrity[0]).lower() != "ok":
        raise ValueError("SQLite readiness check failed: database integrity check did not pass")
    missing_tables = [table for table in REQUIRED_TABLES if not table_exists(connection, table)]
    if missing_tables:
        raise ValueError("SQLite readiness check failed: missing tables: " + ", ".join(missing_tables))
    for table in ("skills", "pipeline_routes"):
        count = int(connection.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0])
        if count == 0:
            raise ValueError(f"SQLite readiness check failed: {table} is empty")


def _assert_checks_passed(run_id: str, project_dir: Path) -> None:
    from biomaster.runtime.yaml_io import load_yaml_mapping, validate_check_report, validate_plan

    if not (project_dir / "PLAN.yaml").exists():
        raise ValueError("cannot enter reporting or done without PLAN.yaml")
    if not (project_dir / "CHECK_REPORT.yaml").exists():
        raise ValueError("cannot enter reporting or done without CHECK_REPORT.yaml")
    plan = load_yaml_mapping(project_dir / "PLAN.yaml", validator=validate_plan)
    report = load_yaml_mapping(project_dir / "CHECK_REPORT.yaml", validator=validate_check_report)
    if report.get("run_id", run_id) != run_id or report.get("overall_status") != "pass":
        raise ValueError("cannot enter reporting or done while checking has not passed")
    required_steps = [str(step["step_id"]) for step in plan["steps"]]
    passed_steps = {
        str(check.get("step_id"))
        for check in report["checks"]
        if check.get("status") == "pass"
    }
    missing = [step_id for step_id in required_steps if step_id not in passed_steps]
    if missing:
        raise ValueError("cannot enter reporting or done before all checks pass: " + ", ".join(missing))


def _validate_phase_readiness(
    connection,
    run_id: str,
    current: dict,
    next_phase: str,
    project_dir: Path,
) -> None:
    previous_phase = str(current.get("phase") or "")
    if previous_phase == "domain_anchoring" and next_phase == "pipeline_routing":
        _assert_sqlite_ready(connection)
    if previous_phase == "pipeline_routing" and next_phase == "planning":
        if not current.get("selected_route_id"):
            raise ValueError("cannot enter planning before SQLite pipeline routing selects a route")
    if next_phase in {"reporting", "done"}:
        _assert_checks_passed(run_id, project_dir)


def update_run(
    connection,
    run_id: str,
    *,
    project_dir: Path | None = None,
    **fields: object,
) -> dict:
    allowed = {
        "phase",
        "mode",
        "domain",
        "discipline",
        "pipeline",
        "selected_route_id",
        "selected_skill_ids",
        "disabled_skill_ids",
        "state_json",
    }
    current = get_run(connection, run_id)
    updates: dict[str, object] = {}
    for key, value in fields.items():
        if key not in allowed:
            raise ValueError(f"unsupported run field: {key}")
        if key == "phase":
            errors = validate_phase_transition(str(current.get("phase") or ""), str(value))
            if errors:
                raise ValueError("; ".join(errors))
            _validate_phase_readiness(
                connection,
                run_id,
                current,
                str(value),
                project_dir or PROJECT_ROOT / "projects" / run_id,
            )
        if key == "selected_route_id":
            phase = str(current.get("phase") or "")
            if phase not in {"pipeline_routing", "planning"}:
                raise ValueError("selected_route_id can only be set after SQLite pipeline_routing")
        if key in {"selected_skill_ids", "disabled_skill_ids", "state_json"}:
            updates[key] = json_dumps(value)
        else:
            updates[key] = value

    if not updates:
        return get_run(connection, run_id)

    set_clause = ", ".join(f"{key} = ?" for key in updates)
    params = list(updates.values()) + [utc_now(), run_id]
    connection.execute(
        f"UPDATE run_states SET {set_clause}, updated_at = ? WHERE run_id = ?",
        params,
    )
    connection.commit()
    return get_run(connection, run_id)


def advance_run_phase(
    connection,
    run_id: str,
    next_phase: str,
    *,
    project_dir: Path | None = None,
) -> dict:
    """Advance one legal phase after all runtime readiness gates pass."""

    return update_run(
        connection,
        run_id,
        project_dir=project_dir,
        phase=next_phase,
    )


def get_disabled_skill_ids(connection, run_id: str | None) -> set[str]:
    if not run_id:
        return set()
    try:
        run = get_run(connection, run_id)
    except KeyError:
        return set()
    return set(json_loads(run.get("disabled_skill_ids"), []))


def disable_skills(connection, run_id: str, skill_ids: list[str]) -> dict:
    run = get_run(connection, run_id)
    disabled = list(dict.fromkeys([*json_loads(run.get("disabled_skill_ids"), []), *skill_ids]))
    return update_run(connection, run_id, disabled_skill_ids=disabled)


def select_skills(connection, run_id: str, skill_ids: list[str]) -> dict:
    return update_run(connection, run_id, selected_skill_ids=list(dict.fromkeys(skill_ids)))


def main() -> None:
    parser = argparse.ArgumentParser(description="Manage BioMaster run state in SQLite.")
    parser.add_argument("--db", type=Path, default=DEFAULT_DB_PATH)
    parser.add_argument("--create-run", action="store_true")
    parser.add_argument("--run-id")
    parser.add_argument("--phase")
    parser.add_argument("--mode")
    parser.add_argument("--route-id")
    parser.add_argument("--selected-skills")
    parser.add_argument("--disable-skills")
    parser.add_argument("--show-run", action="store_true")
    args = parser.parse_args()

    connection = connect(args.db)
    try:
        ensure_schema(connection)

        if args.route_id:
            raise SystemExit("--route-id is disabled; use skill_finder.py --save-run-state after SQLite pipeline_routing")

        if args.create_run:
            run = create_run(
                connection,
                run_id=args.run_id,
                phase=args.phase or "init",
                mode=args.mode,
            )
            print(json.dumps(run, ensure_ascii=False, indent=2))
            return

        if not args.run_id:
            raise SystemExit("--run-id is required unless --create-run is used")

        if args.disable_skills:
            skill_ids = [item.strip() for item in args.disable_skills.split(",") if item.strip()]
            run = disable_skills(connection, args.run_id, skill_ids)
            print(json.dumps(run, ensure_ascii=False, indent=2))
            return

        if args.selected_skills:
            skill_ids = [item.strip() for item in args.selected_skills.split(",") if item.strip()]
            run = select_skills(connection, args.run_id, skill_ids)
            print(json.dumps(run, ensure_ascii=False, indent=2))
            return

        if args.show_run or args.phase:
            updates = {}
            if args.phase:
                updates["phase"] = args.phase
            run = update_run(connection, args.run_id, **updates) if updates else get_run(connection, args.run_id)
            print(json.dumps(run, ensure_ascii=False, indent=2))
            return

        parser.print_help()
    finally:
        connection.close()


if __name__ == "__main__":
    main()
