from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from biomaster.a2a import planning_request_from_intake, write_message  # noqa: E402
from biomaster.knowledge.prompt_assembler import assemble_prompt  # noqa: E402
from biomaster.knowledge.seed_routes import seed_routes  # noqa: E402
from biomaster.knowledge.skill_finder import find_skills  # noqa: E402
from biomaster.knowledge.sync_all import sync_all  # noqa: E402
from biomaster.runtime import RunContext, check_step, debug_step, execute_step, load_plan, new_run_id, save_plan_from_template  # noqa: E402


def test_short_workflow(tmp_path, monkeypatch):
    monkeypatch.setattr("biomaster.runtime.run_context.PROJECT_ROOT", tmp_path)
    db = tmp_path / "knowledge.db"
    sync_all(db_path=db)
    seed_routes(db)

    run_id = new_run_id("tumor-demo", runs_root=tmp_path / "projects")
    assert run_id == "tumor-demo"
    run = RunContext(run_id, root=tmp_path / "projects" / run_id)
    template = ROOT / "examples" / "tumor_scrnaseq_heterogeneity" / "expected_PLAN.yaml"
    save_plan_from_template(run, template)

    finder = find_skills(
        "tumor heterogeneity scRNA-seq QC",
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
    assert assembled["final_context"]

    plan = load_plan(run.plan_path)
    assert plan["plan_id"] == "tumor-demo"
    assert plan["run_dir"].endswith("projects/tumor-demo")
    step_result = execute_step(run, plan, "01_data_preflight", db_path=db)
    assert step_result["status"] == "completed"
    assert step_result["execution_status"] == "success"
    assert step_result["exit_code"] == 0
    assert step_result["sqlite_skill_query"]["queried_skill_ids"] == ["exec-scanpy"]
    assert step_result["sqlite_skill_query"]["resolved_skill_ids"][0]["skill_id"] == "exec-scanpy"
    assert step_result["script_dir"].endswith("projects/tumor-demo/scripts/01_data_preflight")
    assert step_result["result_dir"].endswith("projects/tumor-demo/steps/01_data_preflight")
    assert step_result["stdout_path"].endswith("steps/01_data_preflight/stdout.log")
    assert step_result["stderr_path"].endswith("steps/01_data_preflight/stderr.log")
    assert (run.root / "scripts" / "01_data_preflight" / "run.sh").exists()
    assert not (run.root / "outputs").exists()

    debug = debug_step(run, plan, "01_data_preflight", db_path=db)
    assert debug["status"] == "pass"
    assert debug["next_action"] == "check"
    assert debug["sqlite_debug_query"]["resolved_skill_ids"]
    check = check_step(run, "01_data_preflight", plan=plan, db_path=db)
    assert check["status"] == "pass"
    assert run.project_log_path.exists()
    project_log = load_plan(run.project_log_path)
    logged_step = project_log["steps"][0]
    assert logged_step["summary"]
    assert logged_step["plan_context"]["expected_outputs"]
    assert logged_step["plan_context"]["acceptance_criteria"]
    assert logged_step["skill_evidence"]["verify_skill_query"]
    assert "artifacts" in logged_step
    assert logged_step["next_action"] == "continue"
    assert run.report_path.exists()
    view = run.root / "OPENCODE_VIEW.md"
    assert view.exists()
    view_text = view.read_text(encoding="utf-8")
    assert "## Project Dashboard" in view_text
    assert "| Stage | Status | Execution | Check | Evidence |" in view_text
    assert "## Key Files" in view_text
    assert "scripts/01_data_preflight/run.sh" in view_text
    assert "steps/01_data_preflight/qc_metrics.csv" in view_text
    report_text = run.report_path.read_text(encoding="utf-8")
    assert "## Key Outputs" in report_text
    assert "| Stage | Execution | Exit Code | Check | Conclusion |" in report_text

    message = planning_request_from_intake(
        run_id,
        mode="test",
        domain="tumor",
        discipline="scrnaseq",
        pipeline="tumor_heterogeneity",
        dataset="maynard2020_3k",
        user_goal="short workflow test",
    )
    write_message(run.root, message)
    assert (run.root / "a2a").exists()


def test_execute_step_auto_initializes_sqlite_and_records_query(tmp_path, monkeypatch):
    monkeypatch.setattr("biomaster.runtime.run_context.PROJECT_ROOT", tmp_path)
    db = tmp_path / "missing.db"
    assert not db.exists()

    run_id = new_run_id("tumor-demo", runs_root=tmp_path / "projects")
    run = RunContext(run_id, root=tmp_path / "projects" / run_id)
    template = ROOT / "examples" / "tumor_scrnaseq_heterogeneity" / "expected_PLAN.yaml"
    save_plan_from_template(run, template)
    plan = load_plan(run.plan_path)

    result = execute_step(run, plan, "01_data_preflight", db_path=db)
    assert db.exists()
    assert result["sqlite_skill_query"]["sqlite_readiness"]["created_or_synced"] is True
    assert result["sqlite_skill_query"]["resolved_skill_ids"][0]["skill_id"] == "exec-scanpy"
    assert (run.root / "scripts" / "01_data_preflight" / "run.sh").exists()
