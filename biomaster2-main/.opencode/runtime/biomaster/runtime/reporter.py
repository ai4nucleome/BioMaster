from __future__ import annotations

from biomaster.runtime.run_context import RunContext


def write_final_report(run: RunContext, sections: dict[str, str]) -> str:
    lines = ["# BioMaster Analysis Report", ""]
    for title, body in sections.items():
        lines.append(f"## {title}")
        lines.append(body.strip())
        lines.append("")
    content = "\n".join(lines).strip() + "\n"
    path = run.root / "REPORT.md"
    path.write_text(content, encoding="utf-8")
    return content
