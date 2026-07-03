from __future__ import annotations

from pathlib import Path
import argparse
import hashlib
import json
from datetime import datetime, timezone

from biomaster.knowledge import (
    DEFAULT_DB_PATH,
    DEFAULT_INTERNAL_SKILL_ROOT,
    DEFAULT_SKILL_ROOT,
    allowed_agents_for_layer,
    connect,
    ensure_schema,
    json_dumps,
)
from biomaster.skills.manager import parse_skill_file


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def content_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def io_contract_path(skill_dir: Path, project_root: Path) -> str | None:
    contract = skill_dir / "IO_CONTRACT.md"
    if contract.exists():
        return relative_or_absolute(contract, project_root)
    return None


def manifest_dir(skill_dir: Path, project_root: Path) -> str | None:
    manifest = skill_dir / "manifests"
    if manifest.exists() and manifest.is_dir():
        return relative_or_absolute(manifest, project_root)
    return None


def relative_or_absolute(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def build_skill_row(skill_dir: Path, project_root: Path) -> dict[str, object]:
    skill = parse_skill_file(skill_dir / "SKILL.md")
    relative_path = relative_or_absolute(skill.path, project_root)
    tags = skill.aliases
    extra: dict[str, object] = {}
    manifest = manifest_dir(skill_dir, project_root)
    if manifest:
        extra["manifest_dir"] = manifest
    if skill.metadata.get("analysis"):
        extra["analysis"] = skill.metadata["analysis"]
    if skill.metadata.get("source"):
        extra["source"] = skill.metadata["source"]
    if skill.metadata.get("status"):
        extra["status"] = skill.metadata["status"]

    io_path = io_contract_path(skill_dir, project_root)
    body_text = skill.path.read_text(encoding="utf-8")
    return {
        "skill_id": skill.name,
        "path": relative_path,
        "layer": skill.layer or skill.metadata.get("layer", "unknown"),
        "domain": skill.metadata.get("domain"),
        "discipline": skill.metadata.get("discipline") or skill.metadata.get("analysis"),
        "pipeline": skill.metadata.get("pipeline"),
        "tool": skill.metadata.get("tool"),
        "description": skill.description,
        "tags": ",".join(tags) if tags else None,
        "allowed_agents": allowed_agents_for_layer(skill.layer),
        "insertion_mode": "full",
        "enabled": 1 if skill.metadata.get("status", "active") == "active" else 0,
        "priority": 10 if skill.metadata.get("source", "manual") == "manual" else 0,
        "io_contract": io_path,
        "env_contract": skill.metadata.get("env_contract"),
        "extra_json": json_dumps(extra) if extra else None,
        "content_hash": content_hash(body_text),
        "body": body_text,
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


def iter_skill_dirs(skill_roots: list[Path]) -> list[Path]:
    dirs: list[Path] = []
    for root in skill_roots:
        if not root.exists():
            continue
        dirs.extend(path for path in sorted(root.iterdir()) if path.is_dir())
    return dirs


def sync_skills(
    skill_root: Path = DEFAULT_SKILL_ROOT,
    db_path: Path = DEFAULT_DB_PATH,
    *,
    skill_roots: list[Path] | None = None,
    project_root: Path | None = None,
) -> dict[str, int]:
    project_root = project_root or DEFAULT_SKILL_ROOT.parents[1]
    active_roots = skill_roots or [skill_root, DEFAULT_INTERNAL_SKILL_ROOT]
    connection = connect(db_path)
    try:
        ensure_schema(connection)
        synced = 0
        synced_ids: list[str] = []
        for skill_dir in iter_skill_dirs(active_roots):
            skill_file = skill_dir / "SKILL.md"
            if not skill_file.exists():
                continue
            row = build_skill_row(skill_dir, project_root)
            upsert_skill(connection, row)
            synced_ids.append(str(row["skill_id"]))
            synced += 1
        if synced_ids:
            placeholders = ",".join("?" for _ in synced_ids)
            connection.execute(f"DELETE FROM skills WHERE skill_id NOT IN ({placeholders})", tuple(synced_ids))
        connection.commit()
        total = connection.execute("SELECT COUNT(*) FROM skills").fetchone()[0]
        enabled = connection.execute("SELECT COUNT(*) FROM skills WHERE enabled = 1").fetchone()[0]
        return {"synced": synced, "total": total, "enabled": enabled}
    finally:
        connection.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Sync OpenCode SKILL.md files into SQLite.")
    parser.add_argument("--db", type=Path, default=DEFAULT_DB_PATH)
    parser.add_argument("--skill-root", type=Path, default=DEFAULT_SKILL_ROOT)
    args = parser.parse_args()

    stats = sync_skills(args.skill_root, args.db)
    print(f"Synced {stats['synced']} skills into {args.db}")
    print(f"Total skills: {stats['total']} (enabled: {stats['enabled']})")


if __name__ == "__main__":
    main()
