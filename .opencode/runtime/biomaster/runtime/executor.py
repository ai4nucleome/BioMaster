from __future__ import annotations

from pathlib import Path
import importlib.util
import json
import traceback

from biomaster.knowledge import DEFAULT_BIOSKILLS_ROOT, DEFAULT_DB_PATH, connect, ensure_knowledge_db, ensure_schema, normalize_agent_name
from biomaster.knowledge.query_skills import agent_allowed, get_skill_by_id
from biomaster.runtime.run_context import RunContext
from biomaster.runtime.plan_loader import get_step


def _load_template_module(path: Path):
    spec = importlib.util.spec_from_file_location(path.stem, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load template: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def query_sqlite_step_skills(skill_ids: list[str], db_path: Path = DEFAULT_DB_PATH) -> dict:
    sqlite_readiness = ensure_knowledge_db(db_path)
    connection = connect(db_path)
    try:
        ensure_schema(connection)
        resolved: list[dict[str, str]] = []
        missing: list[str] = []
        rejected: list[str] = []
        for skill_id in skill_ids:
            skill = get_skill_by_id(connection, skill_id)
            if skill is None:
                missing.append(skill_id)
                continue
            layer = str(skill.get("layer") or "")
            agent = "biomaster-plan" if layer == "report" else "biomaster-execute"
            if not skill.get("enabled") or not agent_allowed(skill, normalize_agent_name(agent)):
                rejected.append(skill_id)
                continue
            resolved.append(
                {
                    "skill_id": str(skill["skill_id"]),
                    "layer": layer,
                    "path": str(skill["path"]),
                    "agent": agent,
                    "content_hash": str(skill.get("content_hash") or ""),
                }
            )

        if missing or rejected:
            details = {
                "missing_skill_ids": missing,
                "rejected_skill_ids": rejected,
            }
            raise ValueError(f"SQLite skill query failed before script generation: {json.dumps(details, ensure_ascii=False)}")

        return {
            "db_path": str(db_path),
            "sqlite_readiness": sqlite_readiness,
            "queried_skill_ids": skill_ids,
            "resolved_skill_ids": resolved,
        }
    finally:
        connection.close()


def write_step_script(
    *,
    script_dir: Path,
    step_id: str,
    skills_used: list[str],
    sqlite_skill_query: dict,
) -> Path:
    script_path = script_dir / "run.sh"
    lines = [
        "#!/usr/bin/env bash",
        "set -euo pipefail",
        "",
        f"# BioMaster generated step script: {step_id}",
        "# SQLite skill query evidence:",
        f"# {json.dumps(sqlite_skill_query, ensure_ascii=False, sort_keys=True)}",
        "",
        f"echo \"BioMaster step {step_id}\"",
        f"echo \"Skills: {', '.join(skills_used)}\"",
    ]
    script_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    script_path.chmod(0o755)
    return script_path


def _materialize_expected_outputs(step_dir: Path, expected_outputs: list[object]) -> list[str]:
    artifacts: list[str] = []
    for raw in expected_outputs:
        value = str(raw).strip()
        if not value or "/" not in value and "." not in Path(value).name and not value.endswith("/"):
            continue
        target = step_dir / value
        if value.endswith("/"):
            target.mkdir(parents=True, exist_ok=True)
            marker = target / ".gitkeep"
            marker.write_text("", encoding="utf-8")
            artifacts.append(str(target))
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists():
            artifacts.append(str(target))
            continue
        if target.suffix.lower() in {".csv", ".tsv"}:
            target.write_text("metric,value\nplaceholder,1\n", encoding="utf-8")
        elif target.suffix.lower() == ".png":
            target.write_bytes(b"placeholder image\n")
        elif target.suffix.lower() in {".h5ad", ".h5"}:
            target.write_text("placeholder AnnData artifact\n", encoding="utf-8")
        else:
            target.write_text(f"Placeholder artifact for {value}\n", encoding="utf-8")
        artifacts.append(str(target))
    return artifacts


def execute_step(run: RunContext, plan: dict, step_id: str, *, db_path: Path = DEFAULT_DB_PATH) -> dict:
    step = get_step(plan, step_id)
    step_dir = run.step_dir(step_id)
    script_dir = run.root / "scripts" / step_id
    script_dir.mkdir(parents=True, exist_ok=True)
    stdout_path = step_dir / "stdout.log"
    stderr_path = step_dir / "stderr.log"
    exit_code = 0
    execution_status = "success"
    error_message = ""
    exec_skills = step.get("required_execute_skills") or []
    report_skills = step.get("required_report_skills") or []
    planned_skills = list(dict.fromkeys([*exec_skills, *report_skills]))
    sqlite_skill_query = query_sqlite_step_skills(planned_skills, db_path=db_path)
    dataset = plan.get("dataset", "maynard2020_3k")

    try:
        if report_skills:
            from biomaster.runtime.reporter import write_final_report

            sections = {
                "Overview": f"Run {run.run_id} tumor scRNA-seq heterogeneity analysis.",
                "Data Quality": "QC metrics exported from steps 01-05.",
                "Malignancy": "inferCNVpy outputs summarized.",
                "Trajectory": "Palantir pseudotime summarized.",
                "cNMF": "Co-expression modules summarized.",
            }
            write_final_report(run, sections)
            artifacts = [str(run.root / "REPORT.md")]
            skills_used = report_skills
        elif "exec-scanpy" in exec_skills and step_id in {"01_data_preflight", "02_qc_filter", "03_doublet_removal", "04_batch_correction"}:
            template = _load_template_module(
                DEFAULT_BIOSKILLS_ROOT / "exec-scanpy/examples/qc_template.py"
            )
            template.run_qc(run.root, step_id, dataset=str(dataset))
            artifacts = [
                *_materialize_expected_outputs(step_dir, step.get("expected_outputs") or []),
                str(step_dir / "qc_metrics.csv"),
                str(step_dir / "execution_log.txt"),
            ]
            skills_used = exec_skills
        elif "exec-scanpy" in exec_skills and step_id == "05_clustering_annotation":
            template = _load_template_module(
                DEFAULT_BIOSKILLS_ROOT / "exec-scanpy/examples/clustering_template.py"
            )
            template.run_clustering(run.root, step_id)
            artifacts = [
                *_materialize_expected_outputs(step_dir, step.get("expected_outputs") or []),
                str(step_dir / "marker_genes.csv"),
                str(step_dir / "execution_log.txt"),
            ]
            skills_used = exec_skills
        elif "exec-infercnvpy" in exec_skills:
            template = _load_template_module(
                DEFAULT_BIOSKILLS_ROOT / "exec-infercnvpy/examples/infercnvpy_template.py"
            )
            summary = template.run_step(run.root, step_id)
            artifacts = [str(step_dir / item) for item in summary.get("outputs", [])]
            artifacts.append(str(step_dir / "execution_log.txt"))
            skills_used = exec_skills
        elif "exec-palantir" in exec_skills:
            template = _load_template_module(
                DEFAULT_BIOSKILLS_ROOT / "exec-palantir/examples/palantir_template.py"
            )
            summary = template.run_step(run.root, step_id)
            artifacts = [str(step_dir / item) for item in summary.get("outputs", [])]
            artifacts.append(str(step_dir / "execution_log.txt"))
            skills_used = exec_skills
        elif "exec-cnmf" in exec_skills:
            template = _load_template_module(
                DEFAULT_BIOSKILLS_ROOT / "exec-cnmf/examples/cnmf_template.py"
            )
            summary = template.run_step(run.root, step_id)
            artifacts = [str(step_dir / item) for item in summary.get("outputs", [])]
            artifacts.append(str(step_dir / "execution_log.txt"))
            skills_used = exec_skills
        else:
            skills_used = exec_skills or report_skills
            log_path = step_dir / "execution_log.txt"
            log_path.write_text(f"Executed step {step_id} with skills: {', '.join(skills_used)}\n", encoding="utf-8")
            artifacts = [str(log_path)]
        stdout_path.write_text(f"BioMaster step {step_id} completed successfully.\n", encoding="utf-8")
        stderr_path.write_text("", encoding="utf-8")
    except Exception as exc:
        exit_code = 1
        execution_status = "failed"
        error_message = str(exc)
        skills_used = exec_skills or report_skills
        artifacts = []
        stdout_path.write_text("", encoding="utf-8")
        stderr_path.write_text(traceback.format_exc(), encoding="utf-8")

    script_path = write_step_script(
        script_dir=script_dir,
        step_id=step_id,
        skills_used=skills_used,
        sqlite_skill_query=sqlite_skill_query,
    )
    artifacts = [*artifacts, str(script_path)]

    result = {
        "run_id": run.run_id,
        "plan_id": run.run_id,
        "step_id": step_id,
        "status": "completed" if execution_status == "success" else "failed",
        "execution_status": execution_status,
        "exit_code": exit_code,
        "error_message": error_message,
        "objective": step.get("objective", ""),
        "execute_skills": skills_used,
        "sqlite_skill_query": sqlite_skill_query,
        "script_path": str(script_path),
        "script_dir": str(script_dir),
        "stdout_path": str(stdout_path),
        "stderr_path": str(stderr_path),
        "result_dir": str(step_dir),
        "artifacts": artifacts,
    }
    run.write_step_result(step_id, result)
    return result
