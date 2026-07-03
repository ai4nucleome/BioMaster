from __future__ import annotations

from pathlib import Path
import yaml

from biomaster.knowledge import DEFAULT_DB_PATH, connect, ensure_schema, normalize_agent_name
from biomaster.knowledge.query_skills import agent_allowed, get_skill_by_id
from biomaster.runtime.run_context import RunContext


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


def _is_file_like(expected_output: str) -> bool:
    value = expected_output.strip()
    return "/" in value or "." in Path(value).name or value.endswith("/")


def _expected_output_exists(run: RunContext, step_id: str, expected_output: str) -> bool:
    value = expected_output.strip()
    if not _is_file_like(value):
        return (run.step_dir(step_id) / "step_result.yaml").exists() or (run.step_dir(step_id) / "execution_log.txt").exists()
    return any(
        path.exists()
        for path in (
            run.root / value,
            run.step_dir(step_id) / value,
        )
    )


def query_sqlite_debug_context(skill_ids: list[str], db_path: Path = DEFAULT_DB_PATH) -> dict:
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
            if not skill.get("enabled") or not agent_allowed(skill, normalize_agent_name("biomaster-debug")):
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
            "queried_skill_ids": skill_ids,
            "resolved_skill_ids": resolved,
            "missing_skill_ids": missing,
            "rejected_skill_ids": rejected,
        }
    finally:
        connection.close()


def debug_step(run: RunContext, plan: dict, step_id: str, *, db_path: Path = DEFAULT_DB_PATH) -> dict:
    step = next((item for item in plan.get("steps", []) if item.get("step_id") == step_id), None)
    if step is None:
        raise KeyError(f"unknown step_id: {step_id}")

    step_result_path = run.step_dir(step_id) / "step_result.yaml"
    step_result = _read_yaml(step_result_path)
    missing_outputs = [
        expected
        for expected in _as_list(step.get("expected_outputs"))
        if not _expected_output_exists(run, step_id, expected)
    ]
    execution_failures: list[str] = []
    if not step_result_path.exists():
        execution_failures.append("missing step_result.yaml")
    elif step_result.get("status") != "completed":
        execution_failures.append(f"step_result status is {step_result.get('status')}")
    if missing_outputs:
        execution_failures.append("missing expected outputs: " + ", ".join(missing_outputs))

    debug_skill_ids = ["debug-missing-files"] if execution_failures else []
    context_skill_ids = list(
        dict.fromkeys(
            [
                *debug_skill_ids,
                *_as_list(step.get("required_execute_skills")),
                *_as_list(step.get("required_report_skills")),
                *_as_list(step.get("required_verify_skills")),
                "env-python-scrnaseq",
            ]
        )
    )
    sqlite_debug_query = query_sqlite_debug_context(context_skill_ids, db_path=db_path)
    query_failed = sqlite_debug_query["missing_skill_ids"] or sqlite_debug_query["rejected_skill_ids"]
    failures = [*execution_failures]
    if query_failed:
        failures.append("debug SQLite context lookup failed")

    result = {
        "run_id": run.run_id,
        "plan_id": plan.get("plan_id", run.run_id),
        "step_id": step_id,
        "status": "fail" if failures else "pass",
        "failure_type": "execution_output_missing" if missing_outputs else ("execution_error" if failures else ""),
        "diagnosis": "; ".join(failures),
        "sqlite_debug_query": sqlite_debug_query,
        "used_debug_skills": debug_skill_ids,
        "missing_outputs": missing_outputs,
        "proposed_fix": "generate real outputs for missing expected files before Check" if failures else "",
        "requires_user_approval": False,
        "next_action": "retry_execute" if failures else "check",
        "retry_plan": {
            "step_id": step_id,
            "expected_outputs": _as_list(step.get("expected_outputs")),
            "verify_skills": _as_list(step.get("required_verify_skills")),
        },
    }
    path = run.step_dir(step_id) / "debug_result.yaml"
    path.write_text(yaml.safe_dump(result, sort_keys=False, allow_unicode=True), encoding="utf-8")
    return result
