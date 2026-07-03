from __future__ import annotations

from pathlib import Path
import argparse

from biomaster.knowledge import DEFAULT_DB_PATH
from biomaster.knowledge.sync_knowledge import sync_knowledge
from biomaster.knowledge.sync_skills import sync_skills


def sync_all(db_path: Path = DEFAULT_DB_PATH, *, include_numbered_knowledge: bool = True) -> dict[str, int]:
    """Sync SQLite control data.

    Numbered workflow/task knowledge is searchable context only; strict workflow
    selection still comes from pipeline_routes and phase-filtered skills.
    """
    skill_stats = sync_skills(db_path=db_path)
    if not include_numbered_knowledge:
        return skill_stats
    knowledge_stats = sync_knowledge(db_path=db_path)
    return {**skill_stats, **knowledge_stats}


def main() -> None:
    parser = argparse.ArgumentParser(description="Sync active skills and numbered knowledge records into SQLite.")
    parser.add_argument("--db", type=Path, default=DEFAULT_DB_PATH)
    parser.add_argument("--skills-only", action="store_true", help="Sync only skill records, skipping numbered workflow/task knowledge.")
    args = parser.parse_args()

    stats = sync_all(args.db, include_numbered_knowledge=not args.skills_only)
    print(f"Skills synced: {stats['synced']} (enabled: {stats['enabled']})")
    if not args.skills_only:
        print(f"Workflow records synced: {stats['workflows_synced']} (total: {stats['workflow_total']})")
        print(f"Task records synced: {stats['tasks_synced']} (total: {stats['task_total']})")


if __name__ == "__main__":
    main()
