from __future__ import annotations

from pathlib import Path
import yaml

from biomaster.knowledge import DEFAULT_DB_PATH, connect, ensure_knowledge_db, ensure_schema, normalize_agent_name
from biomaster.knowledge.query_skills import agent_allowed, get_skill_by_id
from biomaster.runtime.run_context import RunContext, utc_now
from biomaster.runtime.yaml_io import (
    load_yaml_mapping,
    validate_check_report,
    validate_project_log,
)


def _as_list(value: object) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item) for item in value]
    return [str(value)]


def _read_yaml(path: Path) -> dict:
    if not path.exists():
        return {}
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return data if isinstance(data, dict) else {}


def query_sqlite_verify_skills(skill_ids: list[str], db_path: Path = DEFAULT_DB_PATH) -> dict:
    sqlite_readiness = ensure_knowledge_db(db_path)
    connection = connect(db_path)
    try:
        ensure_schema(connection)
        resolved: list[dict[str, str]] = []
        missing: list[str] = []
        rejected: list[str] = []
        for skill_id in skill_ids:
            skill = get_skill_by_id(connection, skill_id)
            if skill is None:
                missing.append(skill_id)
                continue
            if not skill.get("enabled") or not agent_allowed(skill, normalize_agent_name("biomaster-check")):
                rejected.append(skill_id)
                continue
            resolved.append(
                {
                    "skill_id": str(skill["skill_id"]),
                    "layer": str(skill.get("layer") or ""),
                    "path": str(skill["path"]),
                    "content_hash": str(skill.get("content_hash") or ""),
                }
            )

        return {
            "db_path": str(db_path),
            "sqlite_readiness": sqlite_readiness,
            "queried_skill_ids": skill_ids,
            "resolved_skill_ids": resolved,
            "missing_skill_ids": missing,
            "rejected_skill_ids": rejected,
        }
    finally:
        connection.close()


def _candidate_paths(run: RunContext, step_id: str, expected_output: str) -> list[Path]:
    value = expected_output.strip()
    candidates = [
        run.root / value,
        run.step_dir(step_id) / value,
    ]
    return candidates


def _is_file_like(expected_output: str) -> bool:
    value = expected_output.strip()
    return "/" in value or "." in Path(value).name or value.endswith("/")


def _check_expected_output(run: RunContext, step_id: str, expected_output: str) -> dict:
    value = expected_output.strip()
    if not _is_file_like(value):
        evidence = [
            run.step_dir(step_id) / "step_result.yaml",
            run.step_dir(step_id) / "execution_log.txt",
        ]
        found = [path for path in evidence if path.exists()]
        return {
            "expected_output": value,
            "status": "pass" if found else "fail",
            "evidence": [str(path) for path in found],
            "reason": "" if found else "no step summary or execution log found for abstract expected output",
        }

    candidates = _candidate_paths(run, step_id, value)
    found = [path for path in candidates if path.exists()]
    return {
        "expected_output": value,
        "status": "pass" if found else "fail",
        "evidence": [str(path) for path in found],
        "reason": "" if found else f"missing expected output: {value}",
    }


def _load_existing_report(run: RunContext) -> dict:
    if not run.check_report_path.exists():
        return {"run_id": run.run_id, "plan_id": run.run_id, "overall_status": "pass", "checks": []}
    data = load_yaml_mapping(run.check_report_path, validator=validate_check_report)
    data.setdefault("run_id", run.run_id)
    data.setdefault("plan_id", run.run_id)
    data.setdefault("checks", [])
    return data


def _load_project_log(run: RunContext) -> dict:
    if run.project_log_path.exists():
        data = load_yaml_mapping(run.project_log_path, validator=validate_project_log)
    else:
        data = {}
    data.setdefault("project_name", run.run_id)
    data.setdefault("project_dir", str(run.root))
    data.setdefault("created_at", utc_now())
    data.setdefault("schema_version", 2)
    data.setdefault("steps", [])
    return data


