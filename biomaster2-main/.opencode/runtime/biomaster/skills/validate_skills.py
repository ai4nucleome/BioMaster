from __future__ import annotations

from pathlib import Path
import json
import re
from typing import Any

import yaml

try:
    from biomaster.knowledge import DEFAULT_BIOSKILLS_ROOT, DEFAULT_SKILL_ROOT, OPENCODE_ROOT
    from biomaster.mvp import MVP_SKILL_IDS
except ModuleNotFoundError:
    DEFAULT_BIOSKILLS_ROOT = Path(".opencode/bioskills")
    DEFAULT_SKILL_ROOT = Path(".opencode/skills")
    OPENCODE_ROOT = Path(".opencode")
    MVP_SKILL_IDS = frozenset()


NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
VALID_STATUS = {"active", "variant", "deprecated"}
VALID_LAYERS = {"registry", "domain-guide", "discipline", "pipeline", "plan", "execute", "verify", "debug", "env", "report", "bioskill"}


def parse_frontmatter(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise ValueError(f"{path} missing YAML frontmatter")
    end = text.find("\n---", 4)
    if end == -1:
        raise ValueError(f"{path} invalid YAML frontmatter")
    data = yaml.safe_load(text[4:end]) or {}
    if not isinstance(data, dict):
        raise ValueError(f"{path} frontmatter must be a mapping")
    return data


def validate_public_skill_surface() -> None:
    public = {path.name for path in DEFAULT_SKILL_ROOT.iterdir() if path.is_dir()}
    if public != {"biomaster"}:
        raise ValueError(f"public .opencode/skills must expose only biomaster, found: {sorted(public)}")


def validate_bioskill(skill_dir: Path, names: set[str]) -> dict[str, str]:
    skill_file = skill_dir / "SKILL.md"
    if not skill_file.exists():
        raise ValueError(f"{skill_dir} missing SKILL.md")
    meta = parse_frontmatter(skill_file)
    name = meta.get("name")
    description = meta.get("description")
    if not isinstance(name, str) or not name:
        raise ValueError(f"{skill_file} missing name")
    if name != skill_dir.name:
        raise ValueError(f"{skill_file} name does not match directory")
    if not NAME_RE.match(name):
        raise ValueError(f"{skill_file} invalid name: {name}")
    if name in names:
        raise ValueError(f"duplicate BioSkill name: {name}")
    if not isinstance(description, str) or not description.strip():
        raise ValueError(f"{skill_file} missing description")
    if meta.get("status", "active") not in VALID_STATUS:
        raise ValueError(f"{skill_file} invalid status: {meta.get('status')}")
    layer = str(meta.get("biomaster_layer") or meta.get("layer") or "bioskill")
    if layer not in VALID_LAYERS:
        raise ValueError(f"{skill_file} invalid biomaster layer: {layer}")
    for sidecar in ("macro.md", "micro.md"):
        if not (skill_dir / sidecar).exists():
            raise ValueError(f"{skill_dir} missing {sidecar}")
    steps_file = skill_dir / "steps.json"
    if steps_file.exists():
        steps = json.loads(steps_file.read_text(encoding="utf-8"))
        if not isinstance(steps, list):
            raise ValueError(f"{steps_file} must contain a JSON array")
    names.add(name)
    return {"name": name, "layer": layer, "description": description.strip()}


def validate_bioskills_library() -> list[dict[str, str]]:
    if not DEFAULT_BIOSKILLS_ROOT.exists():
        raise ValueError(f"BioSkills root does not exist: {DEFAULT_BIOSKILLS_ROOT}")
    names: set[str] = set()
    skills = [
        validate_bioskill(path, names)
        for path in sorted(DEFAULT_BIOSKILLS_ROOT.iterdir())
        if path.is_dir() and not path.name.startswith(".")
    ]
    if not skills:
        raise ValueError(f"no BioSkills found under {DEFAULT_BIOSKILLS_ROOT}")
    missing = MVP_SKILL_IDS - {skill["name"] for skill in skills}
    if missing:
        raise ValueError(f"missing migrated MVP BioSkills: {', '.join(sorted(missing))}")
    return skills


def validate_bioskills_access_policy() -> None:
    policy = OPENCODE_ROOT / "bioskills-access.yaml"
    data = yaml.safe_load(policy.read_text(encoding="utf-8")) or {}
    roles = data.get("roles") or {}
    if "biomaster-plan" not in roles:
        raise ValueError("bioskills-access.yaml must define biomaster-plan")
    if roles.get("biomaster-execute", {}).get("layer") != "micro":
        raise ValueError("biomaster-execute must receive the micro layer")


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Validate BioMaster OpenCode and BioSkills configuration.")
    parser.add_argument("--mvp", action="store_true", help="Validate the migrated MVP BioSkills surface.")
    args = parser.parse_args()

    validate_public_skill_surface()
    skills = validate_bioskills_library()
    validate_bioskills_access_policy()

    layer_counts: dict[str, int] = {}
    for skill in skills:
        layer_counts[skill["layer"]] = layer_counts.get(skill["layer"], 0) + 1

    print(f"Validated {len(skills)} BioSkills")
    for layer in sorted(layer_counts):
        print(f"- {layer}: {layer_counts[layer]}")


if __name__ == "__main__":
    main()
