from __future__ import annotations

from pathlib import Path
from typing import Any
import json

from biomaster.a2a.message import A2AMessage
from biomaster.a2a.protocol import VALID_MESSAGE_TYPES, VALID_TRANSITIONS


REQUIRED_FIELDS = {"message_type", "from", "to", "run_id", "phase", "payload"}


def validate_message_dict(data: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    missing = REQUIRED_FIELDS - set(data)
    if missing:
        errors.append(f"missing fields: {', '.join(sorted(missing))}")
    message_type = data.get("message_type")
    if message_type and message_type not in VALID_MESSAGE_TYPES:
        errors.append(f"invalid message_type: {message_type}")
    if not data.get("run_id"):
        errors.append("run_id must not be empty")
    return errors


def validate_message(message: A2AMessage) -> list[str]:
    return validate_message_dict(message.to_dict())


def validate_transition(previous_type: str | None, next_type: str) -> list[str]:
    if previous_type is None:
        if next_type != "intake_request":
            return [f"workflow must start with intake_request, not {next_type}"]
        return []
    allowed = VALID_TRANSITIONS.get(previous_type, set())
    if next_type not in allowed:
        return [f"invalid transition: {previous_type} -> {next_type}"]
    return []


def load_message(path: Path) -> A2AMessage:
    data = json.loads(path.read_text(encoding="utf-8"))
    errors = validate_message_dict(data)
    if errors:
        raise ValueError("; ".join(errors))
    return A2AMessage.from_dict(data)
