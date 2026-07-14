from __future__ import annotations

from pathlib import Path
from typing import Any

from biomaster.a2a.message import A2AMessage


AGENT_ALIASES = {
    "intake-agent": "biomaster-plan",
    "plan-agent": "biomaster-plan",
    "execute-agent": "biomaster-execute",
    "task-agent": "biomaster-execute",
    "check-agent": "biomaster-check",
    "verify-agent": "biomaster-check",
    "debug-agent": "biomaster-debug",
}

VALID_MESSAGE_TYPES = {
    "intake_request",
    "planning_request",
    "execution_request",
    "check_request",
    "check_result",
    "debug_request",
    "debug_result",
    "final_report_request",
}

VALID_TRANSITIONS: dict[str, set[str]] = {
    "intake_request": {"planning_request"},
    "planning_request": {"execution_request"},
    "execution_request": {"debug_request"},
    "debug_result": {"execution_request", "check_request"},
    "check_request": {"check_result"},
    "check_result": {"debug_request", "execution_request", "final_report_request"},
    "debug_request": {"debug_result"},
    "final_report_request": set(),
}


def normalize_agent(agent: str) -> str:
    return AGENT_ALIASES.get(agent, agent)


def build_message(
    message_type: str,
    *,
    from_agent: str,
    to_agent: str,
    run_id: str,
    phase: str,
    payload: dict[str, Any] | None = None,
    required_outputs: list[str] | None = None,
) -> A2AMessage:
    if message_type not in VALID_MESSAGE_TYPES:
        raise ValueError(f"unknown message_type: {message_type}")
    return A2AMessage(
        message_type=message_type,
        from_agent=normalize_agent(from_agent),
        to_agent=normalize_agent(to_agent),
        run_id=run_id,
        phase=phase,
        payload=payload or {},
        required_outputs=required_outputs or [],
    )


def intake_request(
    run_id: str,
    *,
    user_goal: str,
    mode: str | None = None,
) -> A2AMessage:
    payload: dict[str, Any] = {"user_goal": user_goal}
    if mode:
        payload["mode"] = mode
    return build_message(
        "intake_request",
        from_agent="biomaster-plan",
        to_agent="biomaster-plan",
        run_id=run_id,
        phase="mode_selection",
        payload=payload,
        required_outputs=["mode", "domain", "discipline"],
    )


def planning_request_from_intake(
    run_id: str,
    *,
    mode: str,
    domain: str,
    discipline: str,
    pipeline: str,
    dataset: str,
    user_goal: str,
) -> A2AMessage:
    return build_message(
        "planning_request",
        from_agent="biomaster-plan",
        to_agent="biomaster-plan",
        run_id=run_id,
        phase="planning",
        payload={
            "mode": mode,
            "domain": domain,
            "discipline": discipline,
            "pipeline": pipeline,
            "dataset": dataset,
            "user_goal": user_goal,
        },
        required_outputs=["PLAN.yaml"],
    )


def execution_request(
    run_id: str,
    *,
    plan_path: str,
    start_step: str,
) -> A2AMessage:
    return build_message(
        "execution_request",
        from_agent="biomaster-plan",
        to_agent="biomaster-execute",
        run_id=run_id,
        phase="execution",
        payload={"plan_path": plan_path, "start_step": start_step},
        required_outputs=["step_result.yaml", "execution_log"],
    )


def check_request(
    run_id: str,
    *,
    step_id: str,
    plan_path: str,
) -> A2AMessage:
    return build_message(
        "check_request",
        from_agent="biomaster-debug",
        to_agent="biomaster-check",
        run_id=run_id,
        phase="checking",
        payload={"step_id": step_id, "plan_path": plan_path},
        required_outputs=["check_result.yaml"],
    )


def debug_request_message(
    run_id: str,
    *,
    step_id: str,
    failed_check: str,
    suggested_debug_skills: list[str] | None = None,
    from_agent: str = "biomaster-check",
) -> A2AMessage:
    return build_message(
        "debug_request",
        from_agent=from_agent,
        to_agent="biomaster-debug",
        run_id=run_id,
        phase="debugging",
        payload={
            "step_id": step_id,
            "failed_check": failed_check,
            "suggested_debug_skills": suggested_debug_skills or [],
        },
        required_outputs=["debug_result.yaml"],
    )


def debug_result_message(
    run_id: str,
    *,
    step_id: str,
    status: str,
    proposed_fix: str,
) -> A2AMessage:
    to_agent = "biomaster-check" if status == "pass" else "biomaster-execute"
    phase = "checking" if status == "pass" else "execution"
    required_outputs = ["check_request.yaml"] if status == "pass" else ["retry_plan.yaml"]
    return build_message(
        "debug_result",
        from_agent="biomaster-debug",
        to_agent=to_agent,
        run_id=run_id,
        phase=phase,
        payload={"step_id": step_id, "status": status, "proposed_fix": proposed_fix},
        required_outputs=required_outputs,
    )


def final_report_request(run_id: str, *, plan_path: str) -> A2AMessage:
    return build_message(
        "final_report_request",
        from_agent="biomaster-check",
        to_agent="biomaster-plan",
        run_id=run_id,
        phase="reporting",
        payload={"plan_path": plan_path},
        required_outputs=["REPORT.md"],
    )


def check_result_message(
    run_id: str,
    *,
    step_id: str,
    status: str,
    failed_check: str = "",
    suggested_debug_skills: list[str] | None = None,
) -> A2AMessage:
    failed = status in {"fail", "failed"}
    to_agent = "biomaster-debug" if failed else "biomaster-execute"
    return build_message(
        "check_result",
        from_agent="biomaster-check",
        to_agent=to_agent,
        run_id=run_id,
        phase="debugging" if failed else "execution",
        payload={
            "step_id": step_id,
            "status": status,
            "failed_check": failed_check,
            "suggested_debug_skills": suggested_debug_skills or [],
        },
        required_outputs=["check_result.yaml"],
    )


def write_message(run_dir: Path, message: A2AMessage) -> Path:
    run_dir.mkdir(parents=True, exist_ok=True)
    path = run_dir / "a2a" / f"{message.created_at.replace(':', '')}_{message.message_type}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    import json

    path.write_text(json.dumps(message.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")
    return path
