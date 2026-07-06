from __future__ import annotations

from pathlib import Path
import csv
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / ".opencode" / "runtime"))

from biomaster.knowledge import DEFAULT_DB_PATH, DEFAULT_SKILL_ROOT, connect  # noqa: E402
from biomaster.knowledge.query_skills import list_skills, list_skills_for_agent  # noqa: E402
from biomaster.knowledge.seed_routes import seed_routes  # noqa: E402
from biomaster.knowledge.sync_all import sync_all  # noqa: E402
from biomaster.mvp import MVP_SKILL_IDS  # noqa: E402


DATA_DIR = Path(__file__).resolve().parent / "data"
REAL_DATA_DIR = Path(__file__).resolve().parent / "real_data"
AGENT_DIR = PROJECT_ROOT / ".opencode" / "agents"


def assert_true(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def check_count_matrix() -> None:
    counts_path = DATA_DIR / "rnaseq_counts.csv"
    metadata_path = DATA_DIR / "rnaseq_metadata.csv"
    assert_true(counts_path.exists(), f"missing count matrix: {counts_path}")
    assert_true(metadata_path.exists(), f"missing metadata: {metadata_path}")
    with counts_path.open("r", encoding="utf-8", newline="") as file:
        count_rows = list(csv.DictReader(file))
    with metadata_path.open("r", encoding="utf-8", newline="") as file:
        metadata_rows = list(csv.DictReader(file))
    samples = [key for key in count_rows[0] if key != "gene_id"]
    metadata_samples = [row["sample_id"] for row in metadata_rows]
    assert_true(samples == metadata_samples, "count matrix sample columns must match metadata sample_id order")


def check_fastq() -> None:
    fastq_path = DATA_DIR / "tiny_reads.fastq"
    lines = fastq_path.read_text(encoding="utf-8").splitlines()
    assert_true(len(lines) % 4 == 0, "FASTQ line count must be divisible by 4")


def check_skill_catalog() -> None:
    public_names = {path.name for path in DEFAULT_SKILL_ROOT.iterdir() if path.is_dir()}
    assert_true(public_names == {"biomaster"}, "public OpenCode skill surface must expose only biomaster")

    sync_all(DEFAULT_DB_PATH)
    seed_routes(DEFAULT_DB_PATH)
    connection = connect(DEFAULT_DB_PATH)
    try:
        skill_names = {skill["skill_id"] for skill in list_skills(connection)}
        missing = set(MVP_SKILL_IDS) - skill_names
        assert_true(not missing, f"active skills must include MVP set, missing: {sorted(missing)}")

        plan_hits = list_skills_for_agent(connection, "biomaster-plan")
        execute_hits = list_skills_for_agent(connection, "biomaster-execute")
        check_hits = list_skills_for_agent(connection, "biomaster-check")
        debug_hits = list_skills_for_agent(connection, "biomaster-debug")

        assert_true(any(skill["layer"] == "plan" for skill in plan_hits), "plan agent should retrieve plan skills")
        assert_true(any(skill["layer"] == "execute" for skill in execute_hits), "execute agent should retrieve execute skills")
        assert_true(any(skill["layer"] == "verify" for skill in check_hits), "check agent should retrieve verify skills")
        assert_true(any(skill["layer"] == "debug" for skill in debug_hits), "debug agent should retrieve debug skills")
        assert_true(
            not any(skill["layer"] == "execute" for skill in plan_hits),
            "plan agent must not list execute skills",
        )
        assert_true(
            not any(skill["layer"] == "plan" for skill in execute_hits),
            "execute agent must not list plan skills",
        )
    finally:
        connection.close()


def check_agent_requirements() -> None:
    plan_prompt = (AGENT_DIR / "biomaster-plan.md").read_text(encoding="utf-8")
    execute_prompt = (AGENT_DIR / "biomaster-execute.md").read_text(encoding="utf-8")
    check_prompt = (AGENT_DIR / "biomaster-check.md").read_text(encoding="utf-8")
    debug_prompt = (AGENT_DIR / "biomaster-debug.md").read_text(encoding="utf-8")

    assert_true("operating mode" in plan_prompt.lower(), "plan primary must ask operating mode")
    assert_true("PLAN.yaml" in plan_prompt, "plan agent must generate PLAN.yaml")
    assert_true("verify-*" in check_prompt, "check agent must use verify skills")
    assert_true("debug-*" in debug_prompt, "debug agent must use debug skills")
    assert_true("biomaster-check" in execute_prompt, "execute agent must hand off to check agent")
    assert_true(not (AGENT_DIR / "biomaster-verify.md").exists(), "legacy verify agent must be removed")


def main() -> None:
    check_count_matrix()
    check_fastq()
    check_skill_catalog()
    check_agent_requirements()
    print("BioMaster OpenCode smoke tests passed.")


if __name__ == "__main__":
    main()
