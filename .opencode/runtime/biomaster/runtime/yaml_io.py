from __future__ import annotations

import os
from pathlib import Path
import tempfile
from typing import Callable

import yaml


YamlValidator = Callable[[dict], None]


def _require_mapping(value: object, document_name: str) -> dict:
    if not isinstance(value, dict):
        raise ValueError(f"{document_name} must be a YAML mapping")
    return value


def validate_plan(document: dict) -> None:
    steps = document.get("steps")
    if not isinstance(steps, list):
        raise ValueError("PLAN.yaml must contain a steps list")
    step_ids: list[str] = []
    for index, step in enumerate(steps):
        if not isinstance(step, dict):
            raise ValueError(f"PLAN.yaml steps[{index}] must be a mapping")
        step_id = step.get("step_id")
        if not isinstance(step_id, str) or not step_id.strip():
            raise ValueError(f"PLAN.yaml steps[{index}].step_id must be a non-empty string")
        step_ids.append(step_id)
    if len(step_ids) != len(set(step_ids)):
        raise ValueError("PLAN.yaml step_id values must be unique")


def validate_project_log(document: dict) -> None:
    steps = document.get("steps")
    if not isinstance(steps, list):
        raise ValueError("PROJECT_LOG.yaml must contain a steps list")
    if any(not isinstance(step, dict) for step in steps):
        raise ValueError("PROJECT_LOG.yaml steps must contain only mappings")


def validate_check_report(document: dict) -> None:
    checks = document.get("checks")
    if not isinstance(checks, list):
        raise ValueError("CHECK_REPORT.yaml must contain a checks list")
    status = document.get("overall_status")
    if status not in {"pass", "fail"}:
        raise ValueError("CHECK_REPORT.yaml overall_status must be pass or fail")
    for index, check in enumerate(checks):
        if not isinstance(check, dict):
            raise ValueError(f"CHECK_REPORT.yaml checks[{index}] must be a mapping")
        if check.get("status") not in {"pass", "fail"}:
            raise ValueError(f"CHECK_REPORT.yaml checks[{index}].status must be pass or fail")


def load_yaml_mapping(
    path: Path,
    *,
    document_name: str | None = None,
    validator: YamlValidator | None = None,
) -> dict:
    name = document_name or path.name
    try:
        document = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise ValueError(f"invalid {name}: {exc}") from exc
    mapping = _require_mapping(document, name)
    if validator is not None:
        validator(mapping)
    return mapping


def atomic_write_yaml(
    path: Path,
    document: dict,
    *,
    document_name: str | None = None,
    validator: YamlValidator | None = None,
) -> Path:
    name = document_name or path.name
    mapping = _require_mapping(document, name)
    if validator is not None:
        validator(mapping)
    try:
        serialized = yaml.safe_dump(mapping, sort_keys=False, allow_unicode=True)
        parsed = yaml.safe_load(serialized)
    except yaml.YAMLError as exc:
        raise ValueError(f"{name} cannot be serialized as safe YAML: {exc}") from exc
    parsed_mapping = _require_mapping(parsed, name)
    if validator is not None:
        validator(parsed_mapping)

    path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=path.parent,
            prefix=f".{path.name}.",
            suffix=".tmp",
            delete=False,
        ) as handle:
            temporary_path = Path(handle.name)
            handle.write(serialized)
            handle.flush()
            os.fsync(handle.fileno())
        load_yaml_mapping(temporary_path, document_name=name, validator=validator)
        os.replace(temporary_path, path)
    finally:
        if temporary_path is not None and temporary_path.exists():
            temporary_path.unlink()
    return path
