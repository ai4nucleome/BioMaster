from __future__ import annotations

from biomaster.runtime.run_context import RunContext
from biomaster.runtime.yaml_io import load_yaml_mapping, validate_project_log


def _table_cell(value: object) -> str:
    return str(value or "").replace("|", "\\|").replace("\n", " ")


def write_final_report(run: RunContext, sections: dict[str, str]) -> str:
    lines = ["# BioMaster Analysis Report", ""]
    for title, body in sections.items():
        lines.append(f"## {title}")
        lines.append(body.strip())
        lines.append("")
    content = "\n".join(lines).strip() + "\n"
    path = run.report_path
    path.write_text(content, encoding="utf-8")
    return content


def write_report_from_project_log(run: RunContext) -> str:
    if not run.project_log_path.exists():
        return write_final_report(run, {"Status": "PROJECT_LOG.yaml is not available yet."})

    data = load_yaml_mapping(run.project_log_path, validator=validate_project_log)
    steps = data.get("steps") or []
    passed = [step for step in steps if (step.get("check") or {}).get("status") == "pass"]
    blocked = [step for step in steps if (step.get("check") or {}).get("status") == "fail"]
    overall_status = "DONE" if steps and len(passed) == len(steps) else ("BLOCKED" if blocked else "RUNNING")
    lines = [
        "# BioMaster Analysis Report",
        "",
        f"Project: `{data.get('project_name', run.run_id)}`",
        f"Project directory: `{data.get('project_dir', run.root)}`",
        f"Status: `{overall_status}`",
        f"Progress: `{len(passed)}/{len(steps)}` checked steps passed",
        "",
        "## Key Outputs",
        "",
        "- PLAN: [`PLAN.yaml`](PLAN.yaml)",
        "- Project log: [`PROJECT_LOG.yaml`](PROJECT_LOG.yaml)",
        "- Check report: [`CHECK_REPORT.yaml`](CHECK_REPORT.yaml)",
        "- OpenCode view: [`OPENCODE_VIEW.md`](OPENCODE_VIEW.md)",
        "",
        "## Step Audit Summary",
        "",
        "| Stage | Execution | Exit Code | Check | Conclusion |",
        "|---|---|---|---|---|",
    ]
    if not steps:
        lines.append("| none |  |  |  | No checked steps have been recorded yet. |")
    for step in steps:
        check = step.get("check") or {}
        execution = step.get("execution") or {}
        lines.append(
            "| "
            + " | ".join(
                [
                    _table_cell(step.get("step_id", "unknown")),
                    _table_cell(execution.get("status", "")),
                    _table_cell(execution.get("exit_code", "")),
                    _table_cell(check.get("status", "")),
                    _table_cell(check.get("conclusion", "")),
                ]
            )
            + " |"
        )
    lines.append("")

    if blocked:
        first_blocked = blocked[0]
        lines.extend(
            [
                "## Blocked / Next Action",
                "",
                f"- Blocked step: `{first_blocked.get('step_id', 'unknown')}`",
                f"- Reason: {(first_blocked.get('check') or {}).get('conclusion', '')}",
                "- Next action: review the step evidence, then retry the same step through Execute -> Debug -> Check.",
                "",
            ]
        )

    lines.extend(["## Step Details", ""])
    for step in steps:
        check = step.get("check") or {}
        execution = step.get("execution") or {}
        reviewed_outputs = check.get("reviewed_outputs") or []
        lines.extend(
            [
                f"### {step.get('step_id', 'unknown')}",
                "",
                f"- Objective: {step.get('objective', '')}",
                f"- Script: `{step.get('script', '')}`",
                f"- stdout: `{execution.get('stdout', '')}`",
                f"- stderr: `{execution.get('stderr', '')}`",
                "",
                "| Expected Output | Status | Evidence / Reason |",
                "|---|---|---|",
            ]
        )
        if not reviewed_outputs:
            lines.append("| none recorded |  |  |")
        for output in reviewed_outputs:
            evidence = ", ".join(str(item) for item in output.get("evidence", [])) or output.get("reason", "")
            lines.append(
                "| "
                + " | ".join(
                    [
                        _table_cell(output.get("expected_output", "")),
                        _table_cell(output.get("status", "")),
                        _table_cell(evidence),
                    ]
                )
                + " |"
            )
        lines.append("")
    content = "\n".join(lines).rstrip() + "\n"
    run.report_path.write_text(content, encoding="utf-8")
    return content
