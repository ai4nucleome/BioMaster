from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from biomaster.knowledge import connect  # noqa: E402
from biomaster.knowledge.init_db import init_database  # noqa: E402
from biomaster.knowledge.phases import PRIMARY_USER_AGENT, validate_phase_transition  # noqa: E402
from biomaster.knowledge.state_manager import create_run, update_run  # noqa: E402


def test_plan_is_primary_user_agent():
    assert PRIMARY_USER_AGENT == "biomaster-plan"


def test_phase_transition_policy():
    assert not validate_phase_transition(None, "init")
    assert not validate_phase_transition("init", "mode_selection")
    assert not validate_phase_transition("mode_selection", "domain_anchoring")
    assert validate_phase_transition(None, "planning")
    assert validate_phase_transition("init", "planning")
    assert not validate_phase_transition("execution", "debugging")
    assert validate_phase_transition("execution", "checking")
    assert not validate_phase_transition("checking", "execution")


def test_run_state_rejects_phase_skips(tmp_path):
    db = tmp_path / "knowledge.db"
    init_database(db)
    connection = connect(db)
    try:
        run = create_run(connection)
        run_id = run["run_id"]
        assert run["phase"] == "init"
        assert run_id.startswith("biomaster-project")

        named = create_run(connection, run_id="strict flow demo")
        assert named["run_id"] == "strict-flow-demo"

        try:
            create_run(connection, selected_route_id="tumor_scrnaseq_heterogeneity")
        except ValueError as exc:
            assert "SQLite Skill Finder" in str(exc)
        else:
            raise AssertionError("route_id at create_run should be rejected")

        try:
            update_run(connection, run_id, phase="planning")
        except ValueError as exc:
            assert "invalid phase transition" in str(exc)
        else:
            raise AssertionError("phase skip should be rejected")

        run = update_run(connection, run_id, phase="mode_selection")
        assert run["phase"] == "mode_selection"

        next_project = create_run(connection)
        assert next_project["run_id"].startswith("biomaster-project")
        assert next_project["run_id"] != run_id
    finally:
        connection.close()
