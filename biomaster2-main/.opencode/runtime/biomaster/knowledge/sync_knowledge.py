from __future__ import annotations

from pathlib import Path
import argparse
import hashlib
from datetime import datetime, timezone

from biomaster.knowledge import (
    DEFAULT_DB_PATH,
    TARGET_TASK_RECORDS,
    TARGET_WORKFLOW_RECORDS,
    allowed_agents_for_record_type,
    connect,
    ensure_schema,
    json_dumps,
)
from biomaster.skills.manager import KnowledgeRegistry


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def content_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def build_workflow_row(record, project_root: Path) -> dict[str, object]:
    text = record.path.read_text(encoding="utf-8") if record.path.exists() else ""
    return {
        "record_id": record.record_id,
        "record_type": "workflow",
        "path": record.relative_path,
        "title": record.title,
        "summary": record.summary,
        "keywords": json_dumps(record.keywords),
        "analysis_type": record.metadata.get("analysis_type"),
        "tool": None,
        "domain": "bioinformatics",
        "discipline": record.metadata.get("analysis_type"),
        "canonical_skill_id": record.metadata.get("canonical_plan_skill", "plan-workflow"),
        "allowed_agents": allowed_agents_for_record_type("workflow"),
        "origin_source": record.metadata.get("origin_source"),
        "origin_page": str(record.metadata.get("origin_page", "")),
        "source_entry_index": int(record.metadata.get("source_entry_index", 0) or 0),
        "source_subindex": int(record.metadata.get("source_subindex", 0) or 0),
        "source_file": record.metadata.get("source_file"),
        "enabled": 1 if record.metadata.get("status", "active") == "active" else 0,
        "content_hash": content_hash(text),
        "content": text,
        "extra_json": json_dumps(
            {
                key: value
                for key, value in record.metadata.items()
                if key
                not in {
                    "analysis_type",
                    "canonical_plan_skill",
                    "origin_source",
                    "origin_page",
                    "source_entry_index",
                    "source_subindex",
                    "source_file",
                    "status",
                }
            }
        ),
        "updated_at": utc_now(),
    }


def build_task_row(record, project_root: Path) -> dict[str, object]:
    text = record.path.read_text(encoding="utf-8") if record.path.exists() else ""
    tool = record.metadata.get("tool")
    return {
        "record_id": record.record_id,
        "record_type": "task",
        "path": record.relative_path,
        "title": record.title,
        "summary": record.summary,
        "keywords": json_dumps(record.keywords),
        "analysis_type": None,
        "tool": tool,
        "domain": "bioinformatics",
        "discipline": tool,
        "canonical_skill_id": record.metadata.get("canonical_exec_skill", "exec-task"),
        "allowed_agents": allowed_agents_for_record_type("task"),
        "origin_source": record.metadata.get("origin_source"),
        "origin_page": str(record.metadata.get("origin_page", "")),
        "source_entry_index": int(record.metadata.get("source_entry_index", 0) or 0),
        "source_subindex": int(record.metadata.get("source_subindex", 0) or 0),
        "source_file": record.metadata.get("source_file"),
        "enabled": 1 if record.metadata.get("status", "active") == "active" else 0,
        "content_hash": content_hash(text),
        "content": text,
        "extra_json": json_dumps(
            {
                key: value
                for key, value in record.metadata.items()
                if key
                not in {
                    "tool",
                    "canonical_exec_skill",
                    "origin_source",
                    "origin_page",
                    "source_entry_index",
                    "source_subindex",
                    "source_file",
                    "status",
                }
            }
        ),
        "updated_at": utc_now(),
    }


