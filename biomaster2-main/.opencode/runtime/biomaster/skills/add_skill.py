from __future__ import annotations

from pathlib import Path
import argparse
import re

from biomaster.knowledge import DEFAULT_INTERNAL_SKILL_ROOT


TARGETS = {
    "plan": {
        "layer": "plan",
        "prefix": "plan-",
        "required_metadata": "analysis",
        "default_value": "custom",
        "body_heading": "Planning Notes",
    },
    "execute": {
        "layer": "execute",
        "prefix": "exec-",
        "required_metadata": "tool",
        "default_value": "custom-tool",
        "body_heading": "Execution Notes",
    },
    "verify": {
        "layer": "verify",
        "prefix": "verify-",
        "required_metadata": "output",
        "default_value": "custom-output",
        "body_heading": "Verification Notes",
    },
    "debug": {
        "layer": "debug",
        "prefix": "debug-",
        "required_metadata": "failure",
        "default_value": "custom-failure",
        "body_heading": "Debug Notes",
    },
    "report": {
        "layer": "report",
        "prefix": "report-",
        "required_metadata": "domain",
        "default_value": "custom-domain",
        "body_heading": "Report Notes",
    },
}

NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")


def normalize_skill_name(name: str, target: str) -> str:
    value = name.strip().lower().replace("_", "-")
    value = re.sub(r"[^a-z0-9-]+", "-", value)
    value = re.sub(r"-+", "-", value).strip("-")
    if not value:
        raise ValueError("skill name must not be empty")
    prefix = TARGETS[target]["prefix"]
    if not value.startswith(prefix):
        value = prefix + value
    if not NAME_RE.match(value):
        raise ValueError(f"invalid skill name: {value}")
    return value


def create_skill(
    *,
    name: str,
    target: str,
    description: str,
    metadata_value: str | None = None,
    root: Path = DEFAULT_INTERNAL_SKILL_ROOT,
    overwrite: bool = False,
) -> Path:
    if target not in TARGETS:
        raise ValueError(f"unknown target: {target}")
    spec = TARGETS[target]
    skill_name = normalize_skill_name(name, target)
    skill_dir = root / skill_name
    skill_file = skill_dir / "SKILL.md"
    if skill_file.exists() and not overwrite:
        raise FileExistsError(f"skill already exists: {skill_file}")

    skill_dir.mkdir(parents=True, exist_ok=True)
    required_key = spec["required_metadata"]
    required_value = metadata_value or spec["default_value"]
    text = f"""---
name: {skill_name}
description: {description}
compatibility: opencode
metadata:
  layer: {spec["layer"]}
  {required_key}: {required_value}
  status: active
  source: manual
---

# {skill_name}

## {spec["body_heading"]}

Describe when this skill should be selected, what inputs it expects, and what outputs it contributes.

## Integration

- Target: `{target}`
- Sync with: `make knowledge-seed`
- Select through SQLite Skill Finder during the matching phase.
"""
    skill_file.write_text(text, encoding="utf-8")
    return skill_file


def main() -> None:
    parser = argparse.ArgumentParser(description="Create a BioMaster internal skill.")
    parser.add_argument("name", help="Skill name, e.g. custom-qc or exec-custom-qc")
    parser.add_argument("--target", choices=sorted(TARGETS), required=True)
    parser.add_argument("--description", required=True)
    parser.add_argument("--metadata-value", help="Value for the target's required metadata field")
    parser.add_argument("--root", type=Path, default=DEFAULT_INTERNAL_SKILL_ROOT)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    path = create_skill(
        name=args.name,
        target=args.target,
        description=args.description,
        metadata_value=args.metadata_value,
        root=args.root,
        overwrite=args.overwrite,
    )
    print(path)


if __name__ == "__main__":
    main()
