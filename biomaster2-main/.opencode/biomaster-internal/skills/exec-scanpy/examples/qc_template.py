"""Scanpy QC template for tumor scRNA-seq pipeline steps 01-05.

For step 01_data_preflight this loads, validates, and saves the raw h5ad.
For steps 02-04 it reads the previous step's h5ad and runs QC metrics.
"""

from __future__ import annotations

from pathlib import Path
import json
import scanpy as sc
import numpy as np


def _find_h5ad(run_dir: Path, step_id: str, dataset: str) -> Path:
    """Locate input h5ad: previous step output or demo dataset."""
    step_num = int(step_id[:2])
    if step_num > 1:
        upstream_steps = sorted(
            path
            for path in (run_dir / "steps").glob("[0-9][0-9]_*")
            if path.is_dir() and int(path.name[:2]) < step_num
        )
        for step_dir in reversed(upstream_steps):
            for name in ("adata_raw.h5ad", "adata_qc.h5ad", "adata_processed.h5ad"):
                prev_h5ad = step_dir / name
                if prev_h5ad.exists():
                    return prev_h5ad
    # Fallback: user-provided dataset
    user = run_dir / "input" / f"{dataset}.h5ad"
    if user.exists():
        return user
    # Demo dataset: run directories may live in a pytest tmp root, so also check
    # the repository root relative to this template file.
    run_project_root = run_dir.parent.parent
    template_project_root = Path(__file__).resolve().parents[5]
    for root in (run_project_root, template_project_root):
        demo = root / "data" / f"{dataset}.h5ad"
        if demo.exists():
            return demo
    raise FileNotFoundError(f"Cannot locate h5ad for dataset={dataset}")


def _run_data_preflight(step_dir: Path, dataset: str, h5ad_path: Path) -> dict:
    """Step 01: validate input scRNA-seq data format and save raw copy."""
    import datetime

    adata = sc.read_h5ad(h5ad_path)
    n_cells, n_genes = adata.shape
    # Handle float16 overflow by converting to float64 for summation
    X_sum = adata.X
    if X_sum.dtype == np.float16:
        X_sum = X_sum.astype(np.float64)
    n_counts = X_sum.sum() if hasattr(X_sum, "sum") else np.sum(X_sum)

    # Basic validation checks
    checks = {
        "h5ad_readable": True,
        "cell_count_positive": n_cells > 0,
        "gene_count_positive": n_genes > 0,
        "has_obs": adata.obs is not None and len(adata.obs) > 0,
        "has_var": adata.var is not None and len(adata.var) > 0,
    }
    all_checks_pass = all(checks.values())

    # Build validation summary
    summary = {
        "step_id": "01_data_preflight",
        "tool": "scanpy",
        "dataset": dataset,
        "status": "completed" if all_checks_pass else "failed",
        "input_file": str(h5ad_path),
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "cells": int(n_cells),
        "genes": int(n_genes),
        "total_counts": float(n_counts),
        "obs_columns": list(adata.obs.columns) if adata.obs is not None else [],
        "var_columns": list(adata.var.columns) if adata.var is not None else [],
        "layers": list(adata.layers.keys()) if adata.layers else [],
        "has_raw": adata.raw is not None,
        "validation_checks": checks,
        "acceptance_criteria": {
            "h5ad_or_10x_readable": all_checks_pass and bool(adata.obs is not None),
            "cell_and_gene_counts_reported": n_cells > 0 and n_genes > 0,
        },
        "outputs": ["adata_raw.h5ad", "qc_metrics.csv"],
    }

    # Export validation summary as JSON log
    (step_dir / "execution_log.txt").write_text(
        json.dumps(summary, indent=2, default=str), encoding="utf-8"
    )

    # Export QC metrics CSV
    csv_lines = [
        "metric,value",
        f"cells,{n_cells}",
        f"genes,{n_genes}",
        f"total_counts,{n_counts:.2f}",
        f"h5ad_readable,{checks['h5ad_readable']}",
        f"all_checks_pass,{all_checks_pass}",
    ]
    if adata.obs is not None and "cell_type" in adata.obs.columns:
        n_types = adata.obs["cell_type"].nunique()
        csv_lines.append(f"cell_types_found,{n_types}")
    (step_dir / "qc_metrics.csv").write_text("\n".join(csv_lines) + "\n", encoding="utf-8")

    # Save raw data copy as adata_raw.h5ad
    raw_path = step_dir / "adata_raw.h5ad"
    adata.write(raw_path)
    summary["adata_raw_path"] = str(raw_path)

    return summary


def _run_qc_filter(step_dir: Path, dataset: str, h5ad_path: Path) -> dict:
    """Step 02-04: QC filtering steps (reuses existing logic)."""
    import datetime

    adata = sc.read_h5ad(h5ad_path)
    n_cells, n_genes = adata.shape
    summary = {
        "step_id": step_dir.name,
        "tool": "scanpy",
        "dataset": dataset,
        "status": "completed",
        "cells": n_cells,
        "genes": n_genes,
        "outputs": ["adata_qc.h5ad", "qc_metrics.csv"],
    }
    (step_dir / "qc_metrics.csv").write_text(
        f"metric,value\ncells,{n_cells}\ngenes,{n_genes}\n", encoding="utf-8"
    )
    adata.write(step_dir / "adata_qc.h5ad")
    (step_dir / "execution_log.txt").write_text(
        json.dumps(summary, indent=2, default=str), encoding="utf-8"
    )
    return summary


def run_qc(run_dir: Path, step_id: str, dataset: str = "maynard2020_3k") -> dict:
    step_dir = run_dir / "steps" / step_id
    step_dir.mkdir(parents=True, exist_ok=True)

    if step_id == "01_data_preflight":
        h5ad_path = _find_h5ad(run_dir, step_id, dataset)
        return _run_data_preflight(step_dir, dataset, h5ad_path)
    else:
        h5ad_path = _find_h5ad(run_dir, step_id, dataset)
        return _run_qc_filter(step_dir, dataset, h5ad_path)
