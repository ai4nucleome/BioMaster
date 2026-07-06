from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from biomaster.a2a import (  # noqa: E402
    debug_request_message,
    execution_request,
    intake_request,
    planning_request_from_intake,
    validate_message,
    validate_transition,
    write_message,
)
from biomaster.knowledge import connect  # noqa: E402
from biomaster.knowledge.prompt_assembler import assemble_prompt  # noqa: E402
from biomaster.knowledge.seed_routes import seed_routes  # noqa: E402
from biomaster.knowledge.skill_finder import find_skills  # noqa: E402
from biomaster.knowledge.state_manager import create_run, update_run  # noqa: E402
from biomaster.knowledge.sync_all import sync_all  # noqa: E402
from biomaster.runtime import RunContext, load_plan, new_run_id, run_plan_serial, save_plan_from_template  # noqa: E402


def test_long_workflow(tmp_path, monkeypatch):
    monkeypatch.setattr("biomaster.runtime.run_context.PROJECT_ROOT", tmp_path)

    db = tmp_path / "knowledge.db"
    sync_all(db_path=db)
    seed_routes(db)

    run_id = new_run_id("tumor-long", runs_root=tmp_path / "projects")
    assert run_id == "tumor-long"
    run = RunContext(run_id, root=tmp_path / "projects" / run_id)
    template = ROOT / "examples" / "tumor_scrnaseq_heterogeneity" / "expected_PLAN.yaml"
    save_plan_from_template(run, template)
    plan = load_plan(run.plan_path)
    assert plan["plan_id"] == "tumor-long"
    assert plan["run_dir"].endswith("projects/tumor-long")
    assert len(plan["steps"]) == 9

    connection = connect(db)
    try:
        state = create_run(connection, run_id=run_id)
        for phase in (
            "mode_selection",
            "domain_anchoring",
            "pipeline_routing",
        ):
            update_run(connection, run_id, phase=phase)
        routed = find_skills(
            "肿瘤异质性与状态轨迹分析 inferCNV Palantir cNMF",
            "biomaster-plan",
            "pipeline_routing",
            run_id=run_id,
            db_path=db,
            save_run_state=True,
            log_selection=False,
        )
        assert routed["selected_route_id"] == "tumor_scrnaseq_heterogeneity"
        for phase in ("planning", "preflight", "execution"):
            update_run(connection, run_id, phase=phase)
        assert state["run_id"] == run_id
    finally:
        connection.close()

    intake = intake_request(run_id, user_goal="肿瘤异质性与状态轨迹分析", mode="test")
    planning = planning_request_from_intake(
        run_id,
        mode="test",
        domain="tumor",
        discipline="scrnaseq",
        pipeline="tumor_heterogeneity",
        dataset="maynard2020_3k",
        user_goal="肿瘤异质性与状态轨迹分析",
    )
    write_message(run.root, intake)
    write_message(run.root, planning)
    assert not validate_message(intake)
    assert not validate_message(planning)
    assert not validate_transition(intake.message_type, planning.message_type)

    finder = find_skills(
        "肿瘤异质性与状态轨迹分析 inferCNV Palantir cNMF",
        "plan-agent",
        "planning",
        db_path=db,
        log_selection=False,
    )
    assembled = assemble_prompt(
        agent_name="biomaster-plan",
        phase="planning",
        selected_skill_ids=finder["selected_skill_ids"],
        db_path=db,
    )
    assert len(assembled["inserted_manifests"]) >= 9
    assert "exec-scanpy" not in assembled["inserted_skills"]

    first_step = plan["steps"][0]["step_id"]
    exec_msg = execution_request(run_id, plan_path=str(run.plan_path), start_step=first_step)
    write_message(run.root, exec_msg)
    debug_msg = debug_request_message(
        run_id,
        step_id=first_step,
        failed_check="execution_review",
        from_agent="biomaster-execute",
    )
    assert not validate_transition(exec_msg.message_type, debug_msg.message_type)
    write_message(run.root, debug_msg)

    serial = run_plan_serial(run, plan, db_path=db)
    assert serial["status"] == "pass"
    assert serial["completed_steps"] == [step["step_id"] for step in plan["steps"]]
    assert (run.root / "scripts" / "01_data_preflight" / "run.sh").exists()
    assert (run.root / "scripts" / "02_qc_filter" / "run.sh").exists()
    assert (run.root / "steps" / "02_qc_filter" / "step_result.yaml").exists()
    assert (run.root / "scripts" / "04_batch_correction" / "run.sh").exists()
    assert (run.root / "steps" / "04_batch_correction" / "step_result.yaml").exists()
    assert (run.root / "steps" / "09_report_generation" / "step_result.yaml").exists()
    assert not (run.root / "steps" / "09_report_generation" / "REPORT.md").exists()

    assert (run.root / "a2a").exists()
    assert run.project_log_path.exists()
    assert run.report_path.exists()
    assert (run.root / "OPENCODE_VIEW.md").exists()
