from __future__ import annotations

from pathlib import Path
import argparse
import hashlib
import json
from datetime import datetime, timezone
from typing import Any

import yaml

from biomaster.knowledge import (
    DEFAULT_ACCESS_POLICY_PATH,
    DEFAULT_BIOSKILLS_ROOT,
    DEFAULT_DB_PATH,
    OPENCODE_ROOT,
    allowed_agents_for_layer,
    connect,
    ensure_schema,
    json_dumps,
)


BIOSKILL_FILES = ("SKILL.md", "macro.md", "micro.md", "steps.json")


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def content_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def relative_or_absolute(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def read_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return default


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


def to_list(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    if isinstance(value, str):
        return [item.strip() for item in value.split(",") if item.strip()]
    return []


def bioskills_signature(bioskills_root: Path = DEFAULT_BIOSKILLS_ROOT) -> str:
    parts: list[str] = []
    if not bioskills_root.exists():
        return content_hash("")
    for skill_dir in sorted(path for path in bioskills_root.iterdir() if path.is_dir()):
        for name in BIOSKILL_FILES:
            path = skill_dir / name
            if path.exists():
                stat = path.stat()
                parts.append(f"{skill_dir.name}/{name}:{stat.st_mtime_ns}:{stat.st_size}")
    if DEFAULT_ACCESS_POLICY_PATH.exists():
        stat = DEFAULT_ACCESS_POLICY_PATH.stat()
        parts.append(f"bioskills-access.yaml:{stat.st_mtime_ns}:{stat.st_size}")
    return content_hash("|".join(parts))


def infer_layer(skill_id: str, metadata: dict[str, Any], macro: str, micro: str) -> str:
    explicit = metadata.get("biomaster_layer") or metadata.get("layer")
    if isinstance(explicit, str) and explicit.strip():
        return explicit.strip()
    prefixes = (
        ("registry", "registry"),
        ("domain-guide-", "domain-guide"),
        ("discipline-", "discipline"),
        ("pipeline-", "pipeline"),
        ("plan-", "plan"),
        ("exec-", "execute"),
        ("verify-", "verify"),
        ("debug-", "debug"),
        ("env-", "env"),
        ("report-", "report"),
    )
    for prefix, layer in prefixes:
        if skill_id == prefix or skill_id.startswith(prefix):
            return layer
    if micro.strip():
        return "bioskill"
    if macro.strip():
        return "plan"
    return "bioskill"


def read_bioskill(skill_dir: Path, project_root: Path) -> dict[str, object] | None:
    skill_file = skill_dir / "SKILL.md"
    if not skill_file.exists():
        return None

    skill_text = read_text(skill_file)
    metadata, skill_body = split_frontmatter(skill_text)
    skill_id = str(metadata.get("name") or skill_dir.name)
    macro = read_text(skill_dir / "macro.md")
    micro = read_text(skill_dir / "micro.md")
    steps = read_json(skill_dir / "steps.json", [])
    if not isinstance(steps, list):
        steps = []

    macro_tags = to_list(metadata.get("macro_tags") or metadata.get("macroTags"))
    micro_tags = to_list(metadata.get("micro_tags") or metadata.get("microTags"))
    methods = to_list(metadata.get("methods"))
    step_tags = [
        str(tag).strip()
        for step in steps
        if isinstance(step, dict)
        for tag in to_list(step.get("tags"))
        if str(tag).strip()
    ]
    tags = list(dict.fromkeys([*macro_tags, *micro_tags, *methods, *step_tags]))
    layer = infer_layer(skill_id, metadata, macro, micro)
    enabled = metadata.get("enabled")
    status = str(metadata.get("status") or "active")
    body = "\n\n".join(part.strip() for part in [skill_body, macro, micro] if part.strip())
    source_path = relative_or_absolute(skill_file, project_root)
    io_contract = skill_dir / "IO_CONTRACT.md"
    manifest_dir = skill_dir / "manifests"
    extra = {
        "source_kind": "bioskill",
        "source": metadata.get("source"),
        "custom": metadata.get("custom") is True or str(metadata.get("custom")).lower() == "true",
        "methods": methods,
        "macro_tags": macro_tags,
        "micro_tags": micro_tags,
        "steps": steps,
        "macro_bytes": len(macro.encode("utf-8")),
        "micro_bytes": len(micro.encode("utf-8")),
        "body_bytes": len(body.encode("utf-8")),
        "search_text_hash": content_hash(body),
    }
    if manifest_dir.exists() and manifest_dir.is_dir():
        extra["manifest_dir"] = relative_or_absolute(manifest_dir, project_root)
    return {
        "skill_id": skill_id,
        "path": source_path,
        "layer": layer,
        "domain": metadata.get("domain"),
        "discipline": metadata.get("discipline") or metadata.get("domain"),
        "pipeline": metadata.get("pipeline"),
        "tool": metadata.get("primary_tool") or metadata.get("primaryTool") or metadata.get("tool"),
        "description": str(metadata.get("description") or skill_id),
        "tags": ",".join(tags) if tags else None,
        "allowed_agents": allowed_agents_for_layer(layer),
        "insertion_mode": "layered",
        "enabled": 0 if enabled is False or status != "active" else 1,
        "priority": 20 if extra["custom"] else 10,
        "io_contract": relative_or_absolute(io_contract, project_root) if io_contract.exists() else None,
        "env_contract": metadata.get("env_contract"),
        "extra_json": json_dumps(extra),
        "content_hash": content_hash(skill_text + macro + micro + json.dumps(steps, sort_keys=True)),
        "body": body,
        "updated_at": utc_now(),
    }


def upsert_skill(connection, row: dict[str, object]) -> None:
    connection.execute(
        """
        INSERT INTO skills (
          skill_id, path, layer, domain, discipline, pipeline, tool,
          description, tags, allowed_agents, insertion_mode, enabled, priority,
          io_contract, env_contract, extra_json, content_hash, body, updated_at
        ) VALUES (
          :skill_id, :path, :layer, :domain, :discipline, :pipeline, :tool,
          :description, :tags, :allowed_agents, :insertion_mode, :enabled, :priority,
          :io_contract, :env_contract, :extra_json, :content_hash, :body, :updated_at
        )
        ON CONFLICT(skill_id) DO UPDATE SET
          path = excluded.path,
          layer = excluded.layer,
          domain = excluded.domain,
          discipline = excluded.discipline,
          pipeline = excluded.pipeline,
          tool = excluded.tool,
          description = excluded.description,
          tags = excluded.tags,
          allowed_agents = excluded.allowed_agents,
          insertion_mode = excluded.insertion_mode,
          enabled = excluded.enabled,
          priority = excluded.priority,
          io_contract = excluded.io_contract,
          env_contract = excluded.env_contract,
          extra_json = excluded.extra_json,
          content_hash = excluded.content_hash,
          body = excluded.body,
          updated_at = excluded.updated_at
        """,
        row,
    )


def iter_bioskill_dirs(bioskills_root: Path) -> list[Path]:
    if not bioskills_root.exists():
        return []
    return [
        path
        for path in sorted(bioskills_root.iterdir())
        if path.is_dir() and not path.name.startswith(".") and (path / "SKILL.md").exists()
    ]


def write_sync_meta(connection, key: str, value: str) -> None:
    connection.execute(
        """
        INSERT INTO sync_meta (key, value, updated_at)
        VALUES (?, ?, ?)
        ON CONFLICT(key) DO UPDATE SET
          value = excluded.value,
          updated_at = excluded.updated_at
        """,
        (key, value, utc_now()),
    )


def sync_skills(
    skill_root: Path = DEFAULT_BIOSKILLS_ROOT,
    db_path: Path = DEFAULT_DB_PATH,
    *,
    skill_roots: list[Path] | None = None,
    project_root: Path | None = None,
) -> dict[str, int]:
    """Sync the file-backed BioSkills library into the BioMaster SQLite cache."""

    bioskills_root = (skill_roots or [skill_root])[0]
    project_root = project_root or OPENCODE_ROOT.parent
    signature = bioskills_signature(bioskills_root)
    connection = connect(db_path)
    try:
        ensure_schema(connection)
        synced = 0
        rows: list[dict[str, object]] = []
        for skill_dir in iter_bioskill_dirs(bioskills_root):
            row = read_bioskill(skill_dir, project_root)
            if row is None:
                continue
            rows.append(row)
            synced += 1

        connection.execute("DELETE FROM skills")
        for row in rows:
            upsert_skill(connection, row)

        write_sync_meta(connection, "bioskills_root", str(bioskills_root))
        write_sync_meta(connection, "bioskills_signature", signature)
        connection.commit()
        total = connection.execute("SELECT COUNT(*) FROM skills").fetchone()[0]
        enabled = connection.execute("SELECT COUNT(*) FROM skills WHERE enabled = 1").fetchone()[0]
        return {"synced": synced, "total": total, "enabled": enabled}
    finally:
        connection.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Sync BioSkills into the BioMaster SQLite control cache.")
    parser.add_argument("--db", type=Path, default=DEFAULT_DB_PATH)
    parser.add_argument("--skill-root", type=Path, default=DEFAULT_BIOSKILLS_ROOT)
    args = parser.parse_args()

    stats = sync_skills(args.skill_root, args.db)
    print(f"BioSkills synced: {stats['synced']} into {args.db}")
    print(f"Total skills: {stats['total']} (enabled: {stats['enabled']})")


if __name__ == "__main__":
    main()
