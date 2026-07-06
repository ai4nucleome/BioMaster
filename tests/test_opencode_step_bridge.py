from argparse import Namespace
from pathlib import Path
import importlib.util
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from biomaster.knowledge.seed_routes import seed_routes  # noqa: E402
from biomaster.knowledge.sync_all import sync_all  # noqa: E402
from biomaster.runtime import RunContext, save_plan_from_template  # noqa: E402
import biomaster.runtime.run_context as run_context_module  # noqa: E402


def load_bridge_module():
    path = ROOT / ".opencode/runtime/biomaster/scripts/opencode_step.py"
    spec = importlib.util.spec_from_file_location("opencode_step_bridge", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def args(project: str, step_id: str, db: Path) -> Namespace:
    return Namespace(project=project, step_id=step_id, db=db, yaml=False)


def test_opencode_step_bridge_executes_debugs_and_checks(tmp_path, monkeypatch):
    projects_root = tmp_path / "projects"
    monkeypatch.setattr(run_context_module, "PROJECTS_ROOT", projects_root)
    bridge = load_bridge_module()

    db = tmp_path / "knowledge.db"
    sync_all(db_path=db)
    seed_routes(db)

    project = "tumor-bridge"
    run = RunContext(project, root=projects_root / project)
    save_plan_from_template(run, ROOT / "examples/tumor_scrnaseq_heterogeneity/expected_PLAN.yaml")

    execute = bridge.command_execute_step(args(project, "01_data_preflight", db))
    assert execute["result"]["status"] == "completed"
    debug = bridge.command_debug_step(args(project, "01_data_preflight", db))
    assert debug["result"]["status"] == "pass"
    check = bridge.command_check_step(args(project, "01_data_preflight", db))
    assert check["result"]["status"] == "pass"

    report_execute = bridge.command_execute_step(args(project, "09_report_generation", db))
    assert report_execute["result"]["status"] == "completed"
    report_debug = bridge.command_debug_step(args(project, "09_report_generation", db))
    assert report_debug["result"]["status"] == "pass"
    report_check = bridge.command_check_step(args(project, "09_report_generation", db))
    assert report_check["result"]["status"] == "pass"

    assert (run.root / "REPORT.md").exists()
    assert (run.root / "OPENCODE_VIEW.md").exists()
    assert (run.root / "steps/09_report_generation/step_result.yaml").exists()
    assert not (run.root / "steps/09_report_generation/REPORT.md").exists()


def test_bridge_keeps_v02_strict_output_validation(tmp_path, monkeypatch):
    projects_root = tmp_path / "projects"
    monkeypatch.setattr(run_context_module, "PROJECTS_ROOT", projects_root)
    bridge = load_bridge_module()

    db = tmp_path / "knowledge.db"
    sync_all(db_path=db)
    seed_routes(db)

    project = "strict-validation"
    run = RunContext(project, root=projects_root / project)
    run.write_plan(
        {
            "analysis_type": "strict_validation_probe",
            "plan_version": 1,
            "mode": "test",
            "dataset": "maynard2020_3k",
            "selected_route_id": "tumor_scrnaseq_heterogeneity",
            "steps": [
                {
                    "step_id": "10_unimplemented_probe",
                    "objective": "Probe strict output validation.",
                    "required_execute_skills": ["exec-scanpy"],
                    "required_verify_skills": ["verify-scrna-qc"],
                    "expected_outputs": ["must_not_be_fabricated.csv"],
                    "acceptance_criteria": ["missing output must fail check"],
                }
            ],
        }
    )

    execute = bridge.command_execute_step(args(project, "10_unimplemented_probe", db))
    assert execute["result"]["status"] == "completed"
    assert not (run.root / "steps/10_unimplemented_probe/must_not_be_fabricated.csv").exists()

    check = bridge.command_check_step(args(project, "10_unimplemented_probe", db))
    assert check["result"]["status"] == "fail"
    assert "missing expected output: must_not_be_fabricated.csv" in check["result"]["reason"]
