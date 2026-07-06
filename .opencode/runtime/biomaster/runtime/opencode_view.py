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


def _table_cell(value: object) -> str:
    return str(value or "").replace("|", "\\|").replace("\n", " ")


def _link(label: str, target: str) -> str:
    return f"[`{label}`]({target})"


def _step_display_status(log_entry: dict[str, Any] | None, *, has_script: bool) -> str:
    if not log_entry:
        return "WAITING" if not has_script else "EXECUTED"
    check = log_entry.get("check") or {}
    execution = log_entry.get("execution") or {}
    if check.get("status") == "pass":
        return "DONE"
    if check.get("status") == "fail":
        return "BLOCKED"
    if execution.get("status") in {"success", "completed"}:
        return "EXECUTED"
    if execution.get("status") in {"failed", "fail"}:
        return "EXECUTION_FAILED"
    return "WAITING"


def _project_summary(plan: dict[str, Any], log_steps: dict[str, dict[str, Any]], run: RunContext) -> dict[str, Any]:
    steps = plan.get("steps") or []
    total = len(steps)
    done = 0
    blocked_step = ""
    current_step = ""
    for step in steps:
        step_id = str(step.get("step_id"))
        script = run.root / "scripts" / step_id / "run.sh"
        status = _step_display_status(log_steps.get(step_id), has_script=script.exists())
        if status == "DONE":
            done += 1
            continue
        if not current_step:
            current_step = step_id
        if status in {"BLOCKED", "EXECUTION_FAILED"} and not blocked_step:
            blocked_step = step_id
    return {
        "total": total,
        "done": done,
        "remaining": max(total - done, 0),
        "current_step": current_step,
        "blocked_step": blocked_step,
        "overall": "DONE" if total and done == total else ("BLOCKED" if blocked_step else "RUNNING"),
    }


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
        f"# BioMaster Project {run.run_id}",
        "",
        "This file is a browsable OpenCode view of scripts, project logs, checks, and selected outputs.",
        "",
        "## Project Files",
        "",
        f"- PLAN: [`PLAN.yaml`](PLAN.yaml)",
        f"- CHECK report: [`CHECK_REPORT.yaml`](CHECK_REPORT.yaml)",
    ]
    if run.project_log_path.exists():
        lines.append("- Project log: [`PROJECT_LOG.yaml`](PROJECT_LOG.yaml)")
    if run.report_path.exists():
        lines.append("- Final report: [`REPORT.md`](REPORT.md)")
    lines.append("")

    project_log = _read_yaml(run.project_log_path)
    log_steps = {
        str(item.get("step_id")): item
        for item in project_log.get("steps", [])
        if isinstance(item, dict)
    }
    summary = _project_summary(plan, log_steps, run)

    lines.extend(
        [
            "## Project Dashboard",
            "",
            f"- Status: `{summary['overall']}`",
            f"- Progress: `{summary['done']}/{summary['total']}` steps complete, `{summary['remaining']}` remaining",
            f"- Current step: `{summary['current_step'] or 'none'}`",
            f"- Blocked step: `{summary['blocked_step'] or 'none'}`",
            "",
            "## Key Files",
            "",
            "| File | Link |",
            "|---|---|",
            "| PLAN | [`PLAN.yaml`](PLAN.yaml) |",
            "| Check report | [`CHECK_REPORT.yaml`](CHECK_REPORT.yaml) |",
            "| Project log | [`PROJECT_LOG.yaml`](PROJECT_LOG.yaml) |",
            "| Final report | [`REPORT.md`](REPORT.md) |",
            "",
            "## Stage Summary",
            "",
            "| Stage | Status | Execution | Check | Evidence |",
            "|---|---|---|---|---|",
        ]
    )

    for step in plan.get("steps", []):
        step_id = str(step.get("step_id"))
        log_entry = log_steps.get(step_id)
        script = run.root / "scripts" / step_id / "run.sh"
        status = _step_display_status(log_entry, has_script=script.exists())
        execution = (log_entry or {}).get("execution") or {}
        check = (log_entry or {}).get("check") or {}
        evidence = ""
        if script.exists():
            rel_script = _relative(run, script)
            evidence = _link("script", rel_script)
        elif check.get("conclusion"):
            evidence = str(check.get("conclusion"))
        lines.append(
            "| "
            + " | ".join(
                [
                    _table_cell(step_id),
                    _table_cell(status),
                    _table_cell(execution.get("status", "")),
                    _table_cell(check.get("status", "")),
                    _table_cell(evidence),
                ]
            )
            + " |"
        )
    lines.append("")

    for step in plan.get("steps", []):
        step_id = str(step.get("step_id"))
        lines.extend([f"## {step_id}", ""])
        log_entry = log_steps.get(step_id)
        if log_entry:
            check = log_entry.get("check") or {}
            lines.extend(
                [
                    f"- Check status: `{check.get('status', '')}`",
                    f"- Check conclusion: {check.get('conclusion', '')}",
                ]
            )
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
