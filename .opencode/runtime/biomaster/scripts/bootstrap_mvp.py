#!/usr/bin/env python3
"""Bootstrap BioMaster-OpenCode MVP skills, commands, examples, and runs layout."""
from __future__ import annotations

from pathlib import Path
import textwrap

ROOT = Path(__file__).resolve().parents[4]
OPENCODE_ROOT = ROOT / ".opencode"
SKILLS = OPENCODE_ROOT / "skills"
INTERNAL_SKILLS = OPENCODE_ROOT / "biomaster-internal" / "skills"
COMMANDS = OPENCODE_ROOT / "commands"
EXAMPLES = ROOT / "examples" / "tumor_scrnaseq_heterogeneity"
PROJECTS = ROOT / "projects"


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        return
    path.write_text(content.strip() + "\n", encoding="utf-8")


def skill_md(name: str, description: str, layer: str, extra_meta: dict[str, str], body: str) -> str:
    meta_lines = [f"  layer: {layer}"]
    for key, value in extra_meta.items():
        meta_lines.append(f"  {key}: {value}")
    meta = "\n".join(meta_lines)
    return f"""---
name: {name}
description: {description}
compatibility: opencode
metadata:
{meta}
---

{body.strip()}
"""


def bootstrap_skills() -> None:
    specs: list[tuple[str, str, str, dict[str, str], str]] = [
        (
            "biomaster",
            "Load BioMaster as one integrated skill-driven bioinformatics assistant.",
            "registry",
            {"domain": "bioinformatics", "status": "active"},
            """
# BioMaster

## Purpose
Load BioMaster as a single integrated system, not as a menu of individual skills.

## When to use
Use at cold start or whenever the user asks to load BioMaster.

## Operating model
The visible conversation owner is always `biomaster-plan`. Internal modules such as `registry`, `domain-guide-*`, `plan-*`, `exec-*`, `verify-*`, and `debug-*` are selected by phase and should not be offered to the user as choices.

## Initial response
Use a readable English start card:

```
## BioMaster Ready

**Primary agent:** `biomaster-plan`
**Control plane:** SQLite route and skill gates
**Workspace model:** `projects/<project_slug>/`
```

Then ask the user to choose test mode, formal analysis, or a custom scientific objective.

Use OpenCode's native option selector / QuestionTool for operating mode, project continuation/new-project choices, and risky execution confirmations whenever available.

## Boundaries
Do not list internal skills as user-selectable options. Do not skip the fixed workflow order.
After route selection, always inspect existing `projects/` candidates before planning.
Use semantic project slugs based on dataset, analysis type, and goal; do not create ambiguous numeric project IDs.
Keep user-facing output concise by default; write detailed evidence to PROJECT_LOG.yaml, REPORT.md, and OPENCODE_VIEW.md.
""",
        ),
        (
            "domain-guide-tumor",
            "Define tumor research modes and route tumor scRNA-seq pipelines.",
            "domain-guide",
            {"domain": "tumor", "status": "active"},
            """
# Tumor Domain Guide

## Purpose
Define tumor research conversation entry, operating modes, and supported pipeline families.

## When to use
Load during intake before collecting detailed sample metadata.

## First interaction rule
Ask only for operating mode on the first turn:
1. test mode — run built-in demo data end-to-end
2. formal analysis — user supplies real data paths and sample metadata
3. custom request — user describes the task in free text

Do not mix mode selection with data path, cancer type, or sample questions.

## Outputs
```
domain: tumor
mode: test | formal | custom
candidate_pipelines:
  - tumor_scrnaseq_heterogeneity
missing_information:
next_skill_candidates:
  - discipline-scrnaseq
  - biomaster
  - pipeline-scrnaseq-tumor
  - plan-scrnaseq-tumor-heterogeneity
```

## Boundaries
Do not execute commands, generate PLAN.yaml, or load exec/debug skills.
""",
        ),
        (
            "discipline-scrnaseq",
            "Define scRNA-seq input requirements and generic analysis conventions.",
            "discipline",
            {"discipline": "scrnaseq", "domain": "bioinformatics", "status": "active"},
            """
# scRNA-seq Discipline Guide

## Purpose
Define scRNA-seq input formats, QC norms, and generic workflow stages without binding a tumor-specific pipeline.

## Inputs
- h5ad AnnData
- 10x matrix bundle (matrix.mtx, genes.tsv, barcodes.tsv)
- filtered feature-barcode matrix

## Generic stages
data loading → QC → normalization → HVG → PCA/UMAP → clustering → annotation

## Boundaries
Do not bind inferCNVpy, Palantir, or cNMF unless pipeline-scrnaseq-tumor is selected.
""",
        ),
        (
            "pipeline-scrnaseq-tumor",
            "Define tumor scRNA-seq pipeline family and phase-1 demo target.",
            "pipeline",
            {"pipeline": "tumor_scrnaseq", "discipline": "scrnaseq", "domain": "tumor", "status": "active"},
            """
# Tumor scRNA-seq Pipeline Family

## Supported analyses
- tumor heterogeneity and state trajectory (phase 1 MVP)
- tumor microenvironment cell communication (future)
- immune infiltration and treatment response (future)

## Phase 1 target
`tumor_scrnaseq_heterogeneity` with demo dataset `maynard2020_3k`.

## Tool chain
Scanpy, inferCNVpy, Palantir, cNMF, reporting.

## Boundaries
Routing only — no command execution.
""",
        ),
        (
            "plan-scrnaseq-tumor-heterogeneity",
            "Generate PLAN.yaml for tumor scRNA-seq heterogeneity and trajectory analysis.",
            "plan",
            {
                "domain": "tumor",
                "discipline": "scrnaseq",
                "pipeline": "tumor_heterogeneity",
                "analysis": "tumor_scrnaseq_heterogeneity",
                "status": "active",
            },
            """
# Plan: Tumor scRNA-seq Heterogeneity

## Purpose
Generate structured PLAN.yaml only. Read IO_CONTRACT.md and manifests/ before planning.

## Workflow steps
1. data preflight
2. cell and gene QC
3. doublet removal
4. batch correction
5. clustering and annotation
6. inferCNVpy malignancy
7. Palantir trajectory
8. cNMF modules
9. report generation

## PLAN.yaml rules
- declare step_id, objective, required_execute_skills, required_verify_skills
- declare expected_outputs and acceptance_criteria
- never embed shell commands

## Boundaries
No execution, no environment install, no debugging.
""",
        ),
    ]

    exec_tools = [
        ("exec-scanpy", "scanpy", "Run Scanpy QC, preprocessing, clustering, and annotation steps."),
        ("exec-infercnvpy", "infercnvpy", "Run inferCNVpy malignant cell identification."),
        ("exec-palantir", "palantir", "Run Palantir state trajectory analysis."),
        ("exec-cnmf", "cnmf", "Run cNMF co-expression module analysis."),
    ]
    for name, tool, desc in exec_tools:
        specs.append(
            (
                name,
                desc,
                "execute",
                {"tool": tool, "discipline": "scrnaseq", "domain": "tumor", "status": "active"},
                f"""
# {name}

## Purpose
Provide command templates, parameter conventions, log paths, and output conventions for {tool}.

## Procedure
1. Validate inputs against step contract.
2. Write script under `projects/<project_slug>/steps/<step_id>/`.
3. Execute with logged stdout/stderr.
4. Emit `step_result.yaml`.

## Boundaries
Do not replan workflow or modify PLAN objectives.
""",
            )
        )

    verify_specs = [
        ("verify-scrna-qc", "scrna_qc", "Verify scRNA-seq QC outputs and AnnData integrity."),
        ("verify-infercnv", "infercnv", "Verify inferCNVpy outputs and malignancy calls."),
        ("verify-trajectory", "trajectory", "Verify Palantir trajectory outputs."),
        ("verify-cnmf", "cnmf", "Verify cNMF module outputs."),
    ]
    for name, output, desc in verify_specs:
        specs.append(
            (
                name,
                desc,
                "verify",
                {"output": output, "discipline": "scrnaseq", "status": "active"},
                f"""
# {name}

## Output format
```
status: pass | fail
failed_check:
reason:
suggested_debug_skills:
next_action:
```

## Boundaries
Check only — never repair outputs or rewrite commands.
""",
            )
        )

    debug_specs = [
        ("debug-conda", "conda environment errors"),
        ("debug-tool-not-found", "missing CLI tool"),
        ("debug-missing-files", "missing input or reference files"),
        ("debug-python-package", "missing Python package"),
        ("debug-reference-genome", "reference genome or annotation mismatch"),
    ]
    for name, failure in debug_specs:
        specs.append(
            (
                name,
                f"Diagnose and repair {failure}.",
                "debug",
                {"failure": failure.replace(" ", "_"), "status": "active"},
                f"""
# {name}

## Purpose
Bounded repair for: {failure}.

## Boundaries
Fix only the failed step. Do not replan the workflow.
""",
            )
        )

    env_specs = [
        ("env-python-scrnaseq", "Python conda environment for scRNA-seq tools.", "scanpy,infercnvpy,palantir,cnmf"),
        ("env-r-bioc", "R/Bioconductor environment for auxiliary oncology plots.", "bioconductor"),
    ]
    for name, desc, env_contract in env_specs:
        specs.append(
            (
                name,
                desc,
                "env",
                {"tool": env_contract.split(",")[0], "env_contract": env_contract, "status": "active"},
                f"""
# {name}

## Purpose
Document conda env name, core packages, and verification commands.

## Boundaries
Plan Agent must not load full install details.
""",
            )
        )

    specs.append(
        (
            "report-tumor-scrnaseq",
            "Generate structured tumor scRNA-seq analysis report.",
            "report",
            {"domain": "tumor", "discipline": "scrnaseq", "status": "active"},
            """
# Tumor scRNA-seq Report

## Sections
- analysis overview
- data quality summary
- cell annotation
- malignancy identification
- trajectory results
- cNMF modules
- biological interpretation
- limitations and next steps

See REPORT_TEMPLATE.md in this skill directory.
""",
        )
    )

    for name, description, layer, extra, body in specs:
        skill_dir = (SKILLS if name == "biomaster" else INTERNAL_SKILLS) / name
        write(skill_dir / "SKILL.md", skill_md(name, description, layer, extra, body))

    plan_dir = INTERNAL_SKILLS / "plan-scrnaseq-tumor-heterogeneity"
    write(
        plan_dir / "IO_CONTRACT.md",
        """
# IO Contract: tumor_scrnaseq_heterogeneity

## Inputs
- test mode: demo dataset `maynard2020_3k` (Scanpy built-in or project subset)
- formal mode: h5ad or 10x matrix + sample metadata table

## Outputs
- QC AnnData (`adata_qc.h5ad`)
- annotated AnnData (`adata_annotated.h5ad`)
- inferCNV outputs (`infercnv/`)
- Palantir outputs (`palantir/`)
- cNMF outputs (`cnmf/`)
- final report (`REPORT.md`)
""",
    )
    manifests = [
        ("01_data_contract.md", "Validate readable h5ad or 10x matrix; report cell/gene counts."),
        ("02_qc_contract.md", "Filter low-quality cells/genes; retain mitochondrial fraction thresholds."),
        ("03_doublet_batch_contract.md", "Remove doublets; apply batch correction when batch column exists."),
        ("04_annotation_contract.md", "Cluster, UMAP, and marker-based annotation with confidence notes."),
        ("05_malignancy_contract.md", "inferCNVpy reference vs observation labels; export malignancy scores."),
        ("06_trajectory_contract.md", "Palantir pseudotime and branch probabilities for malignant subsets."),
        ("07_cnmf_contract.md", "cNMF rank selection and top gene modules with stability metrics."),
        ("08_report_contract.md", "Assemble REPORT.md with all prior step summaries."),
    ]
    for filename, summary in manifests:
        write(
            plan_dir / "manifests" / filename,
            f"# {filename.replace('_', ' ').replace('.md', '').title()}\n\n{summary}\n",
        )

    report_dir = INTERNAL_SKILLS / "report-tumor-scrnaseq"
    write(
        report_dir / "REPORT_TEMPLATE.md",
        """
# Tumor scRNA-seq Heterogeneity Report

## 1. Overview
## 2. Data Quality
## 3. Cell Annotation
## 4. Malignant Cells
## 5. Trajectory
## 6. cNMF Modules
## 7. Interpretation
## 8. Limitations
""",
    )

    qc_template = INTERNAL_SKILLS / "exec-scanpy" / "examples" / "qc_template.py"
    clustering_template = INTERNAL_SKILLS / "exec-scanpy" / "examples" / "clustering_template.py"
    write(
        qc_template,
        textwrap.dedent(
            '''
            """Scanpy QC template for tumor scRNA-seq pipeline."""
            from pathlib import Path
            import json

            def run_qc(run_dir: Path, step_id: str, dataset: str = "maynard2020_3k") -> dict:
                step_dir = run_dir / "steps" / step_id
                step_dir.mkdir(parents=True, exist_ok=True)
                summary = {"step_id": step_id, "tool": "scanpy", "dataset": dataset, "status": "completed"}
                (step_dir / "execution_log.txt").write_text(json.dumps(summary), encoding="utf-8")
                return summary
            '''
        ).strip()
        + "\n",
    )
    write(
        clustering_template,
        textwrap.dedent(
            '''
            """Scanpy clustering template for step 05."""
            from pathlib import Path
            import json

            def run_clustering(run_dir: Path, step_id: str) -> dict:
                step_dir = run_dir / "steps" / step_id
                step_dir.mkdir(parents=True, exist_ok=True)
                summary = {"step_id": step_id, "tool": "scanpy", "status": "completed", "clusters": 12}
                (step_dir / "execution_log.txt").write_text(json.dumps(summary), encoding="utf-8")
                return summary
            '''
        ).strip()
        + "\n",
    )

    for name, tool in [("exec-infercnvpy", "infercnvpy"), ("exec-palantir", "palantir"), ("exec-cnmf", "cnmf")]:
        write(
            INTERNAL_SKILLS / name / "examples" / f"{tool}_template.py",
            textwrap.dedent(
                f'''
                """Template stub for {tool} step execution."""
                def run_step(run_dir: str, step_id: str) -> dict:
                    return {{"tool": "{tool}", "step_id": step_id, "status": "stub"}}
                '''
            ).strip()
            + "\n",
        )


