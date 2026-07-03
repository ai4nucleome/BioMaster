from __future__ import annotations

from pathlib import Path
import argparse

from biomaster.knowledge import (
    DEFAULT_DB_PATH,
    DEFAULT_SCHEMA_PATH,
    REQUIRED_TABLES,
    connect,
    ensure_schema,
    table_exists,
)


def init_database(db_path: Path = DEFAULT_DB_PATH, schema_path: Path = DEFAULT_SCHEMA_PATH) -> list[str]:
    connection = connect(db_path)
    try:
        ensure_schema(connection, schema_path)
        return [table for table in REQUIRED_TABLES if table_exists(connection, table)]
    finally:
        connection.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Initialize the BioMaster SQLite skill control database.")
    parser.add_argument(
        "--db",
        type=Path,
        default=DEFAULT_DB_PATH,
        help=f"SQLite database path (default: {DEFAULT_DB_PATH})",
    )
    parser.add_argument(
        "--schema",
        type=Path,
        default=DEFAULT_SCHEMA_PATH,
        help="Path to schema.sql",
    )
    args = parser.parse_args()

    tables = init_database(args.db, args.schema)
    print(f"Initialized database: {args.db}")
    for table in tables:
        print(f"- table ready: {table}")


if __name__ == "__main__":
    main()