def _status_summary(status: str | None, reason: str | None) -> str:
    if status == "pass":
        return "Step passed artifact review; expected outputs and verification gates are satisfied."
    detail = reason or "artifact review failed"
    return f"Step failed artifact review: {detail}"


def _artifact_inventory(step_result: dict) -> list[dict[str, str]]:
    artifacts: list[dict[str, str]] = []
    for artifact in step_result.get("artifacts") or []:
        path = Path(str(artifact))
        artifacts.append(
            {
                "path": str(path),
                "name": path.name,
                "suffix": path.suffix,
                "kind": "directory" if path.is_dir() else "file",
                "exists": str(path.exists()),
            }
        )
    return artifacts


def append_project_log(run: RunContext, plan: dict | None, check_result: dict) -> dict:
    step_id = str(check_result.get("step_id"))
    step = next((item for item in (plan or {}).get("steps", []) if str(item.get("step_id")) == step_id), {})
    step_result = _read_yaml(run.step_dir(step_id) / "step_result.yaml")
    now = utc_now()
    project_log = _load_project_log(run)
    entries = [item for item in project_log.get("steps", []) if str(item.get("step_id")) != step_id]
    reviewed_outputs = [
        {
            "expected_output": item.get("expected_output"),
            "status": item.get("status"),
            "evidence": item.get("evidence", []),
            "reason": item.get("reason", ""),
        }
        for item in check_result.get("output_checks", [])
    ]
    status = str(check_result.get("status") or "")
    reason = str(check_result.get("reason") or "")
    entries.append(
        {
            "step_id": step_id,
            "objective": step.get("objective", ""),
            "summary": _status_summary(status, reason),
            "created_or_updated_by": "biomaster-check",
            "updated_at": now,
            "plan_context": {
                "analysis_type": (plan or {}).get("analysis_type", ""),
                "dataset": (plan or {}).get("dataset", ""),
                "mode": (plan or {}).get("mode", ""),
                "selected_route_id": (plan or {}).get("selected_route_id", ""),
                "expected_outputs": _as_list(step.get("expected_outputs")),
                "acceptance_criteria": _as_list(step.get("acceptance_criteria")),
                "required_execute_skills": _as_list(step.get("required_execute_skills")),
                "required_verify_skills": _as_list(step.get("required_verify_skills")),
            },
            "skill_evidence": {
                "verify_skill_query": check_result.get("verify_skill_query", {}),
                "execute_skills": step_result.get("execute_skills", []),
                "sqlite_execute_query": step_result.get("sqlite_skill_query", {}),
            },
            "script": check_result.get("script_path") or step_result.get("script_path") or str(run.root / "scripts" / step_id / "run.sh"),
            "execution": {
                "status": step_result.get("execution_status") or step_result.get("status", ""),
                "exit_code": step_result.get("exit_code"),
                "stdout": step_result.get("stdout_path", ""),
                "stderr": step_result.get("stderr_path", ""),
                "step_result": str(run.step_dir(step_id) / "step_result.yaml"),
                "error_message": step_result.get("error_message", ""),
                "result_dir": step_result.get("result_dir", str(run.step_dir(step_id))),
            },
            "check": {
                "status": status,
                "failed_check": check_result.get("failed_check", ""),
                "evidence": check_result.get("step_result_path", ""),
                "reviewed_outputs": reviewed_outputs,
                "conclusion": reason or "passed",
                "missing_outputs": [
                    item.get("expected_output")
                    for item in reviewed_outputs
                    if item.get("status") == "fail"
                ],
            },
            "artifacts": _artifact_inventory(step_result),
            "report_notes": _status_summary(status, reason),
            "next_action": "continue" if status == "pass" else "retry_current_step",
            "include_in_report": status == "pass",
        }
    )
    project_log["updated_at"] = now
    project_log["plan_id"] = (plan or {}).get("plan_id", run.run_id)
    project_log["dataset"] = (plan or {}).get("dataset", project_log.get("dataset", ""))
    project_log["analysis_type"] = (plan or {}).get("analysis_type", project_log.get("analysis_type", ""))
    project_log["selected_route_id"] = (plan or {}).get("selected_route_id", project_log.get("selected_route_id", ""))
    project_log["steps"] = sorted(entries, key=lambda item: str(item.get("step_id", "")))
    run.write_project_log(project_log)
    return project_log


