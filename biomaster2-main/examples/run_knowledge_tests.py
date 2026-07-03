from __future__ import annotations

from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / ".opencode" / "runtime"))

from biomaster.knowledge import REQUIRED_TABLES, connect, table_exists  # noqa: E402
from biomaster.knowledge.init_db import init_database  # noqa: E402
from biomaster.knowledge.query_skills import get_route, list_knowledge_records, list_skills, list_skills_for_agent, search_knowledge_records, search_routes, skills_for_route  # noqa: E402
from biomaster.knowledge.seed_routes import seed_routes  # noqa: E402
from biomaster.knowledge.skill_finder import find_skills  # noqa: E402
from biomaster.knowledge.state_manager import create_run, disable_skills, update_run  # noqa: E402
from biomaster.knowledge.sync_all import sync_all  # noqa: E402
from biomaster.mvp import MVP_SKILL_IDS  # noqa: E402


TEST_DB = PROJECT_ROOT / ".opencode" / "knowledge" / "biomaster_skills.db"


def assert_true(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def check_database_bootstrap() -> None:
    if TEST_DB.exists():
        TEST_DB.unlink()
    tables = init_database(TEST_DB)
    assert_true(set(REQUIRED_TABLES).issubset(set(tables)), "required MVP SQLite tables are missing")
    connection = connect(TEST_DB)
    try:
        assert_true(table_exists(connection, "knowledge_records"), "knowledge_records table must exist")
    finally:
        connection.close()


def check_skill_sync() -> None:
    stats = sync_all(db_path=TEST_DB)
    assert_true(stats["synced"] >= len(MVP_SKILL_IDS), f"expected at least {len(MVP_SKILL_IDS)} MVP skills, synced {stats['synced']}")
    assert_true(stats["workflows_synced"] == 56, f"expected 56 workflow records, synced {stats['workflows_synced']}")
    assert_true(stats["tasks_synced"] == 76, f"expected 76 task records, synced {stats['tasks_synced']}")

    connection = connect(TEST_DB)
    try:
        skills = list_skills(connection)
        synced_ids = {skill["skill_id"] for skill in skills}
        missing = set(MVP_SKILL_IDS) - synced_ids
        assert_true(not missing, f"SQLite skills table must include MVP skills, missing: {sorted(missing)}")
        for skill in skills:
            assert_true(skill["body"], f"missing skill body for {skill['skill_id']}")
        workflows = list_knowledge_records(connection, record_type="workflow")
        tasks = list_knowledge_records(connection, record_type="task")
        assert_true(len(workflows) == 56, f"expected 56 workflows, found {len(workflows)}")
        assert_true(len(tasks) == 76, f"expected 76 tasks, found {len(tasks)}")
        assert_true(search_knowledge_records(connection, "DESeq2", record_type="task"), "task knowledge search should find DESeq2 records")
    finally:
        connection.close()


def check_pipeline_routes() -> None:
    route_count = seed_routes(TEST_DB)
    assert_true(route_count >= 3, "expected seeded pipeline routes")

    connection = connect(TEST_DB)
    try:
        tumor_route = get_route(connection, "tumor_scrnaseq_heterogeneity")
        assert_true(tumor_route is not None, "tumor route must exist")
        route_skills = skills_for_route(connection, "tumor_scrnaseq_heterogeneity", agent_name="biomaster-plan")
        route_skill_ids = {skill["skill_id"] for skill in route_skills}
        assert_true("plan-scrnaseq-tumor-heterogeneity" in route_skill_ids, "tumor route must resolve plan skill")
        assert_true("exec-scanpy" not in route_skill_ids, "plan agent route resolution must not include exec skills")

        scored = search_routes(connection, "肿瘤异质性与状态轨迹 inferCNV Palantir")
        assert_true(scored and scored[0][1]["route_id"] == "tumor_scrnaseq_heterogeneity", "tumor route search mismatch")
    finally:
        connection.close()


def check_agent_filtering() -> None:
    connection = connect(TEST_DB)
    try:
        plan_skills = list_skills_for_agent(connection, "biomaster-plan")
        execute_skills = list_skills_for_agent(connection, "biomaster-execute")
        check_skills = list_skills_for_agent(connection, "biomaster-check")
        plan_layers = {skill["layer"] for skill in plan_skills}
        execute_layers = {skill["layer"] for skill in execute_skills}
        check_layers = {skill["layer"] for skill in check_skills}
        assert_true({"plan", "pipeline", "domain-guide"}.intersection(plan_layers), "plan agent should see planning layers")
        assert_true("execute" in execute_layers, "execute agent should see execute skills")
        assert_true(check_layers == {"verify"}, "check agent should see verify skills only")
        assert_true(not any(skill["layer"] == "execute" for skill in plan_skills), "plan agent must not see execute skills")
        assert_true(not any(skill["layer"] == "plan" for skill in execute_skills), "execute agent must not see plan skills")
    finally:
        connection.close()


def check_skill_finder_and_run_state() -> None:
    connection = connect(TEST_DB)
    try:
        run = create_run(connection)
        run_id = run["run_id"]
        for phase in ("mode_selection", "domain_anchoring", "pipeline_routing"):
            run = update_run(connection, run_id, phase=phase)
        routed = find_skills(
            "肿瘤异质性与状态轨迹分析 inferCNV Palantir cNMF",
            "biomaster-intake",
            "pipeline_routing",
            run_id=run_id,
            db_path=TEST_DB,
            save_run_state=True,
            log_selection=False,
        )
        assert_true(routed["selected_route_id"] == "tumor_scrnaseq_heterogeneity", "SQLite route must be saved before planning")
        run = update_run(connection, run_id, phase="planning")
        disable_skills(connection, run_id, ["plan-scrnaseq-tumor-heterogeneity"])

        tumor_result = find_skills(
            "肿瘤异质性与状态轨迹分析 inferCNV Palantir cNMF",
            "biomaster-plan",
            "planning",
            run_id=run_id,
            db_path=TEST_DB,
            log_selection=False,
        )
        assert_true(tumor_result["selected_route_id"] == "tumor_scrnaseq_heterogeneity", "tumor route mismatch")
        assert_true("plan-scrnaseq-tumor-heterogeneity" not in tumor_result["selected_skill_ids"], "disabled skill must not be selected")
        assert_true("plan-scrnaseq-tumor-heterogeneity" in tumor_result["rejected_skill_ids"], "disabled skill should be rejected")
        assert_true("exec-scanpy" not in tumor_result["selected_skill_ids"], "plan phase must not select exec skills")
        assert_true("debug-conda" not in tumor_result["selected_skill_ids"], "plan phase must not select debug skills")

        execute_result = find_skills(
            "run Scanpy QC scRNA-seq",
            "biomaster-execute",
            "execution",
            db_path=TEST_DB,
            include_optional=True,
            log_selection=False,
        )
        assert_true(all(not skill_id.startswith("plan-") for skill_id in execute_result["selected_skill_ids"]), "execute phase must not receive plan skills")
    finally:
        connection.close()


def main() -> None:
    check_database_bootstrap()
    check_skill_sync()
    check_pipeline_routes()
    check_agent_filtering()
    check_skill_finder_and_run_state()
    print("BioMaster SQLite knowledge control tests passed.")


if __name__ == "__main__":
    main()
