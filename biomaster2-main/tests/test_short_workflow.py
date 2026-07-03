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

    run_id = new_run_id("tumor-demo", runs_root=tmp_path / "runs")
    assert run_id == "001"
    run = RunContext(run_id, root=tmp_path / "runs" / run_id)
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
    assert plan["plan_id"] == "001"
    assert plan["run_dir"].endswith("runs/001")
    step_result = execute_step(run, plan, "01_data_preflight", db_path=db)
    assert step_result["status"] == "completed"
    assert step_result["sqlite_skill_query"]["queried_skill_ids"] == ["exec-scanpy"]
    assert step_result["sqlite_skill_query"]["resolved_skill_ids"][0]["skill_id"] == "exec-scanpy"
    assert step_result["script_dir"].endswith("runs/001/scripts/01_data_preflight")
    assert step_result["result_dir"].endswith("runs/001/steps/01_data_preflight")
    assert (run.root / "scripts" / "01_data_preflight" / "run.sh").exists()
    assert not (run.root / "outputs").exists()

    debug = debug_step(run, plan, "01_data_preflight", db_path=db)
    assert debug["status"] == "pass"
    assert debug["next_action"] == "check"
    assert debug["sqlite_debug_query"]["resolved_skill_ids"]
    check = check_step(run, "01_data_preflight", plan=plan, db_path=db)
    assert check["status"] == "pass"
    view = run.root / "OPENCODE_VIEW.md"
    assert view.exists()
    view_text = view.read_text(encoding="utf-8")
    assert "scripts/01_data_preflight/run.sh" in view_text
    assert "steps/01_data_preflight/qc_metrics.csv" in view_text

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


def test_execute_step_requires_sqlite_skill_lookup(tmp_path, monkeypatch):
    monkeypatch.setattr("biomaster.runtime.run_context.PROJECT_ROOT", tmp_path)
    db = tmp_path / "empty.db"

    run_id = new_run_id("tumor-demo", runs_root=tmp_path / "runs")
    run = RunContext(run_id, root=tmp_path / "runs" / run_id)
    template = ROOT / "examples" / "tumor_scrnaseq_heterogeneity" / "expected_PLAN.yaml"
    save_plan_from_template(run, template)
    plan = load_plan(run.plan_path)

    try:
        execute_step(run, plan, "01_data_preflight", db_path=db)
    except ValueError as exc:
        assert "SQLite skill query failed" in str(exc)
    else:
        raise AssertionError("execution should fail before script generation when SQLite has no exec skill")

    assert not (run.root / "scripts" / "01_data_preflight" / "run.sh").exists()
