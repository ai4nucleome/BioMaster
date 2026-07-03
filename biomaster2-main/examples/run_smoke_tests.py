from __future__ import annotations

from pathlib import Path
import csv
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / ".opencode" / "runtime"))

from biomaster.mvp import MVP_SKILL_IDS  # noqa: E402
from biomaster.skills.manager import DEFAULT_INTERNAL_SKILL_ROOT, DEFAULT_SKILL_ROOT, AgentSkillAccessPolicy, SkillCatalog  # noqa: E402


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
    public_catalog = SkillCatalog.from_root(DEFAULT_SKILL_ROOT)
    public_names = {skill.name for skill in public_catalog.list()}
    assert_true(public_names == {"biomaster"}, "public OpenCode skill surface must expose only biomaster")

    catalog = SkillCatalog.from_roots([DEFAULT_SKILL_ROOT, DEFAULT_INTERNAL_SKILL_ROOT])
    policy = AgentSkillAccessPolicy.from_file()
    skill_names = {skill.name for skill in catalog.list()}
    missing = set(MVP_SKILL_IDS) - skill_names
    assert_true(not missing, f"active skills must include MVP set, missing: {sorted(missing)}")

    plan_hits = catalog.search_for_agent("biomaster-plan", policy, "tumor heterogeneity scRNA-seq trajectory")
    execute_hits = catalog.search_for_agent("biomaster-execute", policy, "run Scanpy QC scRNA-seq")
    check_hits = catalog.search_for_agent("biomaster-check", policy, "verify scRNA-seq QC outputs")
    debug_hits = catalog.search_for_agent("biomaster-debug", policy, "conda environment missing")

    assert_true(any(skill.layer == "plan" for skill in plan_hits), "plan agent should retrieve plan skills")
    assert_true(all(skill.layer in {"registry", "domain-guide", "discipline", "pipeline", "plan", "report"} for skill in plan_hits), "plan agent retrieved forbidden layers")
    assert_true(any(skill.layer == "execute" for skill in execute_hits), "execute agent should retrieve execute skills")
    assert_true(all(skill.layer in {"execute", "env", "verify"} for skill in execute_hits), "execute agent retrieved forbidden layers")
    assert_true(all(skill.layer == "verify" for skill in check_hits), "check agent should retrieve verify skills only")
    assert_true(any(skill.layer == "debug" for skill in debug_hits), "debug agent should retrieve debug skills")

    denied_execute = catalog.list_for_agent("biomaster-plan", policy, layer="execute")
    denied_plan = catalog.list_for_agent("biomaster-execute", policy, layer="plan")
    assert_true(not denied_execute, "plan agent must not list execute skills")
    assert_true(not denied_plan, "execute agent must not list plan skills")
    assert_true(not policy.validate({"registry", "domain-guide", "discipline", "pipeline", "plan", "execute", "verify", "debug", "env", "report"}), "access policy should validate")


def check_agent_requirements() -> None:
    intake_prompt = (AGENT_DIR / "biomaster-intake.md").read_text(encoding="utf-8")
    plan_prompt = (AGENT_DIR / "biomaster-plan.md").read_text(encoding="utf-8")
    execute_prompt = (AGENT_DIR / "biomaster-execute.md").read_text(encoding="utf-8")
    check_prompt = (AGENT_DIR / "biomaster-check.md").read_text(encoding="utf-8")
    debug_prompt = (AGENT_DIR / "biomaster-debug.md").read_text(encoding="utf-8")

    assert_true("运行模式" in intake_prompt or "operating mode" in intake_prompt.lower(), "intake must ask operating mode")
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
