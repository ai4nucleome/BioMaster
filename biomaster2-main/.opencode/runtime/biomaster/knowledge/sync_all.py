from __future__ import annotations

from pathlib import Path
import argparse

from biomaster.knowledge import DEFAULT_DB_PATH, connect, ensure_schema
from biomaster.knowledge.sync_skills import sync_skills


def sync_all(db_path: Path = DEFAULT_DB_PATH, *, include_numbered_knowledge: bool = False) -> dict[str, int]:
    """Sync SQLite control data from the file-backed BioSkills library."""

    stats = sync_skills(db_path=db_path)
    connection = connect(db_path)
    try:
        ensure_schema(connection)
        connection.execute("DELETE FROM knowledge_records")
        connection.commit()
    finally:
        connection.close()
    return {**stats, "knowledge_records": 0}


def main() -> None:
    parser = argparse.ArgumentParser(description="Sync active BioSkills into SQLite.")
    parser.add_argument("--db", type=Path, default=DEFAULT_DB_PATH)
    parser.add_argument(
        "--skills-only",
        action="store_true",
        help="Compatibility flag; BioSkills are now the only sync source.",
    )
    args = parser.parse_args()

    stats = sync_all(args.db, include_numbered_knowledge=False)
    print(f"BioSkills synced: {stats['synced']} (enabled: {stats['enabled']})")


if __name__ == "__main__":
    main()
