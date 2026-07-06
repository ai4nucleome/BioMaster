from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from biomaster.knowledge.prompt_assembler import assemble_prompt  # noqa: E402
from biomaster.knowledge.seed_routes import seed_routes  # noqa: E402
from biomaster.knowledge.skill_finder import find_skills  # noqa: E402
from biomaster.knowledge.sync_all import sync_all  # noqa: E402


def test_prompt_assembler_plan_manifests(tmp_path):
    db = tmp_path / "knowledge.db"
    sync_all(db_path=db)
    seed_routes(db)
    finder = find_skills(
        "tumor heterogeneity trajectory scRNA-seq",
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
    assert "plan-scrnaseq-tumor-heterogeneity" in assembled["inserted_skills"]
    assert assembled["inserted_manifests"]
    assert "01_data_contract.md" in "\n".join(assembled["inserted_manifests"])
    assert "exec-scanpy" not in assembled["inserted_skills"]
