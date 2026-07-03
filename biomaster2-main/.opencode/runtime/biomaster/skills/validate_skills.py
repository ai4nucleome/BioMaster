from __future__ import annotations

from pathlib import Path
import json
import re
from typing import Any

import yaml

try:
    from biomaster.mvp import MVP_SKILL_IDS
    from biomaster.knowledge import DEFAULT_INTERNAL_SKILL_ROOT, DEFAULT_KNOWLEDGE_ROOT, DEFAULT_SKILL_ROOT, PROJECT_ROOT
    from biomaster.skills.manager import (
        AgentSkillAccessPolicy,
        KnowledgeRegistry,
        SkillCatalog,
    )
except ModuleNotFoundError:
    from manager import AgentSkillAccessPolicy, KnowledgeRegistry, SkillCatalog

    MVP_SKILL_IDS = frozenset()


BIOMASTER_SKILL_ROOT = PROJECT_ROOT
SKILL_ROOT = DEFAULT_SKILL_ROOT
INTERNAL_SKILL_ROOT = DEFAULT_INTERNAL_SKILL_ROOT
KNOWLEDGE_ROOT = DEFAULT_KNOWLEDGE_ROOT
BIOMASTER_REPO_ROOT = BIOMASTER_SKILL_ROOT.parent
PLAN_KNOWLEDGE = BIOMASTER_REPO_ROOT / "doc" / "Plan_Knowledge.json"
TASK_KNOWLEDGE = BIOMASTER_REPO_ROOT / "doc" / "Task_Knowledge.json"
TARGET_WORKFLOW_RECORDS = 56
TARGET_TASK_RECORDS = 76
NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
VALID_LAYERS = {
    "registry",
    "domain-guide",
    "discipline",
    "pipeline",
    "plan",
    "execute",
    "verify",
    "debug",
    "env",
    "report",
}
VALID_STATUS = {"active", "variant", "deprecated"}
REQUIRED_LAYER_METADATA = {
    "domain-guide": "domain",
    "discipline": "discipline",
    "pipeline": "pipeline",
    "plan": "analysis",
    "execute": "tool",
    "verify": "output",
    "debug": "failure",
    "env": "env_contract",
    "report": "domain",
}


