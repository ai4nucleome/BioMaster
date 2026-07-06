from __future__ import annotations

from pathlib import Path
from typing import Any

from biomaster.knowledge import DEFAULT_DB_PATH, connect, ensure_schema, json_loads, row_to_dict
from biomaster.knowledge.query_skills import (
    get_knowledge_record,
    get_skill_by_id,
    list_knowledge_records,
    list_skills,
    search_knowledge_records,
    search_routes,
)


class KnowledgeStore:
    """SQLite-first runtime knowledge interface."""

    def __init__(self, db_path: Path = DEFAULT_DB_PATH) -> None:
        self.db_path = db_path
        self._connection = connect(db_path)
        ensure_schema(self._connection)

    def close(self) -> None:
        self._connection.close()

    def __enter__(self) -> "KnowledgeStore":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    def summary(self) -> dict[str, int]:
        skills = self._connection.execute("SELECT COUNT(*) FROM skills WHERE enabled = 1").fetchone()[0]
        workflows = self._connection.execute(
            "SELECT COUNT(*) FROM knowledge_records WHERE record_type = 'workflow' AND enabled = 1"
        ).fetchone()[0]
        tasks = self._connection.execute(
            "SELECT COUNT(*) FROM knowledge_records WHERE record_type = 'task' AND enabled = 1"
        ).fetchone()[0]
        routes = self._connection.execute("SELECT COUNT(*) FROM pipeline_routes WHERE enabled = 1").fetchone()[0]
        return {
            "skills": skills,
            "workflow_records": workflows,
            "task_records": tasks,
            "pipeline_routes": routes,
        }

    def get_skill(self, skill_id: str) -> dict[str, Any] | None:
        return get_skill_by_id(self._connection, skill_id)

    def read_skill_body(self, skill_id: str) -> str:
        skill = self.get_skill(skill_id)
        if skill is None:
            raise KeyError(f"unknown skill: {skill_id}")
        body = skill.get("body")
        if isinstance(body, str) and body.strip():
            return body
        raise ValueError(f"skill body missing in SQLite for: {skill_id}")

    def list_skills(self, *, layer: str | None = None) -> list[dict[str, Any]]:
        return list_skills(self._connection, layer=layer)

    def get_record(self, record_id: str) -> dict[str, Any] | None:
        return get_knowledge_record(self._connection, record_id)

    def read_record_content(self, record_id: str) -> str:
        record = self.get_record(record_id)
        if record is None:
            raise KeyError(f"unknown knowledge record: {record_id}")
        content = record.get("content")
        if isinstance(content, str) and content.strip():
            return content
        raise ValueError(f"knowledge content missing in SQLite for: {record_id}")

    def list_records(self, *, record_type: str | None = None) -> list[dict[str, Any]]:
        return list_knowledge_records(self._connection, record_type=record_type)

    def search_records(
        self,
        query: str,
        *,
        record_type: str | None = None,
        agent_name: str | None = None,
        limit: int = 10,
    ) -> list[dict[str, Any]]:
        return [
            record
            for _, record in search_knowledge_records(
                self._connection,
                query,
                record_type=record_type,
                agent_name=agent_name,
                limit=limit,
            )
        ]

    def search_routes(self, query: str, *, limit: int = 5) -> list[dict[str, Any]]:
        return [route for _, route in search_routes(self._connection, query, limit=limit)]

    def record_summary_row(self, record: dict[str, Any]) -> str:
        if record.get("record_type") == "workflow":
            skill = record.get("canonical_skill_id") or "-"
            return f"{record['record_id']}\t{skill}\t{record['title']}"
        tool = record.get("tool") or record.get("canonical_skill_id") or "-"
        return f"{record['record_id']}\t{tool}\t{record['title']}"

    def keywords(self, record: dict[str, Any]) -> list[str]:
        return json_loads(record.get("keywords"), [])
