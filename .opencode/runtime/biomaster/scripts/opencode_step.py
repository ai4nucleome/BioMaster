from __future__ import annotations

from pathlib import Path
import argparse
import json
from typing import Any

import yaml

from biomaster.knowledge import DEFAULT_DB_PATH, PROJECT_ROOT, connect, ensure_knowledge_db, ensure_schema
from biomaster.knowledge.prompt_assembler import assemble_prompt
from biomaster.knowledge.skill_finder import find_skills
from biomaster.knowledge.state_manager import advance_run_phase, create_run, get_run, update_run
from biomaster.runtime import RunContext, check_step, debug_step, execute_step, load_plan
from biomaster.runtime.run_context import find_matching_projects, resolve_project_dir
from biomaster.runtime.yaml_io import load_yaml_mapping, validate_check_report


def json_default(value: object) -> str:
    if isinstance(value, Path):
        return value.as_posix()
    return str(value)


def emit(value: dict[str, Any], *, as_yaml: bool = False) -> None:
    if as_yaml:
        print(yaml.safe_dump(value, sort_keys=False, allow_unicode=True))
    else:
        print(json.dumps(value, ensure_ascii=False, indent=2, default=json_default))


def project_root(project: str) -> Path:
    return resolve_project_dir(project)


def run_context(project: str) -> RunContext:
    return RunContext(project, root=project_root(project))


def load_project_plan(project: str) -> dict[str, Any]:
    plan_path = project_root(project) / "PLAN.yaml"
    if not plan_path.exists():
        raise FileNotFoundError(f"PLAN.yaml not found for project {project}: {plan_path}")
    return load_plan(plan_path)


def advance_project_phase(project: str, db_path: Path, next_phase: str) -> None:
    connection = connect(db_path)
    try:
        ensure_schema(connection)
        try:
            state = get_run(connection, project)
        except KeyError:
            return
        if str(state.get("phase") or "") != next_phase:
            advance_run_phase(
                connection,
                project,
                next_phase,
                project_dir=project_root(project),
            )
    finally:
        connection.close()


def ensure_pipeline_routing_state(project: str, db_path: Path) -> None:
    ensure_knowledge_db(db_path)
    connection = connect(db_path)
    try:
        ensure_schema(connection)
        try:
            get_run(connection, project)
        except KeyError:
            create_run(connection, run_id=project)
        for phase in ("mode_selection", "domain_anchoring", "pipeline_routing"):
            try:
                run = get_run(connection, project)
                if str(run.get("phase") or "") == phase:
                    continue
                update_run(connection, project, phase=phase)
            except ValueError:
                break
    finally:
        connection.close()


def command_route(args: argparse.Namespace) -> dict[str, Any]:
    if args.save_run_state:
        ensure_pipeline_routing_state(args.project, args.db)
    result = find_skills(
        args.request,
        args.agent,
        args.phase,
        run_id=args.project,
        db_path=args.db,
        include_optional=args.include_optional,
        save_run_state=args.save_run_state,
    )
    return {
        "command": "route",
        "project": args.project,
        "request": args.request,
        "result": result,
    }


def command_plan_context(args: argparse.Namespace) -> dict[str, Any]:
    if args.save_run_state:
        ensure_pipeline_routing_state(args.project, args.db)
    finder = find_skills(
        args.request,
        "biomaster-plan",
        "planning",
        run_id=args.project,
        db_path=args.db,
        include_optional=args.include_optional,
        save_run_state=args.save_run_state,
    )
    context = assemble_prompt(
        agent_name="biomaster-plan",
        phase="planning",
        selected_skill_ids=[str(item) for item in finder.get("selected_skill_ids", [])],
        run_id=args.project,
        db_path=args.db,
    )
    return {
        "command": "plan-context",
        "project": args.project,
        "request": args.request,
        "skill_finder": finder,
        "prompt_context": context,
    }


def command_execute_step(args: argparse.Namespace) -> dict[str, Any]:
    run = run_context(args.project)
    plan = load_project_plan(args.project)
    connection = connect(args.db)
    try:
        ensure_schema(connection)
        try:
            phase = str(get_run(connection, args.project).get("phase") or "")
        except KeyError:
            phase = ""
    finally:
        connection.close()
    if phase == "pipeline_routing":
        advance_project_phase(args.project, args.db, "planning")
        phase = "planning"
    if phase == "planning":
        advance_project_phase(args.project, args.db, "preflight")
    advance_project_phase(args.project, args.db, "execution")
    result = execute_step(run, plan, args.step_id, db_path=args.db)
    return {
        "command": "execute-step",
        "project": args.project,
        "step_id": args.step_id,
        "project_dir": run.root.as_posix(),
        "plan_path": run.plan_path.as_posix(),
        "result": result,
    }


def command_debug_step(args: argparse.Namespace) -> dict[str, Any]:
    run = run_context(args.project)
    plan = load_project_plan(args.project)
    advance_project_phase(args.project, args.db, "debugging")
    result = debug_step(run, plan, args.step_id, db_path=args.db)
    return {
        "command": "debug-step",
        "project": args.project,
        "step_id": args.step_id,
        "project_dir": run.root.as_posix(),
        "debug_result_path": (run.step_dir(args.step_id) / "debug_result.yaml").as_posix(),
        "result": result,
    }


