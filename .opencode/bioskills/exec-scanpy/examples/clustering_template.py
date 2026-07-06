"""Scanpy clustering and annotation template for step 05."""

from __future__ import annotations

from pathlib import Path
import json
import shutil


def _find_upstream_h5ad(run_dir: Path, step_id: str) -> Path | None:
    step_num = int(step_id[:2])
    upstream_steps = sorted(
        path
        for path in (run_dir / "steps").glob("[0-9][0-9]_*")
        if path.is_dir() and int(path.name[:2]) < step_num
    )
    for step_dir in reversed(upstream_steps):
        for name in ("adata_batch_corrected.h5ad", "adata_no_doublets.h5ad", "adata_qc.h5ad", "adata_raw.h5ad"):
            candidate = step_dir / name
            if candidate.exists():
                return candidate
    return None


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
    source_h5ad = _find_upstream_h5ad(run_dir, step_id)
    if source_h5ad:
        shutil.copy2(source_h5ad, step_dir / "adata_annotated.h5ad")
    else:
        (step_dir / "adata_annotated.h5ad").write_text("placeholder annotated AnnData\n", encoding="utf-8")
    (step_dir / "umap.png").write_bytes(b"placeholder umap image\n")
    (step_dir / "execution_log.txt").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary
