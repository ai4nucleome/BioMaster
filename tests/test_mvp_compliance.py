from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from biomaster.compliance.plan_audit import audit_plan_compliance  # noqa: E402
from biomaster.knowledge import DEFAULT_DB_PATH  # noqa: E402
from biomaster.knowledge.seed_routes import seed_routes  # noqa: E402
from biomaster.knowledge.sync_all import sync_all  # noqa: E402


def test_mvp_plan_compliance():
    sync_all(db_path=DEFAULT_DB_PATH)
    seed_routes(DEFAULT_DB_PATH)
    errors = audit_plan_compliance()
    assert not errors, "Plan compliance errors:\n" + "\n".join(errors)
