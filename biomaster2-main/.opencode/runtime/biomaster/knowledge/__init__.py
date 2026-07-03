from __future__ import annotations

from pathlib import Path
import json
import sqlite3
from typing import Any

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
TARGET_WORKFLOW_RECORDS = 56
TARGET_TASK_RECORDS = 76

REQUIRED_TABLES = MVP_REQUIRED_TABLES

AGENT_ALIASES = {
    "intake-agent": "biomaster-intake",
    "plan-agent": "biomaster-plan",
    "execute-agent": "biomaster-execute",
    "check-agent": "biomaster-check",
    "verify-agent": "biomaster-check",
    "debug-agent": "biomaster-debug",
}

LAYER_ALLOWED_AGENTS: dict[str, list[str]] = {
    "registry": ["biomaster-intake", "biomaster-plan"],
    "domain-guide": ["biomaster-intake", "biomaster-plan"],
    "discipline": ["biomaster-intake", "biomaster-plan"],
    "pipeline": ["biomaster-intake", "biomaster-plan"],
    "plan": ["biomaster-plan"],
    "exec": ["biomaster-execute", "biomaster-debug"],
    "execute": ["biomaster-execute", "biomaster-debug"],
    "verify": ["biomaster-check", "biomaster-execute", "biomaster-debug"],
    "debug": ["biomaster-debug"],
    "env": ["biomaster-execute", "biomaster-debug"],
    "report": ["biomaster-plan", "biomaster-debug"],
}

KNOWLEDGE_RECORD_AGENTS: dict[str, list[str]] = {
    "workflow": ["biomaster-intake", "biomaster-plan"],
    "task": ["biomaster-execute", "biomaster-debug"],
}


def normalize_agent_name(agent_name: str) -> str:
    return AGENT_ALIASES.get(agent_name, agent_name)


def allowed_agents_for_layer(layer: str) -> str:
    agents = LAYER_ALLOWED_AGENTS.get(layer, [])
    return ",".join(agents)


def allowed_agents_for_record_type(record_type: str) -> str:
    agents = KNOWLEDGE_RECORD_AGENTS.get(record_type, [])
    return ",".join(agents)


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


def json_dumps(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True)


def json_loads(value: str | None, default: Any) -> Any:
    if not value:
        return default
    return json.loads(value)


def row_to_dict(row: sqlite3.Row) -> dict[str, Any]:
    return {key: row[key] for key in row.keys()}
