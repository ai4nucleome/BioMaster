from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
import uuid


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def new_message_id() -> str:
    return f"msg-{uuid.uuid4().hex[:12]}"


@dataclass
class A2AMessage:
    message_type: str
    from_agent: str
    to_agent: str
    run_id: str
    phase: str
    payload: dict[str, Any] = field(default_factory=dict)
    required_outputs: list[str] = field(default_factory=list)
    message_id: str = field(default_factory=new_message_id)
    created_at: str = field(default_factory=utc_now)

    def to_dict(self) -> dict[str, Any]:
        return {
            "message_id": self.message_id,
            "message_type": self.message_type,
            "from": self.from_agent,
            "to": self.to_agent,
            "run_id": self.run_id,
            "phase": self.phase,
            "payload": self.payload,
            "required_outputs": self.required_outputs,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "A2AMessage":
        return cls(
            message_type=str(data["message_type"]),
            from_agent=str(data["from"]),
            to_agent=str(data["to"]),
            run_id=str(data["run_id"]),
            phase=str(data["phase"]),
            payload=dict(data.get("payload") or {}),
            required_outputs=list(data.get("required_outputs") or []),
            message_id=str(data.get("message_id") or new_message_id()),
            created_at=str(data.get("created_at") or utc_now()),
        )
