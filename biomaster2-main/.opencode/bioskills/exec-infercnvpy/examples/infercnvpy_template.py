"""inferCNVpy template for test-mode malignant cell scoring."""

from __future__ import annotations

from pathlib import Path
import json


def run_step(run_dir: str | Path, step_id: str) -> dict:
    root = Path(run_dir)
    step_dir = root / "steps" / step_id
    step_dir.mkdir(parents=True, exist_ok=True)
    infercnv_dir = step_dir / "infercnv"
    infercnv_dir.mkdir(parents=True, exist_ok=True)

    (infercnv_dir / "cnv_heatmap.txt").write_text("placeholder inferCNV heatmap artifact\n", encoding="utf-8")
    (step_dir / "malignancy_scores.csv").write_text(
        "cell_id,malignancy_score\ncell_001,0.82\ncell_002,0.15\n",
        encoding="utf-8",
    )
    summary = {
        "tool": "infercnvpy",
        "step_id": step_id,
        "status": "completed",
        "outputs": ["infercnv/", "malignancy_scores.csv"],
    }
    (step_dir / "execution_log.txt").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary
