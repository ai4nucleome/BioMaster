from __future__ import annotations

from pathlib import Path
import json
import sqlite3
from typing import Any

import yaml

from biomaster.mvp import MVP_REQUIRED_TABLES


PACKAGE_ROOT = Path(__file__).resolve().parents[1]
RUNTIME_ROOT = Path(__file__).resolve().parents[2]
OPENCODE_ROOT = Path(__file__).resolve().parents[3]
PROJECT_ROOT = OPENCODE_ROOT.parent
DEFAULT_DB_PATH = OPENCODE_ROOT / "knowledge" / "biomaster_skills.db"
DEFAULT_SCHEMA_PATH = Path(__file__).resolve().parent / "schema.sql"
DEFAULT_SKILL_ROOT = OPENCODE_ROOT / "skills"
DEFAULT_INTERNAL_SKILL_ROOT = OPENCODE_ROOT / "biomaster-internal" / "skills"
DEFAULT_KNOWLEDGE_ROOT = OPENCODE_ROOT / "knowledge"
DEFAULT_BIOSKILLS_ROOT = OPENCODE_ROOT / "bioskills"
DEFAULT_ACCESS_POLICY_PATH = OPENCODE_ROOT / "bioskills-access.yaml"

REQUIRED_TABLES = MVP_REQUIRED_TABLES

def load_access_policy(policy_path: Path = DEFAULT_ACCESS_POLICY_PATH) -> dict[str, Any]:
    """Load the single fail-closed BioSkills access policy."""
    if not policy_path.exists():
        return {}
    value = yaml.safe_load(policy_path.read_text(encoding="utf-8"))
    return value if isinstance(value, dict) else {}


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item).strip() for item in value if str(item).strip()]


def normalize_agent_name(agent_name: str) -> str:
    aliases = load_access_policy().get("aliases")
    if not isinstance(aliases, dict):
        return agent_name
    normalized = aliases.get(agent_name)
    return str(normalized).strip() if normalized else agent_name


def allowed_agents_for_layer(layer: str) -> str:
    layer_agents = load_access_policy().get("layer_agents")
    if not isinstance(layer_agents, dict):
        return ""
    return ",".join(_string_list(layer_agents.get(layer)))


def allowed_agents_for_record_type(record_type: str) -> str:
    record_agents = load_access_policy().get("record_agents")
    if not isinstance(record_agents, dict):
        return ""
    return ",".join(_string_list(record_agents.get(record_type)))


def connect(db_path: Path = DEFAULT_DB_PATH) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def load_schema(schema_path: Path = DEFAULT_SCHEMA_PATH) -> str:
    return schema_path.read_text(encoding="utf-8")


def table_exists(connection: sqlite3.Connection, table_name: str) -> bool:
    row = connection.execute(
        "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = ?",
        (table_name,),
    ).fetchone()
    return row is not None


def ensure_schema(connection: sqlite3.Connection, schema_path: Path = DEFAULT_SCHEMA_PATH) -> None:
    connection.executescript(load_schema(schema_path))
    migrate_schema(connection)
    connection.commit()


def migrate_schema(connection: sqlite3.Connection) -> None:
    skill_columns = {row[1] for row in connection.execute("PRAGMA table_info(skills)")}
    if "body" not in skill_columns:
        connection.execute("ALTER TABLE skills ADD COLUMN body TEXT")

    if table_exists(connection, "knowledge_records"):
        record_columns = {row[1] for row in connection.execute("PRAGMA table_info(knowledge_records)")}
        if "content" not in record_columns:
            connection.execute("ALTER TABLE knowledge_records ADD COLUMN content TEXT")
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS sync_meta (
          key TEXT PRIMARY KEY,
          value TEXT NOT NULL,
          updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """
    )


def json_dumps(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True)


def json_loads(value: str | None, default: Any) -> Any:
    if not value:
        return default
    return json.loads(value)


def row_to_dict(row: sqlite3.Row) -> dict[str, Any]:
    return {key: row[key] for key in row.keys()}


def _count_rows(db_path: Path, table_name: str) -> int:
    if not db_path.exists():
        return 0
    connection = sqlite3.connect(db_path)
    try:
        if not table_exists(connection, table_name):
            return 0
        row = connection.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()
        return int(row[0]) if row else 0
    finally:
        connection.close()


def _meta_value(db_path: Path, key: str) -> str | None:
    if not db_path.exists():
        return None
    connection = sqlite3.connect(db_path)
    try:
        if not table_exists(connection, "sync_meta"):
            return None
        row = connection.execute("SELECT value FROM sync_meta WHERE key = ?", (key,)).fetchone()
        return str(row[0]) if row else None
    finally:
        connection.close()


def knowledge_db_ready(db_path: Path = DEFAULT_DB_PATH) -> bool:
    if not db_path.exists():
        return False
    connection = sqlite3.connect(db_path)
    try:
        existing_tables = {
            row[0]
            for row in connection.execute("SELECT name FROM sqlite_master WHERE type = 'table'")
        }
        if not set(REQUIRED_TABLES).issubset(existing_tables):
            return False
    finally:
        connection.close()
    if _count_rows(db_path, "skills") == 0 or _count_rows(db_path, "pipeline_routes") == 0:
        return False
    from biomaster.knowledge.sync_skills import bioskills_signature

    synced_root = _meta_value(db_path, "bioskills_root")
    if synced_root and synced_root != str(DEFAULT_BIOSKILLS_ROOT):
        return True
    return _meta_value(db_path, "bioskills_signature") == bioskills_signature()


def ensure_knowledge_db(db_path: Path = DEFAULT_DB_PATH) -> dict[str, Any]:
    """Ensure the generated SQLite control plane exists and is queryable."""

    if knowledge_db_ready(db_path):
        return {"db_path": str(db_path), "created_or_synced": False}

    from biomaster.knowledge.seed_routes import seed_routes
    from biomaster.knowledge.sync_all import sync_all

    stats = sync_all(db_path=db_path)
    route_count = seed_routes(db_path)
    return {
        "db_path": str(db_path),
        "created_or_synced": True,
        "skills_synced": stats.get("synced", 0),
        "routes_seeded": route_count,
    }
