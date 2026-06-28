"""Message contracts for agent-to-agent communication."""

from __future__ import annotations

from dataclasses import dataclass, field
from itertools import count
from typing import Any


VALID_PRIORITIES = {"low", "normal", "high", "critical"}
VALID_MESSAGE_TYPES = {
    "observation_report",
    "triage_recommendation",
    "route_proposal",
    "allocation_bid",
    "escalation_request",
    "approval_decision",
    "dispatch_assignment",
    "conflict_notice",
}

_message_counter = count(1)


class ContractError(ValueError):
    """Raised when a message violates the communication contract."""


def reset_message_counter() -> None:
    global _message_counter
    _message_counter = count(1)


def next_message_id() -> str:
    return f"msg-{next(_message_counter):04d}"


@dataclass(frozen=True)
class Message:
    timestamp: str
    sender: str
    receiver: str
    message_type: str
    priority: str
    location: str
    payload: dict[str, Any]
    confidence: float
    requires_human_approval: bool
    correlation_id: str
    message_id: str = field(default_factory=next_message_id)

    def __post_init__(self) -> None:
        if self.priority not in VALID_PRIORITIES:
            raise ContractError(f"invalid priority: {self.priority}")
        if self.message_type not in VALID_MESSAGE_TYPES:
            raise ContractError(f"invalid message_type: {self.message_type}")
        if not 0.0 <= self.confidence <= 1.0:
            raise ContractError("confidence must be between 0.0 and 1.0")
        required_strings = {
            "timestamp": self.timestamp,
            "sender": self.sender,
            "receiver": self.receiver,
            "location": self.location,
            "correlation_id": self.correlation_id,
            "message_id": self.message_id,
        }
        missing = [name for name, value in required_strings.items() if not value]
        if missing:
            raise ContractError(f"missing required fields: {', '.join(missing)}")