def parse_frontmatter(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise ValueError(f"{path} missing YAML frontmatter")

    parts = text.split("---", 2)
    if len(parts) < 3 or not parts[1].strip():
        raise ValueError(f"{path} invalid YAML frontmatter")

    data = yaml.safe_load(parts[1])
    if not isinstance(data, dict):
        raise ValueError(f"{path} frontmatter must be a mapping")
    return data


def validate_skill(skill_dir: Path, names: set[str]) -> dict[str, Any]:
    skill_file = skill_dir / "SKILL.md"
    if not skill_file.exists():
        raise ValueError(f"{skill_dir} missing SKILL.md")

    meta = parse_frontmatter(skill_file)
    name = meta.get("name")
    description = meta.get("description")
    metadata = meta.get("metadata") or {}

    if not name:
        raise ValueError(f"{skill_file} missing name")
    if not isinstance(name, str):
        raise ValueError(f"{skill_file} name must be a string")
    if not description or not isinstance(description, str) or not description.strip():
        raise ValueError(f"{skill_file} missing description")
    if name != skill_dir.name:
        raise ValueError(f"{skill_file} name does not match directory")
    if not NAME_RE.match(name):
        raise ValueError(f"{skill_file} invalid name: {name}")
    if name in names:
        raise ValueError(f"duplicate skill name: {name}")

    if not isinstance(metadata, dict):
        raise ValueError(f"{skill_file} metadata must be a mapping")
    layer = metadata.get("layer")
    if layer not in VALID_LAYERS:
        raise ValueError(f"{skill_file} invalid metadata.layer: {layer}")

    for key, value in metadata.items():
        if not isinstance(key, str) or not isinstance(value, str):
            raise ValueError(f"{skill_file} metadata values must be strings")

    status = metadata.get("status", "active")
    if status not in VALID_STATUS:
        raise ValueError(f"{skill_file} invalid metadata.status: {status}")

    required_key = REQUIRED_LAYER_METADATA.get(layer)
    if required_key and not metadata.get(required_key):
        raise ValueError(f"{skill_file} missing metadata.{required_key} for {layer} skill")

    names.add(name)
    return {"name": name, "layer": layer, "description": description.strip()}


def validate_canonical_metadata(catalog: SkillCatalog) -> None:
    for skill in catalog.list():
        canonical = skill.metadata.get("canonical")
        if canonical and canonical not in {item.name for item in catalog.list()}:
            raise ValueError(f"{skill.name} references unknown canonical skill: {canonical}")


def validate_references() -> None:
    catalog = SkillCatalog.from_roots([SKILL_ROOT, INTERNAL_SKILL_ROOT])
    errors = catalog.validate_references()
    if errors:
        raise ValueError("skill reference validation failed:\n" + "\n".join(errors))

def validate_agent_access_policy() -> None:
    policy = AgentSkillAccessPolicy.from_file()
    errors = policy.validate(VALID_LAYERS)
    if errors:
        raise ValueError("agent skill access policy validation failed:\n" + "\n".join(errors))


def source_json_count(path: Path) -> int:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError(f"{path} must contain a JSON array")
    return len(data)


def validate_numbered_knowledge_library() -> None:
    catalog = SkillCatalog.from_roots([SKILL_ROOT, INTERNAL_SKILL_ROOT])
    workflows = KnowledgeRegistry.workflows(KNOWLEDGE_ROOT)
    tasks = KnowledgeRegistry.tasks(KNOWLEDGE_ROOT)

    source_workflow_entries = source_json_count(PLAN_KNOWLEDGE)
    source_task_entries = source_json_count(TASK_KNOWLEDGE)
    if len(workflows.list()) != TARGET_WORKFLOW_RECORDS:
        raise ValueError(f"workflow registry count mismatch: {len(workflows.list())} != {TARGET_WORKFLOW_RECORDS}")
    if len(tasks.list()) != TARGET_TASK_RECORDS:
        raise ValueError(f"task registry count mismatch: {len(tasks.list())} != {TARGET_TASK_RECORDS}")
    workflow_source_entries = {int(record.metadata.get("source_entry_index", "0")) for record in workflows.list()}
    task_source_entries = {int(record.metadata.get("source_entry_index", "0")) for record in tasks.list()}
    if workflow_source_entries != set(range(1, source_workflow_entries + 1)):
        raise ValueError("workflow records do not cover every Plan_Knowledge source entry")
    if task_source_entries != set(range(1, source_task_entries + 1)):
        raise ValueError("task records do not cover every Task_Knowledge source entry")

    for record in workflows.list():
        if not record.path.exists():
            raise ValueError(f"workflow record path does not exist: {record.path}")
        skill_name = record.metadata.get("canonical_plan_skill")
        if not skill_name:
            raise ValueError(f"workflow record missing canonical_plan_skill: {record.record_id}")
        if catalog.get(skill_name).layer != "plan":
            raise ValueError(f"workflow record references non-plan skill: {record.record_id} -> {skill_name}")

    for record in tasks.list():
        if not record.path.exists():
            raise ValueError(f"task record path does not exist: {record.path}")
        skill_name = record.metadata.get("canonical_exec_skill")
        if not skill_name:
            raise ValueError(f"task record missing canonical_exec_skill: {record.record_id}")
        if catalog.get(skill_name).layer != "execute":
            raise ValueError(f"task record references non-execute skill: {record.record_id} -> {skill_name}")

def validate_mvp_skill_set(skill_names: set[str]) -> None:
    missing = MVP_SKILL_IDS - skill_names
    if missing:
        raise ValueError(f"missing MVP skills: {', '.join(sorted(missing))}")


def validate_public_skill_surface() -> None:
    public = {path.name for path in SKILL_ROOT.iterdir() if path.is_dir()}
    if public != {"biomaster"}:
        raise ValueError(f"public .opencode/skills must expose only biomaster, found: {sorted(public)}")


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Validate OpenCode skills.")
    parser.add_argument("--mvp", action="store_true", help="Validate the public/internal skill surface.")
    args = parser.parse_args()

    if not SKILL_ROOT.exists():
        raise ValueError(f"skill root does not exist: {SKILL_ROOT}")

    names: set[str] = set()
    skills = []
    for root in (SKILL_ROOT, INTERNAL_SKILL_ROOT):
        if not root.exists():
            continue
        for skill_dir in sorted(path for path in root.iterdir() if path.is_dir()):
            skills.append(validate_skill(skill_dir, names))

    if not skills:
        raise ValueError(f"no skills found under {SKILL_ROOT}")

    if args.mvp:
        validate_public_skill_surface()
        validate_mvp_skill_set(names)

    validate_references()
    validate_canonical_metadata(SkillCatalog.from_roots([SKILL_ROOT, INTERNAL_SKILL_ROOT]))
    validate_agent_access_policy()
    if not args.mvp:
        validate_numbered_knowledge_library()

    layer_counts: dict[str, int] = {}
    for skill in skills:
        layer_counts[skill["layer"]] = layer_counts.get(skill["layer"], 0) + 1

    print(f"Validated {len(skills)} skills")
    for layer in sorted(layer_counts):
        print(f"- {layer}: {layer_counts[layer]}")


if __name__ == "__main__":
    main()
