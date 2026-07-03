"""Strict compliance checks against BioMaster-OpenCode implementation plan."""

from __future__ import annotations

import yaml

from biomaster.knowledge import DEFAULT_DB_PATH, DEFAULT_INTERNAL_SKILL_ROOT, DEFAULT_SKILL_ROOT, OPENCODE_ROOT, PACKAGE_ROOT, PROJECT_ROOT
from biomaster.mvp import MVP_CORE_TABLES, MVP_SKILL_IDS, REGISTRY_REQUIRED_OUTPUT_FIELDS, TUMOR_PIPELINE_STEPS

SKILL_ROOT = DEFAULT_SKILL_ROOT
INTERNAL_SKILL_ROOT = DEFAULT_INTERNAL_SKILL_ROOT
AGENT_DIR = OPENCODE_ROOT / "agents"
COMMAND_DIR = OPENCODE_ROOT / "commands"
A2A_SCHEMA_DIR = PACKAGE_ROOT / "a2a" / "schemas"
BIOM_SCHEMA_DIR = PACKAGE_ROOT / "schemas"


def check_mvp_skills() -> list[str]:
    errors: list[str] = []
    public = {path.name for path in SKILL_ROOT.iterdir() if path.is_dir()}
    if public != {"biomaster"}:
        errors.append(f"public .opencode/skills must expose only biomaster, found: {sorted(public)}")
    present = public | {path.name for path in INTERNAL_SKILL_ROOT.iterdir() if path.is_dir()}
    missing = MVP_SKILL_IDS - present
    if missing:
        errors.append(f"missing MVP skills: {sorted(missing)}")
    for skill_id in MVP_SKILL_IDS:
        skill_file = (SKILL_ROOT / skill_id / "SKILL.md") if skill_id == "biomaster" else (INTERNAL_SKILL_ROOT / skill_id / "SKILL.md")
        if not skill_file.exists():
            errors.append(f"missing SKILL.md for {skill_id}")
    return errors


def check_exec_scanpy_templates() -> list[str]:
    errors: list[str] = []
    base = INTERNAL_SKILL_ROOT / "exec-scanpy" / "examples"
    for name in ("qc_template.py", "clustering_template.py"):
        if not (base / name).exists():
            errors.append(f"missing exec-scanpy/examples/{name}")
    if (base / "scanpy_template.py").exists():
        errors.append("unexpected exec-scanpy/examples/scanpy_template.py")
    return errors


def check_registry_outputs() -> list[str]:
    text = (INTERNAL_SKILL_ROOT / "registry" / "SKILL.md").read_text(encoding="utf-8")
    return [field for field in REGISTRY_REQUIRED_OUTPUT_FIELDS if f"{field}:" not in text]


def check_plan_manifests() -> list[str]:
    errors: list[str] = []
    plan_dir = INTERNAL_SKILL_ROOT / "plan-scrnaseq-tumor-heterogeneity"
    if not (plan_dir / "IO_CONTRACT.md").exists():
        errors.append("missing IO_CONTRACT.md")
    for index in range(1, 9):
        name = f"{index:02d}_"
        matches = list((plan_dir / "manifests").glob(f"{name}*_contract.md"))
        if not matches:
            errors.append(f"missing manifest starting with {index:02d}_")
    return errors


def check_expected_plan_steps() -> list[str]:
    plan_path = PROJECT_ROOT / "examples/tumor_scrnaseq_heterogeneity/expected_PLAN.yaml"
    plan = yaml.safe_load(plan_path.read_text(encoding="utf-8"))
    steps = plan.get("steps") or []
    if len(steps) != 9:
        return [f"expected_PLAN.yaml must contain 9 steps, found {len(steps)}"]
    expected_ids = [step["step_id"] for step in TUMOR_PIPELINE_STEPS]
    actual_ids = [step["step_id"] for step in steps]
    if actual_ids != expected_ids:
        return [f"step_id mismatch: expected {expected_ids}, got {actual_ids}"]
    return []


def check_agents_and_commands() -> list[str]:
    errors: list[str] = []
    for name in (
        "biomaster-intake.md",
        "biomaster-plan.md",
        "biomaster-execute.md",
        "biomaster-check.md",
        "biomaster-debug.md",
    ):
        if not (AGENT_DIR / name).exists():
            errors.append(f"missing agent {name}")
    for name in (
        "biomaster-start.md",
        "biomaster-plan.md",
        "biomaster-run.md",
        "biomaster-check.md",
        "biomaster-debug.md",
        "biomaster-resume.md",
    ):
        if not (COMMAND_DIR / name).exists():
            errors.append(f"missing command {name}")
    if (AGENT_DIR / "biomaster-verify.md").exists():
        errors.append("legacy agent biomaster-verify.md must not exist")
    return errors


def check_schemas() -> list[str]:
    errors: list[str] = []
    for name in (
        "intake_request.schema.json",
        "planning_request.schema.json",
        "execution_request.schema.json",
        "check_result.schema.json",
        "debug_request.schema.json",
        "debug_result.schema.json",
    ):
        if not (A2A_SCHEMA_DIR / name).exists():
            errors.append(f"missing A2A schema {name}")
    for name in (
        "plan.schema.json",
        "run_state.schema.json",
        "skill_selection.schema.json",
        "step_result.schema.json",
    ):
        if not (BIOM_SCHEMA_DIR / name).exists():
            errors.append(f"missing biomaster schema {name}")
    return errors


def check_sqlite_core_tables() -> list[str]:
    from biomaster.knowledge import connect, table_exists

    db = DEFAULT_DB_PATH
    if not db.exists():
        return ["SQLite database missing; run make knowledge-seed"]
    connection = connect(db)
    try:
        return [
            f"missing SQLite table {table}"
            for table in MVP_CORE_TABLES
            if not table_exists(connection, table)
        ]
    finally:
        connection.close()


def audit_plan_compliance() -> list[str]:
    errors: list[str] = []
    errors.extend(check_mvp_skills())
    errors.extend(check_exec_scanpy_templates())
    errors.extend(check_registry_outputs())
    errors.extend(check_plan_manifests())
    errors.extend(check_expected_plan_steps())
    errors.extend(check_agents_and_commands())
    errors.extend(check_schemas())
    errors.extend(check_sqlite_core_tables())
    return errors