def _write_report_with_check(run: RunContext, result: dict) -> None:
    report = _load_existing_report(run)
    checks = [item for item in report.get("checks", []) if item.get("step_id") != result["step_id"]]
    checks.append(result)
    report["checks"] = checks
    report["overall_status"] = "fail" if any(item.get("status") == "fail" for item in checks) else "pass"
    run.write_check_report(report)
    from biomaster.runtime.reporter import write_report_from_project_log

    if run.project_log_path.exists():
        write_report_from_project_log(run)


def check_step(
    run: RunContext,
    step_id: str,
    *,
    plan: dict | None = None,
    db_path: Path = DEFAULT_DB_PATH,
    status: str | None = None,
    failed_check: str = "",
) -> dict:
    if plan is None:
        result = {
            "step_id": step_id,
            "status": status or "pass",
            "failed_check": failed_check,
            "reason": "" if (status or "pass") == "pass" else failed_check,
            "suggested_debug_skills": [] if (status or "pass") == "pass" else ["debug-missing-files"],
            "next_action": "continue" if (status or "pass") == "pass" else "debug",
        }
        _write_report_with_check(run, result)
        append_project_log(run, None, result)
        return result

    step = next((item for item in plan.get("steps", []) if item.get("step_id") == step_id), None)
    if step is None:
        raise KeyError(f"unknown step_id: {step_id}")

    step_dir = run.step_dir(step_id)
    step_result_path = step_dir / "step_result.yaml"
    script_path = run.root / "scripts" / step_id / "run.sh"
    step_result = _read_yaml(step_result_path)
    verify_skill_query = query_sqlite_verify_skills(_as_list(step.get("required_verify_skills")), db_path=db_path)
    output_checks = [_check_expected_output(run, step_id, expected) for expected in _as_list(step.get("expected_outputs"))]

    failures: list[str] = []
    if not step_result_path.exists():
        failures.append("missing step_result.yaml")
    elif step_result.get("status") != "completed":
        failures.append(f"step_result status is {step_result.get('status')}")

    if not script_path.exists() and step.get("required_execute_skills"):
        failures.append("missing generated run.sh")

    if verify_skill_query["missing_skill_ids"] or verify_skill_query["rejected_skill_ids"]:
        failures.append("verify skill lookup failed")

    for output_check in output_checks:
        if output_check["status"] == "fail":
            failures.append(output_check["reason"])

    result = {
        "step_id": step_id,
        "status": "fail" if failures else "pass",
        "failed_check": "output_contract" if failures else "",
        "reason": "; ".join(failures),
        "expected_outputs": _as_list(step.get("expected_outputs")),
        "output_checks": output_checks,
        "verify_skill_query": verify_skill_query,
        "step_result_path": str(step_result_path),
        "script_path": str(script_path),
        "suggested_debug_skills": ["debug-missing-files"] if failures else [],
        "next_action": "debug" if failures else "continue",
    }
    append_project_log(run, plan, result)
    _write_report_with_check(run, result)
    from biomaster.runtime.opencode_view import write_opencode_view

    write_opencode_view(run, plan)
    return result


def check_run(run: RunContext, plan: dict, *, db_path: Path = DEFAULT_DB_PATH) -> dict:
    checks = [check_step(run, str(step["step_id"]), plan=plan, db_path=db_path) for step in plan.get("steps", [])]
    report = {
        "run_id": run.run_id,
        "plan_id": plan.get("plan_id", run.run_id),
        "overall_status": "fail" if any(item["status"] == "fail" for item in checks) else "pass",
        "checks": checks,
    }
    run.write_check_report(report)
    from biomaster.runtime.reporter import write_report_from_project_log

    write_report_from_project_log(run)
    from biomaster.runtime.opencode_view import write_opencode_view

    write_opencode_view(run, plan)
    return report
