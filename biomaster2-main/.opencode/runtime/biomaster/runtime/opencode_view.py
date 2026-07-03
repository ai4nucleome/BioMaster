from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from biomaster.runtime.run_context import RunContext


PREVIEW_SUFFIXES = {".csv", ".tsv", ".txt", ".log", ".md", ".yaml", ".yml", ".json", ".sh"}
IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp", ".gif"}


def _relative(run: RunContext, path: Path) -> str:
    try:
        return path.relative_to(run.root).as_posix()
    except ValueError:
        return path.as_posix()


def _read_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return data if isinstance(data, dict) else {}


def _candidate_paths(run: RunContext, step_id: str, output_name: str) -> list[Path]:
    value = output_name.strip()
    return [
        run.root / value,
        run.step_dir(step_id) / value,
    ]


def _first_existing(paths: list[Path]) -> Path | None:
    for path in paths:
        if path.exists():
            return path
    return None


def _preview_text(path: Path, *, max_lines: int = 8) -> str:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except UnicodeDecodeError:
        return "_binary file_"
    return "\n".join(lines[:max_lines])


def _artifact_section(run: RunContext, step_id: str, output_name: str) -> list[str]:
    found = _first_existing(_candidate_paths(run, step_id, output_name))
    if found is None:
        return [f"- `{output_name}`: missing"]

    rel = _relative(run, found)
    suffix = found.suffix.lower()
    if found.is_dir():
        return [f"- `{output_name}`: [`{rel}/`]({rel}/)"]
    if suffix in IMAGE_SUFFIXES:
        return [f"- `{output_name}`: [`{rel}`]({rel})", f"  ![]({rel})"]
    if suffix in PREVIEW_SUFFIXES:
        preview = _preview_text(found)
        return [f"- `{output_name}`: [`{rel}`]({rel})", "", "```text", preview, "```"]
    return [f"- `{output_name}`: [`{rel}`]({rel})"]


def write_opencode_view(run: RunContext, plan: dict | None = None) -> Path:
    """Write a Markdown index optimized for browsing run artifacts in OpenCode."""

    if plan is None and run.plan_path.exists():
        plan = _read_yaml(run.plan_path)
    plan = plan or {}

    lines = [
        f"# BioMaster Run {run.run_id}",
        "",
        "This file is a browsable OpenCode view of scripts, checks, and selected outputs.",
        "",
        "## Run Files",
        "",
        f"- PLAN: [`PLAN.yaml`](PLAN.yaml)",
        f"- CHECK report: [`CHECK_REPORT.yaml`](CHECK_REPORT.yaml)",
    ]
    if (run.root / "REPORT.md").exists():
        lines.append("- Final report: [`REPORT.md`](REPORT.md)")
    lines.append("")

    for step in plan.get("steps", []):
        step_id = str(step.get("step_id"))
        lines.extend([f"## {step_id}", ""])
        script = run.root / "scripts" / step_id / "run.sh"
        if script.exists():
            rel_script = _relative(run, script)
            lines.extend([f"- Script: [`{rel_script}`]({rel_script})", "", "```bash", _preview_text(script, max_lines=12), "```"])
        else:
            lines.append("- Script: missing")

        step_result = run.step_dir(step_id) / "step_result.yaml"
        if step_result.exists():
            rel_result = _relative(run, step_result)
            lines.append(f"- Step result: [`{rel_result}`]({rel_result})")
            step_result_data = _read_yaml(step_result)
            artifacts = step_result_data.get("artifacts") or []
            if artifacts:
                lines.extend(["", "### Recorded Artifacts", ""])
                for artifact in artifacts:
                    artifact_path = Path(str(artifact))
                    if artifact_path.exists():
                        rel_artifact = _relative(run, artifact_path)
                        lines.append(f"- [`{rel_artifact}`]({rel_artifact})")
                    else:
                        lines.append(f"- `{artifact}`: missing")

        expected_outputs = step.get("expected_outputs") or []
        if expected_outputs:
            lines.extend(["", "### Outputs", ""])
            for output_name in expected_outputs:
                lines.extend(_artifact_section(run, step_id, str(output_name)))
                lines.append("")

    path = run.root / "OPENCODE_VIEW.md"
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    return path
