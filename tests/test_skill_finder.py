from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from biomaster.knowledge.seed_routes import seed_routes  # noqa: E402
from biomaster.knowledge.skill_finder import find_skills  # noqa: E402
from biomaster.knowledge.sync_all import sync_all  # noqa: E402


def test_skill_finder_init_phase(tmp_path):
    db = tmp_path / "knowledge.db"
    sync_all(db_path=db)
    seed_routes(db)
    result = find_skills(
        "",
        "biomaster-plan",
        "init",
        db_path=db,
        log_selection=False,
    )
    assert result["selected_skill_ids"] == ["biomaster"]


def test_skill_finder_auto_initializes_missing_sqlite(tmp_path):
    db = tmp_path / "missing" / "knowledge.db"
    assert not db.exists()
    result = find_skills(
        "tumor heterogeneity inferCNV Palantir cNMF scRNA-seq",
        "plan-agent",
        "planning",
        db_path=db,
        log_selection=False,
    )
    assert db.exists()
    assert result["sqlite_readiness"]["created_or_synced"] is True
    assert result["selected_route_id"] == "tumor_scrnaseq_heterogeneity"
    assert result["sqlite_route_search"] is True


def test_skill_finder_mode_selection_core_only(tmp_path):
    db = tmp_path / "knowledge.db"
    sync_all(db_path=db)
    seed_routes(db)
    result = find_skills(
        "tumor heterogeneity inferCNV Palantir cNMF scRNA-seq",
        "biomaster-plan",
        "mode_selection",
        db_path=db,
        log_selection=False,
    )
    assert result["selected_skill_ids"] == ["biomaster"]
    selected = set(result["selected_skill_ids"])
    assert "registry" not in selected
    assert "domain-guide-tumor" not in selected
    assert "pipeline-scrnaseq-tumor" not in selected
    assert "plan-scrnaseq-tumor-heterogeneity" not in selected


def test_skill_finder_mode_selection_falls_back_to_registry(tmp_path):
    db = tmp_path / "knowledge.db"
    sync_all(db_path=db)
    seed_routes(db)
    result = find_skills(
        "请帮我加载当前 biomaster 的 skill",
        "biomaster-plan",
        "mode_selection",
        db_path=db,
        log_selection=False,
    )
    assert result["selected_skill_ids"] == ["biomaster"]
    assert result["selected_route_id"] is None


def test_skill_finder_tumor_plan_phase(tmp_path):
    db = tmp_path / "knowledge.db"
    sync_all(db_path=db)
    seed_routes(db)
    result = find_skills(
        "肿瘤异质性与状态轨迹分析 inferCNV Palantir cNMF",
        "plan-agent",
        "planning",
        db_path=db,
        log_selection=False,
    )
    assert result["selected_route_id"] == "tumor_scrnaseq_heterogeneity"
    assert result["sqlite_route_search"] is True
    assert result["route_candidates"]
    selected = set(result["selected_skill_ids"])
    assert "plan-scrnaseq-tumor-heterogeneity" in selected
    assert "exec-scanpy" not in selected
    assert "debug-conda" not in selected


def test_skill_finder_planning_requires_sqlite_route(tmp_path):
    db = tmp_path / "knowledge.db"
    sync_all(db_path=db)
    seed_routes(db)
    try:
        find_skills(
            "完全无法匹配的随机分析目标",
            "plan-agent",
            "planning",
            db_path=db,
            log_selection=False,
        )
    except ValueError as exc:
        assert "SQLite pipeline_routes match" in str(exc)
    else:
        raise AssertionError("planning without SQLite route should fail")


def test_skill_finder_execute_phase(tmp_path):
    db = tmp_path / "knowledge.db"
    sync_all(db_path=db)
    seed_routes(db)
    result = find_skills(
        "tumor scRNA-seq Scanpy QC inferCNV Palantir",
        "execute-agent",
        "execution",
        db_path=db,
        include_optional=True,
        log_selection=False,
    )
    selected = set(result["selected_skill_ids"])
    assert selected
    assert "exec-scanpy" in selected or "exec-infercnvpy" in selected
    assert "plan-scrnaseq-tumor-heterogeneity" not in selected
