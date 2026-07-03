"""cNMF template for test-mode co-expression module artifacts."""

from __future__ import annotations

from pathlib import Path
import json


def run_step(run_dir: str | Path, step_id: str) -> dict:
    root = Path(run_dir)
    step_dir = root / "steps" / step_id
    cnmf_dir = step_dir / "cnmf"
    cnmf_dir.mkdir(parents=True, exist_ok=True)

    (cnmf_dir / "modules.csv").write_text(
        "module,top_genes\nM1,\"MKI67,TOP2A\"\nM2,\"COL1A1,DCN\"\n",
        encoding="utf-8",
    )
    (cnmf_dir / "gene_loadings.csv").write_text(
        "gene,module,loading\nMKI67,M1,0.91\nDCN,M2,0.87\n",
        encoding="utf-8",
    )
    summary = {
        "tool": "cnmf",
        "step_id": step_id,
        "status": "completed",
        "outputs": ["cnmf/modules.csv", "cnmf/gene_loadings.csv"],
    }
    (step_dir / "execution_log.txt").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary
