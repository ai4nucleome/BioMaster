from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
import argparse
import json
import re
import shutil
from typing import Any

import yaml

try:
    from biomaster.knowledge import DEFAULT_KNOWLEDGE_ROOT, PROJECT_ROOT
    from biomaster.skills.build_knowledge_skills import infer_analysis, infer_tool, slugify
    from biomaster.skills.manager import SkillCatalog
except ModuleNotFoundError:
    from build_knowledge_skills import infer_analysis, infer_tool, slugify
    from manager import SkillCatalog


BIOMASTER_SKILL_ROOT = PROJECT_ROOT
BIOMASTER_REPO_ROOT = PROJECT_ROOT.parent
PLAN_KNOWLEDGE = BIOMASTER_REPO_ROOT / "doc" / "Plan_Knowledge.json"
TASK_KNOWLEDGE = BIOMASTER_REPO_ROOT / "doc" / "Task_Knowledge.json"
KNOWLEDGE_ROOT = DEFAULT_KNOWLEDGE_ROOT
WORKFLOW_ROOT = KNOWLEDGE_ROOT / "workflows"
TASK_ROOT = KNOWLEDGE_ROOT / "tasks"
REPORT_PATH = KNOWLEDGE_ROOT / "build_report.yaml"
TARGET_WORKFLOW_RECORDS = 56
TARGET_TASK_RECORDS = 76
OBSOLETE_GENERATED_PATHS = (
    BIOMASTER_SKILL_ROOT / ".opencode" / "skills_migrated_draft",
    BIOMASTER_SKILL_ROOT / ".opencode" / "workflows",
    BIOMASTER_SKILL_ROOT / ".opencode" / "workflows" / "migrated_draft",
)

TOOL_KEYWORDS = (
    "FastQC",
    "Trimmomatic",
    "Cutadapt",
    "STAR-Fusion",
    "STAR",
    "HISAT2",
    "Bowtie2",
    "BWA",
    "samtools",
    "featureCounts",
    "DESeq2",
    "MACS3",
    "Seurat",
    "Scanpy",
    "clusterProfiler",
    "GeneFEAST",
    "MAFin",
    "dorado",
    "eventalign",
    "bedtools",
    "cooler",
)


@dataclass(frozen=True)
class KnowledgeRecord:
    record_id: str
    title: str
    summary: str
    keywords: list[str]
    path: Path
    source_file: str
    origin_source: str
    origin_page: int | str
    source_entry_index: int
    source_subindex: int
    content: str
    category: str
    canonical_skill: str

    @property
    def relative_path(self) -> str:
        return self.path.relative_to(BIOMASTER_SKILL_ROOT).as_posix()

    def registry_entry(self, skill_key: str) -> dict[str, Any]:
        entry = {
            "id": self.record_id,
            "title": self.title,
            "summary": self.summary,
            "keywords": self.keywords,
            "path": self.relative_path,
            "origin_source": self.origin_source,
            "origin_page": self.origin_page,
            "source_entry_index": self.source_entry_index,
            "source_subindex": self.source_subindex,
            "source_file": self.source_file,
            "status": "active",
        }
        entry[skill_key] = self.canonical_skill
        if skill_key == "canonical_plan_skill":
            entry["analysis_type"] = self.category
        else:
            entry["tool"] = self.category
        return entry


