from pathlib import Path
import sqlite3
import sys

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from biomaster.runtime import statusline  # noqa: E402


def test_statusline_reports_plan_task_progress(tmp_path, monkeypatch):
    db_path = tmp_path / "knowledge.db"
    projects_root = tmp_path / "projects"
    run_dir = projects_root / "tumor-demo"
    run_dir.mkdir(parents=True)

    connection = sqlite3.connect(db_path)
    connection.execute(
        "CREATE TABLE run_states (id INTEGER PRIMARY KEY, run_id TEXT, phase TEXT, updated_at TEXT)"
    )
    connection.execute(
        "INSERT INTO run_states (run_id, phase, updated_at) VALUES ('tumor-demo', 'execution', '2026-01-01T00:00:00Z')"
    )
    connection.commit()
    connection.close()

    (run_dir / "PLAN.yaml").write_text(
        yaml.safe_dump({"steps": [{"step_id": "01_a"}, {"step_id": "02_b"}]}),
        encoding="utf-8",
    )
    (run_dir / "CHECK_REPORT.yaml").write_text(
        yaml.safe_dump({"checks": [{"step_id": "01_a", "status": "pass"}]}),
        encoding="utf-8",
    )

    monkeypatch.setattr(statusline, "DB_PATH", db_path)
    monkeypatch.setattr(statusline, "PROJECTS_ROOT", projects_root)
    monkeypatch.setattr(statusline, "PROJECT_ROOT", tmp_path)

    text = statusline.build_status({"cwd": str(tmp_path)})
    assert "BioMaster project tumor-demo" in text
    assert "phase: execution" in text
    assert "1/2 steps complete" in text
    assert "current: 02_b" in text
