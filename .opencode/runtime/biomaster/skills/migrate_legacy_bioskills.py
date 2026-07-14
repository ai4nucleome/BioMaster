from __future__ import annotations

from pathlib import Path
import argparse
import json
import re
import shutil
from typing import Any

import yaml

from biomaster.knowledge import DEFAULT_BIOSKILLS_ROOT, DEFAULT_INTERNAL_SKILL_ROOT, DEFAULT_SKILL_ROOT, OPENCODE_ROOT


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.strip().lower()).strip("-")
    if not slug:
        raise ValueError(f"invalid skill name: {value!r}")
    return slug


def split_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    if not text.startswith("---\n"):
        return {}, text
    end = text.find("\n---", 4)
    if end == -1:
        return {}, text
    raw = text[4:end]
    body = text[end + 4 :].lstrip("\n")
    data = yaml.safe_load(raw) or {}
    return data if isinstance(data, dict) else {}, body


def title_case(slug: str) -> str:
    return " ".join(part.capitalize() for part in slug.split("-") if part)


def to_list(*values: Any) -> list[str]:
    result: list[str] = []
    for value in values:
        if isinstance(value, list):
            result.extend(str(item).strip() for item in value if str(item).strip())
        elif isinstance(value, str) and value.strip():
            result.extend(item.strip() for item in value.split(",") if item.strip())
    return list(dict.fromkeys(result))


def frontmatter(fields: dict[str, Any]) -> str:
    return "---\n" + yaml.safe_dump(fields, sort_keys=False, allow_unicode=True).strip() + "\n---\n"


def convert_skill(skill_file: Path, target_root: Path) -> str:
    text = skill_file.read_text(encoding="utf-8")
    data, body = split_frontmatter(text)
    metadata = data.get("metadata") if isinstance(data.get("metadata"), dict) else {}
    name = slugify(str(data.get("name") or metadata.get("name") or skill_file.parent.name))
    layer = str(metadata.get("layer") or data.get("layer") or "bioskill")
    domain = str(metadata.get("domain") or data.get("domain") or "bioinformatics")
    tool = str(metadata.get("tool") or data.get("primary_tool") or data.get("tool") or "")
    discipline = str(metadata.get("discipline") or metadata.get("analysis") or "")
    pipeline = str(metadata.get("pipeline") or "")
    description = str(data.get("description") or metadata.get("description") or name)
    tags = to_list(layer, domain, discipline, pipeline, tool, metadata.get("tags"), data.get("aliases"))

    target = target_root / name
    target.mkdir(parents=True, exist_ok=True)
    rel_source = skill_file.relative_to(OPENCODE_ROOT.parent).as_posix()
    fm = {
        "name": name,
        "description": description,
        "domain": domain,
        "primary_tool": tool,
        "methods": [tool] if tool else [],
        "macro_tags": [tag for tag in tags if tag],
        "micro_tags": [tag for tag in tags if tag],
        "source": f"legacy:{rel_source}",
        "status": str(metadata.get("status") or data.get("status") or "active"),
        "enabled": True,
        "custom": False,
        "biomaster_layer": layer,
        "discipline": discipline,
        "pipeline": pipeline,
    }
    (target / "SKILL.md").write_text(frontmatter(fm) + f"\n# {title_case(name)}\n", encoding="utf-8")
    macro = "\n\n".join(
        [
            f"# {title_case(name)}",
            "## Overview",
            description,
            "## Legacy BioMaster Control Notes",
            body.strip() or description,
        ]
    ).strip()
    micro = "\n\n".join(
        [
            f"# {title_case(name)}",
            "## Operational Notes",
            body.strip() or description,
        ]
    ).strip()
    (target / "macro.md").write_text(macro + "\n", encoding="utf-8")
    (target / "micro.md").write_text(micro + "\n", encoding="utf-8")
    (target / "steps.json").write_text(
        json.dumps(
            [
                {
                    "id": slugify(layer or "control"),
                    "title": title_case(layer or "control"),
                    "tags": [tag for tag in tags if tag],
                }
            ],
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    for child in skill_file.parent.iterdir():
        if child.name == "SKILL.md":
            continue
        dest = target / child.name
        if child.is_dir():
            if dest.exists():
                shutil.rmtree(dest)
            shutil.copytree(child, dest)
        elif child.is_file():
            shutil.copy2(child, dest)
    return name


def iter_legacy_skill_files(skill_root: Path, internal_root: Path) -> list[Path]:
    files: list[Path] = []
    if skill_root.exists():
        files.extend(path / "SKILL.md" for path in sorted(skill_root.iterdir()) if (path / "SKILL.md").exists())
    if internal_root.exists():
        files.extend(path / "SKILL.md" for path in sorted(internal_root.iterdir()) if (path / "SKILL.md").exists())
    return files


def migrate_legacy_bioskills(
    *,
    skill_root: Path = DEFAULT_SKILL_ROOT,
    internal_root: Path = DEFAULT_INTERNAL_SKILL_ROOT,
    target_root: Path = DEFAULT_BIOSKILLS_ROOT,
) -> list[str]:
    target_root.mkdir(parents=True, exist_ok=True)
    migrated: list[str] = []
    for skill_file in iter_legacy_skill_files(skill_root, internal_root):
        migrated.append(convert_skill(skill_file, target_root))
    return migrated


def main() -> None:
    parser = argparse.ArgumentParser(description="Migrate legacy BioMaster SKILL.md files into .opencode/bioskills.")
    parser.add_argument("--skill-root", type=Path, default=DEFAULT_SKILL_ROOT)
    parser.add_argument("--internal-root", type=Path, default=DEFAULT_INTERNAL_SKILL_ROOT)
    parser.add_argument("--target-root", type=Path, default=DEFAULT_BIOSKILLS_ROOT)
    args = parser.parse_args()
    migrated = migrate_legacy_bioskills(
        skill_root=args.skill_root,
        internal_root=args.internal_root,
        target_root=args.target_root,
    )
    print(f"Migrated {len(migrated)} legacy skills into {args.target_root}")
    for name in migrated:
        print(f"- {name}")


if __name__ == "__main__":
    main()
