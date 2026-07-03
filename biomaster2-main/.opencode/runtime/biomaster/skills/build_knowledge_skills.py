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
    from biomaster.knowledge import OPENCODE_ROOT, PROJECT_ROOT
    from biomaster.skills.manager import DEFAULT_SKILL_ROOT, SkillCatalog
except ModuleNotFoundError:
    from manager import DEFAULT_SKILL_ROOT, SkillCatalog


BIOMASTER_SKILL_ROOT = PROJECT_ROOT
BIOMASTER_REPO_ROOT = PROJECT_ROOT.parent
PLAN_KNOWLEDGE = BIOMASTER_REPO_ROOT / "doc" / "Plan_Knowledge.json"
TASK_KNOWLEDGE = BIOMASTER_REPO_ROOT / "doc" / "Task_Knowledge.json"
REPORT_PATH = OPENCODE_ROOT / "knowledge_build_report.yaml"
TARGET_WORKFLOW_SKILLS = 56
TARGET_EXECUTE_SKILLS = 76

OCR_MARKERS = ("pageent", "provpage", "euclpage", "quantififation", "Indendetection")
HARDCODED_PATH_RE = re.compile(r"/home/agent/|(?:^|\s)\./output/\d+|(?:^|\s)\./data/", re.IGNORECASE)
COMMAND_RE = re.compile(
    r"```(?:bash|sh|shell)|\b(?:bash|Rscript|samtools|fastqc|featureCounts|STAR|bwa|bowtie2|hisat2|conda)\b",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class KnowledgeSkill:
    name: str
    canonical: str
    status: str
    aliases: str
    layer: str
    metadata_key: str
    metadata_value: str
    description: str
    source_file: str
    origin_source: str
    origin_page: int | str
    record_id: str
    source_entry_index: int
    source_subindex: int
    content: str
    issues: list[str]


def load_json(path: Path) -> list[dict[str, Any]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError(f"{path} must contain a JSON array")
    return data


def slugify(value: str, fallback: str = "entry") -> str:
    text = value.lower().strip()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    text = re.sub(r"-+", "-", text).strip("-")
    return text or fallback


def compact_description(content: str, layer: str) -> str:
    first = next((line.strip("# -*\t") for line in content.splitlines() if line.strip()), "")
    first = re.sub(r"\s+", " ", first).strip()
    if len(first) > 150:
        first = first[:147].rstrip() + "..."
    if first:
        return first
    return f"Use this BioMaster {layer} skill generated from the legacy knowledge base."


def title_for_skill(content: str, fallback: str) -> str:
    first = next((line.strip("# -*\t") for line in content.splitlines() if line.strip()), "")
    first = re.sub(r"\s+", " ", first).strip()
    if len(first) > 100:
        first = first[:97].rstrip() + "..."
    return first or fallback


def infer_tool(source: str, content: str, page: int | str) -> str:
    source_clean = source.strip()
    if source_clean.endswith(".sh"):
        return source_clean[:-3]
    if source_clean.lower().startswith("run-"):
        return source_clean

    patterns = (
        r"\b(featureCounts)\b",
        r"\b(samtools)\b",
        r"\b(DESeq2)\b",
        r"\b(FastQC)\b",
        r"\b(Trimmomatic)\b",
        r"\b(Cutadapt)\b",
        r"\b(STAR-Fusion|STAR)\b",
        r"\b(HISAT2)\b",
        r"\b(Bowtie2)\b",
        r"\b(BWA(?:-MEM)?)\b",
        r"\b(MACS3)\b",
        r"\b(Seurat)\b",
        r"\b(Scanpy)\b",
        r"\b(DiffBind)\b",
        r"\b(clusterProfiler)\b",
        r"\b(bedtools)\b",
        r"\b(cooler)\b",
        r"\b(dorado)\b",
    )
    for pattern in patterns:
        match = re.search(pattern, content, re.IGNORECASE)
        if match:
            return slugify(match.group(1))

    return slugify(source_clean, fallback=f"tool-{page}")


def infer_analysis(source: str, content: str, page: int | str) -> str:
    haystack = f"{source} {content}".lower()
    def has_keyword(keyword: str) -> bool:
        escaped = re.escape(keyword.lower())
        if re.fullmatch(r"[a-z0-9+-]+", keyword.lower()):
            return re.search(rf"(?<![a-z0-9]){escaped}(?![a-z0-9])", haystack) is not None
        return keyword.lower() in haystack

    mappings = [
        ("rnaseq-de", ("rna-seq", "rnaseq", "differential expression", "deg")),
        ("chipseq-peak", ("chip-seq", "chipseq", "peak calling")),
        ("scrnaseq-cluster", ("scrna", "single-cell", "single cell", "seurat", "scanpy")),
        ("hic-matrix", ("hi-c", "hic", "cooler", "pairsam", "juicer")),
        ("spatial-transcriptomics", ("spatial", "squidpy", "nichepca")),
        ("nanopore", ("nanopore", "dorado", "eventalign")),
        ("variant-calling", ("variant", "vcf", "gatk", "bcftools")),
        ("functional-enrichment", ("enrichment", "clusterprofiler", "gene ontology", "kegg")),
        ("metagenomics", ("metagenomic", "microbiome", "phyloseq")),
        ("motif-analysis", ("motif", "mafin", "jaspar")),
        ("annotation-comparison", ("annotation", "rnalib", "transcriptome")),
    ]
    for name, keywords in mappings:
        if any(has_keyword(keyword) for keyword in keywords):
            return name
    return slugify(source, fallback=f"workflow-{page}")


def classify_entry(source_file: str, item: dict[str, Any]) -> tuple[str, str]:
    metadata = item.get("metadata") or {}
    source = str(metadata.get("source", "unknown"))
    page = metadata.get("page", "x")
    content = str(item.get("content", ""))
    source_lower = source.lower().strip()
    content_head = content.lower()[:500]

    if "Plan_Knowledge" in source_file:
        if source_lower == "tools" and COMMAND_RE.search(content):
            return "execute", infer_tool(source, content, page)
        return "plan", infer_analysis(source, content, page)

    if "workflow" in source_lower or "workflow" in content_head:
        return "plan", infer_analysis(source, content, page)
    return "execute", infer_tool(source, content, page)


def detect_issues(source_file: str, item: dict[str, Any], seen_sources: set[str]) -> list[str]:
    metadata = item.get("metadata") or {}
    source = str(metadata.get("source", "unknown"))
    content = str(item.get("content", ""))
    source_key = f"{source_file}:{source}"
    issues: list[str] = []

    if source_key in seen_sources:
        issues.append("duplicate_source_label")
    seen_sources.add(source_key)
    if any(marker.lower() in content.lower() for marker in OCR_MARKERS):
        issues.append("possible_ocr_noise")
    if HARDCODED_PATH_RE.search(content):
        issues.append("contains_example_paths")
    if "Task_Knowledge" in source_file and "workflow" in source.lower():
        issues.append("workflow_record_from_task_knowledge")
    if "Plan_Knowledge" in source_file and COMMAND_RE.search(content):
        issues.append("command_like_text_in_plan_source")

    return issues


def unique_name(base_name: str, used_names: set[str], source: str, page: int | str) -> str:
    candidates = [
        base_name,
        f"{base_name}-{page}",
        f"{base_name}-{slugify(source)}-{page}",
    ]
    for candidate in candidates:
        if candidate not in used_names:
            used_names.add(candidate)
            return candidate

    suffix = 2
    while True:
        candidate = f"{base_name}-{slugify(source)}-{page}-{suffix}"
        if candidate not in used_names:
            used_names.add(candidate)
            return candidate
        suffix += 1


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


def build_skill(
    source_file: str,
    item: dict[str, Any],
    used_names: set[str],
    seen_sources: set[str],
) -> KnowledgeSkill:
    metadata = item.get("metadata") or {}
    source = str(metadata.get("source", "unknown")).strip()
    page = metadata.get("page", "x")
    content = str(item.get("content", "")).strip()
    layer, inferred_value = classify_entry(source_file, item)
    prefix = "plan" if layer == "plan" else "exec"
    metadata_key = "analysis" if layer == "plan" else "tool"
    inferred_slug = slugify(inferred_value)
    base_name = f"{prefix}-{inferred_slug}"
    name = unique_name(base_name, used_names, source, page)
    canonical = base_name
    status = "active" if name == canonical else "variant"
    aliases = ", ".join(
        dict.fromkeys(
            item
            for item in (
                inferred_slug,
                inferred_value,
                source,
                str(page),
            )
            if str(item).strip()
        )
    )

    return KnowledgeSkill(
        name=name,
        canonical=canonical,
        status=status,
        aliases=aliases,
        layer=layer,
        metadata_key=metadata_key,
        metadata_value=inferred_slug,
        description=compact_description(content, layer),
        source_file=source_file,
        origin_source=source,
        origin_page=page,
        record_id=str(page),
        source_entry_index=int(page) if str(page).isdigit() else 0,
        source_subindex=1,
        content=content,
        issues=detect_issues(source_file, item, seen_sources),
    )


def build_record_skill(
    *,
    kind: str,
    index: int,
    item: dict[str, Any],
    source_file: str,
    source_entry_index: int,
    source_subindex: int,
    content: str,
    seen_sources: set[str],
) -> KnowledgeSkill:
    metadata = item.get("metadata") or {}
    source = str(metadata.get("source", "unknown")).strip()
    page = metadata.get("page", source_entry_index)
    record_prefix = "wf" if kind == "workflow" else "task"
    record_id = f"{record_prefix}-{index:04d}"
    if kind == "workflow":
        metadata_value = slugify(infer_analysis(source, content, page))
        name = f"plan-{record_id}-{slugify(title_for_skill(content, 'plan'), fallback='plan')}"
        layer = "plan"
        metadata_key = "analysis"
    else:
        metadata_value = slugify(infer_tool(source, content, page))
        name = f"exec-{record_id}-{slugify(title_for_skill(content, 'exec'), fallback='exec')}"
        layer = "execute"
        metadata_key = "tool"

    aliases = ", ".join(
        dict.fromkeys(
            value
            for value in (
                record_id,
                metadata_value,
                source,
                str(page),
            )
            if str(value).strip()
        )
    )
    return KnowledgeSkill(
        name=name[:120].rstrip("-"),
        canonical=name[:120].rstrip("-"),
        status="active",
        aliases=aliases,
        layer=layer,
        metadata_key=metadata_key,
        metadata_value=metadata_value,
        description=compact_description(content, layer),
        source_file=source_file,
        origin_source=source,
        origin_page=page,
        record_id=record_id,
        source_entry_index=source_entry_index,
        source_subindex=source_subindex,
        content=content,
        issues=detect_issues(source_file, item, seen_sources),
    )


def render_skill(skill: KnowledgeSkill) -> str:
    frontmatter = {
        "name": skill.name,
        "description": skill.description,
        "compatibility": "opencode",
        "metadata": {
            "layer": skill.layer,
            "domain": "bioinformatics",
            skill.metadata_key: skill.metadata_value,
            "source": "legacy-knowledge",
            "status": skill.status,
            "canonical": skill.canonical,
            "aliases": skill.aliases,
            "origin_source": skill.origin_source,
            "origin_page": str(skill.origin_page),
            "record_id": skill.record_id,
            "source_entry_index": str(skill.source_entry_index),
            "source_subindex": str(skill.source_subindex),
        },
    }
    frontmatter_text = yaml.safe_dump(frontmatter, sort_keys=False, allow_unicode=True).strip()
    title = "Plan Knowledge Skill" if skill.layer == "plan" else "Execute Knowledge Skill"
    safe_content = skill.content.replace("```", "~~~")

    return f"""---
{frontmatter_text}
---

# {skill.name} {title}

## Purpose

Use this skill as one migrated BioMaster {skill.layer} knowledge record.

It corresponds to one normalized source record from `{skill.source_file}` and preserves source-specific knowledge for agent retrieval.

## When to use

Load this skill only when the responsible BioMaster agent is allowed to access the `{skill.layer}` layer.

## Inputs

Extract required inputs from the original source excerpt. Normalize example paths, sample names, references, and output directories before use.

## Outputs

Derive expected outputs from the source excerpt and convert them into the current user's workflow-specific output paths.

## Procedure

1. Read the source excerpt.
2. Identify reusable workflow or execution logic.
3. Keep source-specific assumptions explicit.
4. Combine this knowledge with the current user request and agent role boundaries.
5. Do not copy hard-coded example paths into user-facing outputs.

## Validation

Validate that any generated plan, command, or report respects BioMaster's intake/plan/execute/verify/debug separation.

## Source Trace

- Record ID: `{skill.record_id}`
- Source entry index: `{skill.source_entry_index}`
- Source subindex: `{skill.source_subindex}`
- Origin source: `{skill.origin_source}`
- Origin page: `{skill.origin_page}`

## Original Source Excerpt

```text
{safe_content}
```

## Source-quality notes

{', '.join(skill.issues) if skill.issues else 'none detected'}.
"""


def write_skill(skill: KnowledgeSkill, overwrite_generated: bool) -> str:
    skill_dir = DEFAULT_SKILL_ROOT / skill.name
    skill_file = skill_dir / "SKILL.md"
    if skill_file.exists() and not overwrite_generated:
        return "kept_existing"
    if skill_file.exists() and overwrite_generated:
        existing_text = skill_file.read_text(encoding="utf-8")
        if "source: legacy-knowledge" not in existing_text:
            return "kept_manual"

    skill_dir.mkdir(parents=True, exist_ok=True)
    skill_file.write_text(render_skill(skill), encoding="utf-8")
    return "written"


def collect_knowledge_skills() -> list[KnowledgeSkill]:
    # Legacy Plan/Task records are intentionally stored under .opencode/knowledge
    # rather than as active skills, so OpenCode loads only curated entry skills.
    return []


def clean_generated_skills() -> int:
    removed = 0
    for skill_dir in sorted(path for path in DEFAULT_SKILL_ROOT.iterdir() if path.is_dir()):
        skill_file = skill_dir / "SKILL.md"
        if not skill_file.exists():
            continue
        text = skill_file.read_text(encoding="utf-8")
        if "source: legacy-knowledge" in text or skill_dir.name.startswith(("workflow-", "execute-")):
            shutil.rmtree(skill_dir)
            removed += 1
    return removed


def main() -> None:
    parser = argparse.ArgumentParser(description="Build active OpenCode skills from the legacy BioMaster knowledge bases.")
    parser.add_argument(
        "--overwrite-generated",
        action="store_true",
        help="rewrite existing skills generated from legacy knowledge while preserving manual seed skills",
    )
    parser.add_argument(
        "--keep-generated",
        action="store_true",
        help="do not remove previously generated legacy-knowledge skills before rebuilding",
    )
    args = parser.parse_args()

    removed = 0 if args.keep_generated else clean_generated_skills()
    skills = collect_knowledge_skills()
    results: dict[str, int] = {}
    report_items = []
    for skill in skills:
        result = write_skill(skill, overwrite_generated=args.overwrite_generated)
        results[result] = results.get(result, 0) + 1
        report_items.append(
            {
                "name": skill.name,
                "layer": skill.layer,
                "source_file": skill.source_file,
                "origin_source": skill.origin_source,
                "origin_page": skill.origin_page,
                "canonical": skill.canonical,
                "status": skill.status,
                "result": result,
                "issues": skill.issues,
            }
        )

    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_files": [
            PLAN_KNOWLEDGE.relative_to(BIOMASTER_REPO_ROOT).as_posix(),
            TASK_KNOWLEDGE.relative_to(BIOMASTER_REPO_ROOT).as_posix(),
        ],
        "summary": {
            "total_knowledge_skills": len(skills),
            "removed_previous_generated_skills": removed,
            "results": results,
        },
        "skills": report_items,
    }
    REPORT_PATH.write_text(yaml.safe_dump(report, sort_keys=False, allow_unicode=True), encoding="utf-8")

    print(f"Processed {len(skills)} legacy knowledge entries")
    print(f"Removed previous generated skills: {removed}")
    for key in sorted(results):
        print(f"- {key}: {results[key]}")
    print(f"Wrote report to {REPORT_PATH}")


if __name__ == "__main__":
    main()
