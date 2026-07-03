from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from biomaster.mvp import MVP_SKILL_IDS  # noqa: E402


from biomaster.knowledge.sync_skills import sync_skills  # noqa: E402


def test_sync_skills(tmp_path):
    db = tmp_path / "skills.db"
    stats = sync_skills(db_path=db)
    assert stats["synced"] >= len(MVP_SKILL_IDS)
    assert stats["enabled"] >= len(MVP_SKILL_IDS)
