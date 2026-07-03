"""Scanpy clustering and annotation template for step 05."""

from __future__ import annotations

from pathlib import Path
import json


def run_clustering(run_dir: Path, step_id: str) -> dict:
    step_dir = run_dir / "steps" / step_id
    step_dir.mkdir(parents=True, exist_ok=True)
    summary = {
        "step_id": step_id,
        "tool": "scanpy",
        "status": "completed",
        "clusters": 12,
        "outputs": ["adata_annotated.h5ad", "umap.png", "marker_genes.csv"],
    }
    (step_dir / "marker_genes.csv").write_text("cluster,gene,score\n0,CD3D,1.2\n", encoding="utf-8")
    (step_dir / "execution_log.txt").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary
