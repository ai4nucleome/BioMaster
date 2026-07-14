from __future__ import annotations

from pathlib import Path
import yaml

from biomaster.knowledge import DEFAULT_DB_PATH, connect, ensure_knowledge_db, ensure_schema, normalize_agent_name
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


def query_sqlite_debug_context(skill_ids: list[str], db_path: Path = DEFAULT_DB_PATH) -> dict:
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
            layer = str(skill.get("layer") or "")
            agent = "biomaster-plan" if layer == "report" else "biomaster-debug"
            if not skill.get("enabled") or not agent_allowed(skill, normalize_agent_name(agent)):
                rejected.append(skill_id)
                continue
            resolved.append(
                {
                    "skill_id": str(skill["skill_id"]),
                    "layer": layer,
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


def debug_step(run: RunContext, plan: dict, step_id: str, *, db_path: Path = DEFAULT_DB_PATH) -> dict:
    step = next((item for item in plan.get("steps", []) if item.get("step_id") == step_id), None)
    if step is None:
        raise KeyError(f"unknown step_id: {step_id}")

    step_result_path = run.step_dir(step_id) / "step_result.yaml"
    step_result = _read_yaml(step_result_path)
    execution_failures: list[str] = []
    exit_code = step_result.get("exit_code")
    execution_status = str(step_result.get("execution_status") or "")
    stderr_path = Path(str(step_result.get("stderr_path") or run.step_dir(step_id) / "stderr.log"))
    stdout_path = Path(str(step_result.get("stdout_path") or run.step_dir(step_id) / "stdout.log"))
    script_path = Path(str(step_result.get("script_path") or run.root / "scripts" / step_id / "run.sh"))

    if not step_result_path.exists():
        execution_failures.append("missing step_result.yaml")
    elif execution_status != "success" or exit_code not in (0, "0"):
        execution_failures.append(
            f"script execution failed: execution_status={execution_status or step_result.get('status')}, exit_code={exit_code}"
        )
    if step_result_path.exists() and not script_path.exists():
        execution_failures.append("missing generated script")
    stderr_text = stderr_path.read_text(encoding="utf-8") if stderr_path.exists() else ""
    if execution_failures and stderr_text.strip():
        execution_failures.append("stderr: " + stderr_text.strip().splitlines()[-1])

    debug_skill_ids = ["debug-missing-files"] if execution_failures else []
    context_skill_ids = list(
        dict.fromkeys(
            [
                *debug_skill_ids,
                *_as_list(step.get("required_execute_skills")),
                *_as_list(step.get("required_report_skills")),
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
        "execution_status": "failed" if failures else "success",
        "exit_code": exit_code if exit_code is not None else (1 if failures else 0),
        "failure_type": "execution_error" if failures else "",
        "error_summary": "; ".join(failures),
        "diagnosis": "; ".join(failures),
        "evidence": {
            "script_path": str(script_path),
            "stdout_path": str(stdout_path),
            "stderr_path": str(stderr_path),
            "step_result_path": str(step_result_path),
        },
        "sqlite_debug_query": sqlite_debug_query,
        "used_debug_skills": debug_skill_ids,
        "suggested_fix": "review stderr/stdout and regenerate the step script in Execute" if failures else "",
        "proposed_fix": "review stderr/stdout and regenerate the step script in Execute" if failures else "",
        "requires_user_approval": False,
        "retry_required": bool(failures),
        "next_action": "retry_execute" if failures else "check",
        "retry_plan": {
            "step_id": step_id,
            "suggested_fix": "review stderr/stdout and regenerate the step script in Execute" if failures else "",
        },
    }
    path = run.step_dir(step_id) / "debug_result.yaml"
    path.write_text(yaml.safe_dump(result, sort_keys=False, allow_unicode=True), encoding="utf-8")
    return result
