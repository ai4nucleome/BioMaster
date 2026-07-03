from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from biomaster.runtime import find_matching_projects, new_project_id, new_semantic_project_id, semantic_project_slug, slugify_project_name  # noqa: E402


def test_project_slug_and_new_suffix(tmp_path):
    projects = tmp_path / "projects"
    (projects / "tumor-heterogeneity").mkdir(parents=True)

    assert slugify_project_name("Tumor heterogeneity!") == "tumor-heterogeneity"
    assert new_project_id("Tumor heterogeneity", projects_root=projects, force_new=False) == "tumor-heterogeneity"
    assert new_project_id("Tumor heterogeneity", projects_root=projects, force_new=True) == "tumor-heterogeneity-002"


def test_semantic_project_slug_uses_dataset_and_goal(tmp_path):
    projects = tmp_path / "projects"
    slug = semantic_project_slug(
        dataset="maynard2020_3k",
        analysis_type="tumor_scrnaseq_heterogeneity",
        goal="state trajectory analysis",
    )
    assert slug == "maynard2020-3k-tumor-scrnaseq-heterogeneity-state-trajectory-analysis"
    assert not slug.startswith("001")
    assert new_semantic_project_id(
        dataset="maynard2020_3k",
        analysis_type="tumor_scrnaseq_heterogeneity",
        goal="state trajectory analysis",
        projects_root=projects,
    ) == slug


def test_find_matching_projects_reads_project_files(tmp_path):
    project = tmp_path / "projects" / "maynard2020-3k-tumor-scrnaseq-heterogeneity"
    project.mkdir(parents=True)
    (project / "PLAN.yaml").write_text(
        "dataset: maynard2020_3k\nanalysis_type: tumor_scrnaseq_heterogeneity\nselected_route_id: tumor_scrnaseq_heterogeneity\nsteps:\n  - step_id: '01_data_preflight'\n",
        encoding="utf-8",
    )
    (project / "PROJECT_LOG.yaml").write_text("steps: []\n", encoding="utf-8")

    matches = find_matching_projects(
        dataset="maynard2020_3k",
        analysis_type="tumor_scrnaseq_heterogeneity",
        projects_root=tmp_path / "projects",
    )
    assert matches
    assert matches[0]["project_id"] == "maynard2020-3k-tumor-scrnaseq-heterogeneity"
    assert matches[0]["has_plan"] is True
