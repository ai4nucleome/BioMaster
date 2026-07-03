from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from biomaster.a2a import (  # noqa: E402
    check_result_message,
    check_request,
    debug_request_message,
    debug_result_message,
    execution_request,
    intake_request,
    planning_request_from_intake,
    validate_message,
    validate_transition,
)


def test_a2a_planning_request():
    message = planning_request_from_intake(
        "001",
        mode="test",
        domain="tumor",
        discipline="scrnaseq",
        pipeline="tumor_heterogeneity",
        dataset="maynard2020_3k",
        user_goal="肿瘤异质性与状态轨迹分析",
    )
    assert not validate_message(message)
    assert message.to_agent == "biomaster-plan"


def test_a2a_transition_chain():
    run_id = "001"
    intake_msg = intake_request(run_id, user_goal="demo", mode="test")
    plan_msg = planning_request_from_intake(
        run_id,
        mode="test",
        domain="tumor",
        discipline="scrnaseq",
        pipeline="tumor_heterogeneity",
        dataset="maynard2020_3k",
        user_goal="demo",
    )
    exec_msg = execution_request(run_id, plan_path=f"runs/{run_id}/PLAN.yaml", start_step="01_data_preflight")
    debug_msg = debug_request_message(
        run_id,
        step_id="01_data_preflight",
        failed_check="execution_review",
        from_agent="biomaster-execute",
    )
    debug_pass = debug_result_message(
        run_id,
        step_id="01_data_preflight",
        status="pass",
        proposed_fix="",
    )
    check_msg = check_request(run_id, step_id="01_data_preflight", plan_path=f"runs/{run_id}/PLAN.yaml")
    check_pass = check_result_message(run_id, step_id="01_data_preflight", status="pass")
    next_exec = execution_request(run_id, plan_path=f"runs/{run_id}/PLAN.yaml", start_step="02_qc_filter")
    assert not validate_transition(None, intake_msg.message_type)
    assert validate_transition(None, plan_msg.message_type)
    assert not validate_transition(intake_msg.message_type, plan_msg.message_type)
    assert not validate_transition(plan_msg.message_type, exec_msg.message_type)
    assert validate_transition(exec_msg.message_type, check_msg.message_type)
    assert not validate_transition(exec_msg.message_type, debug_msg.message_type)
    assert not validate_transition(debug_msg.message_type, debug_pass.message_type)
    assert not validate_transition(debug_pass.message_type, check_msg.message_type)
    assert not validate_transition(check_msg.message_type, check_pass.message_type)
    assert not validate_transition(check_pass.message_type, next_exec.message_type)