def load_json(path: Path) -> list[dict[str, Any]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError(f"{path} must contain a JSON array")
    return data


def compact_text(value: str, limit: int = 220) -> str:
    text = re.sub(r"\s+", " ", value).strip()
    if len(text) <= limit:
        return text
    return text[: limit - 3].rstrip() + "..."


def title_from_content(content: str, fallback: str) -> str:
    for line in content.splitlines():
        cleaned = line.strip().strip("# -*\t")
        if cleaned:
            return compact_text(cleaned, limit=100)
    return fallback


def keyword_list(*values: str) -> list[str]:
    keywords: list[str] = []
    for value in values:
        if not value:
            continue
        for part in re.split(r"[,;/|]+|\s{2,}", value):
            cleaned = part.strip(" .:_-")
            if cleaned:
                keywords.append(cleaned)
    joined = " ".join(values)
    for tool in TOOL_KEYWORDS:
        if re.search(rf"\b{re.escape(tool)}\b", joined, re.IGNORECASE):
            keywords.append(tool)
    return list(dict.fromkeys(keywords))


def existing_skill_or_fallback(catalog: SkillCatalog, candidate: str, fallback: str) -> str:
    try:
        catalog.get(candidate)
    except KeyError:
        return fallback
    return candidate


def skill_name_for_record(kind: str, record_id: str, title: str) -> str:
    prefix = "plan" if kind == "workflow" else "exec"
    fallback = "plan" if kind == "workflow" else "exec"
    return f"{prefix}-{record_id}-{slugify(title, fallback=fallback)}"[:120].rstrip("-")


def split_by_pattern(content: str, pattern: str, max_sections: int) -> list[str]:
    matches = list(re.finditer(pattern, content, flags=re.IGNORECASE | re.MULTILINE))
    if len(matches) <= 1 or max_sections <= 1:
        return [content]
    selected = matches[:max_sections]
    sections: list[str] = []
    for index, match in enumerate(selected):
        start = match.start()
        end = selected[index + 1].start() if index + 1 < len(selected) else len(content)
        section = content[start:end].strip()
        if section:
            sections.append(section)
    return sections or [content]


def normalize_items(
    items: list[dict[str, Any]],
    target_count: int,
    split_patterns: tuple[str, ...],
) -> list[tuple[dict[str, Any], int, int, str]]:
    records: list[tuple[dict[str, Any], int, int, str]] = []
    remaining_extra = target_count - len(items)
    if remaining_extra < 0:
        raise ValueError(f"target_count {target_count} is smaller than source item count {len(items)}")

    for source_index, item in enumerate(items, start=1):
        content = str(item.get("content", "")).strip()
        sections = [content]
        if remaining_extra > 0:
            for pattern in split_patterns:
                candidate = split_by_pattern(content, pattern, max_sections=remaining_extra + 1)
                if len(candidate) > 1:
                    sections = candidate
                    break
        if len(sections) > 1:
            remaining_extra -= len(sections) - 1
        for subindex, section in enumerate(sections, start=1):
            records.append((item, source_index, subindex, section))

    if len(records) != target_count:
        raise ValueError(f"normalized record count mismatch: {len(records)} != {target_count}")
    return records


def workflow_record(
    index: int,
    item: dict[str, Any],
    catalog: SkillCatalog,
    source_entry_index: int,
    source_subindex: int = 1,
    content_override: str | None = None,
) -> KnowledgeRecord:
    metadata = item.get("metadata") or {}
    source = str(metadata.get("source", "unknown")).strip()
    page = metadata.get("page", index)
    content = (content_override if content_override is not None else str(item.get("content", ""))).strip()
    analysis = slugify(infer_analysis(source, content, page))
    title = title_from_content(content, fallback=f"Workflow record {index:04d}")
    summary = compact_text(content)
    record_id = f"wf-{index:04d}"
    canonical_plan = "plan-workflow"
    filename = f"{record_id}-{slugify(title, fallback='workflow')}.md"
    return KnowledgeRecord(
        record_id=record_id,
        title=title,
        summary=summary,
        keywords=keyword_list(analysis, source, title, content[:1200]),
        path=WORKFLOW_ROOT / filename,
        source_file=PLAN_KNOWLEDGE.relative_to(BIOMASTER_REPO_ROOT).as_posix(),
        origin_source=source,
        origin_page=page,
        source_entry_index=source_entry_index,
        source_subindex=source_subindex,
        content=content,
        category=analysis,
        canonical_skill=canonical_plan,
    )


def task_record(
    index: int,
    item: dict[str, Any],
    catalog: SkillCatalog,
    source_entry_index: int,
    source_subindex: int = 1,
    content_override: str | None = None,
) -> KnowledgeRecord:
    metadata = item.get("metadata") or {}
    source = str(metadata.get("source", "unknown")).strip()
    page = metadata.get("page", index)
    content = (content_override if content_override is not None else str(item.get("content", ""))).strip()
    tool = slugify(infer_tool(source, content, page))
    title = title_from_content(content, fallback=f"Task record {index:04d}")
    summary = compact_text(content)
    record_id = f"task-{index:04d}"
    lowered_content = content.lower()
    if "conda install" in lowered_content or "conda create" in lowered_content or "mamba install" in lowered_content:
        candidate_exec = "exec-conda"
    elif "biocmanager" in lowered_content or "install.packages" in lowered_content or "rscript" in lowered_content:
        candidate_exec = "exec-r-package"
    else:
        candidate_exec = f"exec-{tool}"
    canonical_exec = existing_skill_or_fallback(catalog, candidate_exec, "exec-task")
    filename = f"{record_id}-{slugify(title, fallback='task')}.md"
    return KnowledgeRecord(
        record_id=record_id,
        title=title,
        summary=summary,
        keywords=keyword_list(tool, source, title, content[:1200]),
        path=TASK_ROOT / filename,
        source_file=TASK_KNOWLEDGE.relative_to(BIOMASTER_REPO_ROOT).as_posix(),
        origin_source=source,
        origin_page=page,
        source_entry_index=source_entry_index,
        source_subindex=source_subindex,
        content=content,
        category=tool,
        canonical_skill=canonical_exec,
    )


def render_record(record: KnowledgeRecord, kind: str, skill_key: str) -> str:
    frontmatter = record.registry_entry(skill_key)
    frontmatter_text = yaml.safe_dump(frontmatter, sort_keys=False, allow_unicode=True).strip()
    safe_content = record.content.replace("```", "~~~")
    heading = "Workflow" if kind == "workflow" else "Task"
    return f"""---
{frontmatter_text}
---

# {record.title}

## One-line description

{record.summary}

## Source

- Source file: `{record.source_file}`
- Origin source: `{record.origin_source}`
- Origin page: `{record.origin_page}`
- Source entry index: `{record.source_entry_index}`
- Source subindex: `{record.source_subindex}`
- Canonical skill: `{record.canonical_skill}`

## Inputs

Extract user-provided data paths, sample metadata, reference files, tool parameters, and execution permissions from the user request. Do not reuse source example paths without user confirmation.

## Steps

Use the original source excerpt below as the authoritative source-specific procedure. Convert prose or script-specific instructions into explicit, ordered plan or execution steps before use.

## Tool mapping

- Canonical skill: `{record.canonical_skill}`
- Registry ID: `{record.record_id}`
- Analysis/tool category: `{record.category}`

## Expected outputs

Derive expected outputs from the selected source excerpt and normalize them into user-specific output directories.

## Validation hints

Validate required inputs, generated outputs, logs, and format-specific assumptions before handing results to the next agent.

## Suggested use

Use this numbered {kind} record as source-specific BioMaster knowledge. Core OpenCode skills should select this record through the registry, then normalize paths, sample names, and output directories before generating a plan or command.

## Original source excerpt

```text
{safe_content}
```

## Curation notes

- Keep this record as provenance-preserving knowledge.
- Do not copy example paths directly into user workflows.
- Combine this record with the canonical `{heading.lower()}` skill before producing user-facing outputs.
"""


def write_records(records: list[KnowledgeRecord], root: Path, kind: str, skill_key: str) -> None:
    root.mkdir(parents=True, exist_ok=True)
    for record in records:
        record.path.write_text(render_record(record, kind=kind, skill_key=skill_key), encoding="utf-8")


def write_registry(records: list[KnowledgeRecord], path: Path, key: str, skill_key: str) -> None:
    path.write_text(
        yaml.safe_dump(
            {key: [record.registry_entry(skill_key) for record in records]},
            sort_keys=False,
            allow_unicode=True,
        ),
        encoding="utf-8",
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Build BioMaster numbered workflow/task knowledge libraries.")
    parser.add_argument("--keep-existing", action="store_true", help="do not remove existing knowledge library files first")
    args = parser.parse_args()

    if not args.keep_existing:
        for path in (KNOWLEDGE_ROOT, *OBSOLETE_GENERATED_PATHS):
            if path.exists():
                shutil.rmtree(path)
    WORKFLOW_ROOT.mkdir(parents=True, exist_ok=True)
    TASK_ROOT.mkdir(parents=True, exist_ok=True)

    catalog = SkillCatalog.from_root()
    plan_items = load_json(PLAN_KNOWLEDGE)
    task_items = load_json(TASK_KNOWLEDGE)
    normalized_workflows = normalize_items(
        plan_items,
        target_count=TARGET_WORKFLOW_RECORDS,
        split_patterns=(r"^\s*\d+\.\s+.*?\.sh\s*:",),
    )
    normalized_tasks = normalize_items(
        task_items,
        target_count=TARGET_TASK_RECORDS,
        split_patterns=(r"^\s*\d+\.\s+.+",),
    )
    workflows = [
        workflow_record(index, item, catalog, source_entry_index=source_index, source_subindex=subindex, content_override=content)
        for index, (item, source_index, subindex, content) in enumerate(normalized_workflows, start=1)
    ]
    tasks = [
        task_record(index, item, catalog, source_entry_index=source_index, source_subindex=subindex, content_override=content)
        for index, (item, source_index, subindex, content) in enumerate(normalized_tasks, start=1)
    ]

    write_records(workflows, WORKFLOW_ROOT, kind="workflow", skill_key="canonical_plan_skill")
    write_registry(workflows, WORKFLOW_ROOT / "registry.yaml", key="workflows", skill_key="canonical_plan_skill")
    write_records(tasks, TASK_ROOT, kind="task", skill_key="canonical_exec_skill")
    write_registry(tasks, TASK_ROOT / "registry.yaml", key="tasks", skill_key="canonical_exec_skill")

    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_files": [
            PLAN_KNOWLEDGE.relative_to(BIOMASTER_REPO_ROOT).as_posix(),
            TASK_KNOWLEDGE.relative_to(BIOMASTER_REPO_ROOT).as_posix(),
        ],
        "summary": {
            "source_plan_entries": len(plan_items),
            "source_task_entries": len(task_items),
            "workflow_records": len(workflows),
            "task_records": len(tasks),
            "target_workflow_records": TARGET_WORKFLOW_RECORDS,
            "target_task_records": TARGET_TASK_RECORDS,
        },
    }
    REPORT_PATH.write_text(yaml.safe_dump(report, sort_keys=False, allow_unicode=True), encoding="utf-8")

    print(f"Wrote {len(workflows)} workflow records to {WORKFLOW_ROOT}")
    print(f"Wrote {len(tasks)} task records to {TASK_ROOT}")
    print(f"Wrote report to {REPORT_PATH}")


if __name__ == "__main__":
    main()
