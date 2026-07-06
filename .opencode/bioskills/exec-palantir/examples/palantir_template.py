"""Palantir template for test-mode trajectory artifacts."""

from __future__ import annotations

from pathlib import Path
import json


def run_step(run_dir: str | Path, step_id: str) -> dict:
    root = Path(run_dir)
    step_dir = root / "steps" / step_id
    palantir_dir = step_dir / "palantir"
    palantir_dir.mkdir(parents=True, exist_ok=True)

    (palantir_dir / "pseudotime.csv").write_text(
        "cell_id,pseudotime\ncell_001,0.12\ncell_002,0.88\n",
        encoding="utf-8",
    )
    (palantir_dir / "branch_probs.csv").write_text(
        "cell_id,branch_a,branch_b\ncell_001,0.7,0.3\ncell_002,0.2,0.8\n",
        encoding="utf-8",
    )
    summary = {
        "tool": "palantir",
        "step_id": step_id,
        "status": "completed",
        "outputs": ["palantir/pseudotime.csv", "palantir/branch_probs.csv"],
    }
    (step_dir / "execution_log.txt").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary
