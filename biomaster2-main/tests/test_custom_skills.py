from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from biomaster.knowledge import DEFAULT_INTERNAL_SKILL_ROOT, DEFAULT_SKILL_ROOT  # noqa: E402
from biomaster.knowledge.seed_routes import seed_routes  # noqa: E402
from biomaster.knowledge.skill_finder import find_skills  # noqa: E402
from biomaster.knowledge.sync_skills import sync_skills  # noqa: E402
from biomaster.skills.add_skill import create_skill  # noqa: E402


def test_custom_plan_and_execute_skills_are_selectable(tmp_path):
    custom_root = tmp_path / "skills"
    create_skill(
        name="spatial-routing",
        target="plan",
        description="Plan spatial transcriptomics routing with Xenium custom markers.",
        metadata_value="spatial-transcriptomics",
        root=custom_root,
    )
    create_skill(
        name="xenium-qc",
        target="execute",
        description="Execute Xenium spatial transcriptomics QC for custom marker panels.",
        metadata_value="xenium-qc",
        root=custom_root,
    )

    db = tmp_path / "knowledge.db"
    sync_skills(
        db_path=db,
        skill_roots=[DEFAULT_SKILL_ROOT, DEFAULT_INTERNAL_SKILL_ROOT, custom_root],
        project_root=ROOT,
    )
    seed_routes(db)

    planning = find_skills(
        "tumor heterogeneity inferCNV Palantir cNMF spatial transcriptomics Xenium custom markers",
        "biomaster-plan",
        "planning",
        db_path=db,
        log_selection=False,
    )
    assert "plan-spatial-routing" in planning["selected_skill_ids"]
    assert "exec-xenium-qc" not in planning["selected_skill_ids"]

    execution = find_skills(
        "run Xenium spatial transcriptomics QC custom marker panels",
        "biomaster-execute",
        "execution",
        db_path=db,
        log_selection=False,
    )
    assert "exec-xenium-qc" in execution["selected_skill_ids"]
    assert "plan-spatial-routing" not in execution["selected_skill_ids"]
