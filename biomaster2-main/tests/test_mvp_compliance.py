from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from biomaster.compliance.plan_audit import audit_plan_compliance  # noqa: E402


def test_mvp_plan_compliance():
    errors = audit_plan_compliance()
    assert not errors, "Plan compliance errors:\n" + "\n".join(errors)
