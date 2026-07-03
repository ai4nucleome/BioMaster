from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

try:
    from biomaster.knowledge import DEFAULT_SKILL_ROOT, PROJECT_ROOT
    from biomaster.skills.manager import SkillCatalog
except ModuleNotFoundError:
    from manager import SkillCatalog


BIOMASTER_SKILL_ROOT = PROJECT_ROOT
SKILL_ROOT = DEFAULT_SKILL_ROOT
INDEX_PATH = SKILL_ROOT / "index.yaml"


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


def skill_index_entry(skill_dir: Path) -> dict[str, Any]:
    skill_file = skill_dir / "SKILL.md"
    if not skill_file.exists():
        raise ValueError(f"{skill_dir} missing SKILL.md")

    meta = parse_frontmatter(skill_file)
    metadata = meta.get("metadata") or {}
    if not isinstance(metadata, dict):
        raise ValueError(f"{skill_file} metadata must be a mapping")

    entry: dict[str, Any] = {
        "name": meta.get("name"),
        "layer": metadata.get("layer"),
        "path": skill_file.relative_to(BIOMASTER_SKILL_ROOT).as_posix(),
        "description": meta.get("description"),
        "source": metadata.get("source", "manual"),
        "status": metadata.get("status", "active"),
    }

    for key in (
        "domain",
        "analysis",
        "tool",
        "output",
        "failure",
        "canonical",
        "aliases",
        "origin_source",
        "origin_page",
    ):
        if key in metadata:
            entry[key] = metadata[key]

    return entry


def main() -> None:
    if not SKILL_ROOT.exists():
        raise ValueError(f"skill root does not exist: {SKILL_ROOT}")

    catalog = SkillCatalog.from_root(SKILL_ROOT)
    reference_errors = catalog.validate_references()
    if reference_errors:
        raise ValueError("skill reference validation failed:\n" + "\n".join(reference_errors))

    entries = [
        skill_index_entry(skill_dir)
        for skill_dir in sorted(path for path in SKILL_ROOT.iterdir() if path.is_dir())
    ]
    if not entries:
        raise ValueError(f"no skills found under {SKILL_ROOT}")

    INDEX_PATH.write_text(
        yaml.safe_dump({"skills": entries}, sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )
    print(f"Wrote {len(entries)} skills to {INDEX_PATH}")


if __name__ == "__main__":
    main()