def command_check_step(args: argparse.Namespace) -> dict[str, Any]:
    run = run_context(args.project)
    plan = load_project_plan(args.project)
    advance_project_phase(args.project, args.db, "checking")
    result = check_step(run, args.step_id, plan=plan, db_path=args.db)
    if result.get("status") == "fail":
        advance_project_phase(args.project, args.db, "debugging")
    else:
        report = load_yaml_mapping(run.check_report_path, validator=validate_check_report)
        passed = {
            str(item.get("step_id"))
            for item in report.get("checks", [])
            if item.get("status") == "pass"
        }
        if all(str(step["step_id"]) in passed for step in plan.get("steps", [])):
            advance_project_phase(args.project, args.db, "reporting")
            advance_project_phase(args.project, args.db, "done")
    return {
        "command": "check-step",
        "project": args.project,
        "step_id": args.step_id,
        "project_dir": run.root.as_posix(),
        "check_report_path": run.check_report_path.as_posix(),
        "project_log_path": run.project_log_path.as_posix(),
        "report_path": run.report_path.as_posix(),
        "opencode_view_path": (run.root / "OPENCODE_VIEW.md").as_posix(),
        "result": result,
    }


def command_status(args: argparse.Namespace) -> dict[str, Any]:
    root = project_root(args.project)
    plan = yaml.safe_load((root / "PLAN.yaml").read_text(encoding="utf-8")) if (root / "PLAN.yaml").exists() else {}
    project_log = (
        yaml.safe_load((root / "PROJECT_LOG.yaml").read_text(encoding="utf-8"))
        if (root / "PROJECT_LOG.yaml").exists()
        else {}
    )
    check_report = (
        yaml.safe_load((root / "CHECK_REPORT.yaml").read_text(encoding="utf-8"))
        if (root / "CHECK_REPORT.yaml").exists()
        else {}
    )
    steps = plan.get("steps") if isinstance(plan, dict) else []
    logged_steps = project_log.get("steps") if isinstance(project_log, dict) else []
    return {
        "command": "status",
        "project": args.project,
        "project_dir": root.as_posix(),
        "exists": root.exists(),
        "plan_path": (root / "PLAN.yaml").as_posix(),
        "has_plan": bool(plan),
        "total_steps": len(steps) if isinstance(steps, list) else 0,
        "logged_steps": len(logged_steps) if isinstance(logged_steps, list) else 0,
        "overall_status": check_report.get("overall_status", "") if isinstance(check_report, dict) else "",
        "report_path": (root / "REPORT.md").as_posix(),
        "opencode_view_path": (root / "OPENCODE_VIEW.md").as_posix(),
    }


def command_projects(args: argparse.Namespace) -> dict[str, Any]:
    matches = find_matching_projects(dataset=args.dataset, goal=args.goal, analysis_type=args.analysis_type)
    return {
        "command": "projects",
        "projects_root": (PROJECT_ROOT / "projects").as_posix(),
        "matches": matches,
    }


def add_common(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--db", type=Path, default=DEFAULT_DB_PATH)
    parser.add_argument("--yaml", action="store_true", help="Emit YAML instead of JSON.")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="OpenCode bridge for deterministic BioMaster runtime actions.")
    sub = parser.add_subparsers(dest="command", required=True)

    route = sub.add_parser("route", help="Run SQLite Skill Finder for a user request.")
    add_common(route)
    route.add_argument("--project", required=True)
    route.add_argument("--request", required=True)
    route.add_argument("--agent", default="biomaster-plan")
    route.add_argument("--phase", default="planning")
    route.add_argument("--include-optional", action="store_true")
    route.add_argument("--save-run-state", action="store_true")
    route.set_defaults(func=command_route)

    plan_context = sub.add_parser("plan-context", help="Run Skill Finder and assemble planning prompt context.")
    add_common(plan_context)
    plan_context.add_argument("--project", required=True)
    plan_context.add_argument("--request", required=True)
    plan_context.add_argument("--include-optional", action="store_true")
    plan_context.add_argument("--save-run-state", action="store_true")
    plan_context.set_defaults(func=command_plan_context)

    execute = sub.add_parser("execute-step", help="Execute one canonical PLAN step through Python runtime.")
    add_common(execute)
    execute.add_argument("--project", required=True)
    execute.add_argument("--step-id", required=True)
    execute.set_defaults(func=command_execute_step)

    debug = sub.add_parser("debug-step", help="Debug one canonical PLAN step through Python runtime.")
    add_common(debug)
    debug.add_argument("--project", required=True)
    debug.add_argument("--step-id", required=True)
    debug.set_defaults(func=command_debug_step)

    check = sub.add_parser("check-step", help="Check one canonical PLAN step through Python runtime.")
    add_common(check)
    check.add_argument("--project", required=True)
    check.add_argument("--step-id", required=True)
    check.set_defaults(func=command_check_step)

    status = sub.add_parser("status", help="Summarize one BioMaster project directory.")
    add_common(status)
    status.add_argument("--project", required=True)
    status.set_defaults(func=command_status)

    projects = sub.add_parser("projects", help="List candidate BioMaster project directories.")
    add_common(projects)
    projects.add_argument("--dataset")
    projects.add_argument("--goal")
    projects.add_argument("--analysis-type")
    projects.set_defaults(func=command_projects)
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    try:
        emit(args.func(args), as_yaml=args.yaml)
    except Exception as exc:
        emit({"error": str(exc), "command": args.command}, as_yaml=args.yaml)
        raise SystemExit(1) from exc


if __name__ == "__main__":
    main()
