from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from biomaster.knowledge import REQUIRED_TABLES, connect, table_exists  # noqa: E402
from biomaster.knowledge.init_db import init_database  # noqa: E402


def test_sqlite_init(tmp_path):
    db = tmp_path / "test.db"
    tables = init_database(db)
    assert set(REQUIRED_TABLES).issubset(set(tables))
    connection = connect(db)
    try:
        for table in REQUIRED_TABLES:
            assert table_exists(connection, table)
    finally:
        connection.close()