def upsert_knowledge_record(connection, row: dict[str, object]) -> None:
    connection.execute(
        """
        INSERT INTO knowledge_records (
          record_id, record_type, path, title, summary, keywords,
          analysis_type, tool, domain, discipline, canonical_skill_id, allowed_agents,
          origin_source, origin_page, source_entry_index, source_subindex, source_file,
          enabled, content_hash, content, extra_json, updated_at
        ) VALUES (
          :record_id, :record_type, :path, :title, :summary, :keywords,
          :analysis_type, :tool, :domain, :discipline, :canonical_skill_id, :allowed_agents,
          :origin_source, :origin_page, :source_entry_index, :source_subindex, :source_file,
          :enabled, :content_hash, :content, :extra_json, :updated_at
        )
        ON CONFLICT(record_id) DO UPDATE SET
          record_type = excluded.record_type,
          path = excluded.path,
          title = excluded.title,
          summary = excluded.summary,
          keywords = excluded.keywords,
          analysis_type = excluded.analysis_type,
          tool = excluded.tool,
          domain = excluded.domain,
          discipline = excluded.discipline,
          canonical_skill_id = excluded.canonical_skill_id,
          allowed_agents = excluded.allowed_agents,
          origin_source = excluded.origin_source,
          origin_page = excluded.origin_page,
          source_entry_index = excluded.source_entry_index,
          source_subindex = excluded.source_subindex,
          source_file = excluded.source_file,
          enabled = excluded.enabled,
          content_hash = excluded.content_hash,
          content = excluded.content,
          extra_json = excluded.extra_json,
          updated_at = excluded.updated_at
        """,
        row,
    )


def prune_missing_records(connection, record_type: str, active_ids: set[str]) -> int:
    rows = connection.execute(
        "SELECT record_id FROM knowledge_records WHERE record_type = ?",
        (record_type,),
    ).fetchall()
    removed = 0
    for row in rows:
        record_id = row[0]
        if record_id not in active_ids:
            connection.execute(
                "DELETE FROM knowledge_records WHERE record_id = ?",
                (record_id,),
            )
            removed += 1
    return removed


def sync_knowledge(db_path: Path = DEFAULT_DB_PATH) -> dict[str, int]:
    """Load numbered workflow/task records into knowledge_records.

    These records are used for retrieval and prompt context. They deliberately
    do not create pipeline_routes or bypass route/skill gates.
    """
    project_root = db_path.parents[2]
    workflows = KnowledgeRegistry.workflows()
    tasks = KnowledgeRegistry.tasks()
    connection = connect(db_path)
    try:
        ensure_schema(connection)
        workflow_ids: set[str] = set()
        task_ids: set[str] = set()

        for record in workflows.list():
            upsert_knowledge_record(connection, build_workflow_row(record, project_root))
            workflow_ids.add(record.record_id)

        for record in tasks.list():
            upsert_knowledge_record(connection, build_task_row(record, project_root))
            task_ids.add(record.record_id)

        removed_workflows = prune_missing_records(connection, "workflow", workflow_ids)
        removed_tasks = prune_missing_records(connection, "task", task_ids)
        connection.commit()

        workflow_total = connection.execute(
            "SELECT COUNT(*) FROM knowledge_records WHERE record_type = 'workflow'"
        ).fetchone()[0]
        task_total = connection.execute(
            "SELECT COUNT(*) FROM knowledge_records WHERE record_type = 'task'"
        ).fetchone()[0]
        return {
            "workflows_synced": len(workflow_ids),
            "tasks_synced": len(task_ids),
            "workflow_total": workflow_total,
            "task_total": task_total,
            "removed_workflows": removed_workflows,
            "removed_tasks": removed_tasks,
        }
    finally:
        connection.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Sync numbered workflow/task knowledge records into SQLite.")
    parser.add_argument("--db", type=Path, default=DEFAULT_DB_PATH)
    args = parser.parse_args()

    stats = sync_knowledge(args.db)
    print(f"Synced workflows: {stats['workflows_synced']} (total: {stats['workflow_total']})")
    print(f"Synced tasks: {stats['tasks_synced']} (total: {stats['task_total']})")
    if stats["removed_workflows"] or stats["removed_tasks"]:
        print(
            "Removed stale records: "
            f"workflows={stats['removed_workflows']}, tasks={stats['removed_tasks']}"
        )
    if stats["workflow_total"] != TARGET_WORKFLOW_RECORDS:
        raise SystemExit(
            f"expected {TARGET_WORKFLOW_RECORDS} workflow records, found {stats['workflow_total']}"
        )
    if stats["task_total"] != TARGET_TASK_RECORDS:
        raise SystemExit(f"expected {TARGET_TASK_RECORDS} task records, found {stats['task_total']}")


if __name__ == "__main__":
    main()