def bootstrap_commands() -> None:
    command_specs = {
        "biomaster-start.md": "Start BioMaster workflow, select or create a project folder, and invoke Plan Agent for mode selection.",
        "biomaster-plan.md": "Enter planning: Skill Finder + Plan Agent → PLAN.yaml",
        "biomaster-run.md": "Execute PLAN.yaml steps via Execute Agent.",
        "biomaster-check.md": "Check step outputs via Check Agent and verify skills.",
        "biomaster-debug.md": "Debug failed step via Debug Agent.",
        "biomaster-resume.md": "Resume an interrupted project from run_states or project files.",
    }
    for filename, purpose in command_specs.items():
        write(
            COMMANDS / filename,
            f"# {filename.replace('.md', '')}\n\nPurpose: {purpose}\n\nUsage: `/{filename.replace('.md', '')} <args>`\n",
        )


def bootstrap_examples() -> None:
    write(
        EXAMPLES / "user_request.md",
        """
# User Request

肿瘤异质性与状态轨迹分析

Use test mode with demo dataset maynard2020_3k.
""",
    )
    write(
        EXAMPLES / "demo_config.yaml",
        """
mode: test
domain: tumor
discipline: scrnaseq
pipeline: tumor_heterogeneity
dataset: maynard2020_3k
route_id: tumor_scrnaseq_heterogeneity
""",
    )
    write(
        EXAMPLES / "expected_PLAN.yaml",
        """
analysis_type: tumor_scrnaseq_heterogeneity
plan_id: "<auto_run_id>"
run_id: "<auto_run_id>"
project_id: "<project_slug>"
project_name: "<project_slug>"
project_dir: projects/<project_slug>
run_dir: projects/<project_slug>
plan_version: 1
mode: test
dataset: maynard2020_3k
route_id: tumor_scrnaseq_heterogeneity
selected_route_id: tumor_scrnaseq_heterogeneity

steps:
  - step_id: "01_data_preflight"
    objective: Validate input scRNA-seq data.
    required_execute_skills:
      - exec-scanpy
    required_verify_skills:
      - verify-scrna-qc
    expected_outputs:
      - input validation summary
    acceptance_criteria:
      - h5ad or 10x matrix is readable
      - cell and gene counts are reported
""",
    )


def main() -> None:
    if INTERNAL_SKILLS.exists():
        from biomaster.skills.migrate_legacy_bioskills import migrate_legacy_bioskills

        migrate_legacy_bioskills()
    bootstrap_examples()
    print(f"Bootstrap complete under {ROOT}")


if __name__ == "__main__":
    main()
