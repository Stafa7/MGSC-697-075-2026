"""Shared state and audit log for the simulation."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .contracts import Message


@dataclass(frozen=True)
class AuditEvent:
    timestamp: str
    actor: str
    action: str
    rationale: str
    reference: str


@dataclass
class Blackboard:
    scenario_name: str
    route_status: dict[str, dict[str, Any]]
    resources: dict[str, int]
    reports: dict[str, list[Message]] = field(default_factory=dict)
    triage: dict[str, Message] = field(default_factory=dict)
    routes: dict[str, Message] = field(default_factory=dict)
    bids: dict[str, Message] = field(default_factory=dict)
    assignments: dict[str, dict[str, Any]] = field(default_factory=dict)
    approvals: list[Message] = field(default_factory=list)
    conflicts: list[str] = field(default_factory=list)
    audit_log: list[AuditEvent] = field(default_factory=list)

    def record(self, timestamp: str, actor: str, action: str, rationale: str, reference: str) -> None:
        self.audit_log.append(AuditEvent(timestamp, actor, action, rationale, reference))

    def add_report(self, message: Message) -> None:
        self.reports.setdefault(message.location, []).append(message)
        self.record(
            message.timestamp,
            message.sender,
            "report_added",
            f"Recorded observation for {message.location}",
            message.message_id,
        )

    def add_triage(self, message: Message) -> None:
        self.triage[message.location] = message
        self.record(
            message.timestamp,
            message.sender,
            "triage_added",
            message.payload["rationale"],
            message.message_id,
        )

    def add_route(self, message: Message) -> None:
        self.routes[message.location] = message
        if message.payload.get("primary_blocked"):
            self.record(
                message.timestamp,
                message.sender,
                "rollback_checkpoint",
                "Primary route blocked; dispatch must use safe alternate",
                message.message_id,
            )
        self.record(
            message.timestamp,
            message.sender,
            "route_added",
            message.payload["rationale"],
            message.message_id,
        )

    def add_bid(self, message: Message) -> None:
        self.bids[message.location] = message
        self.record(
            message.timestamp,
            message.sender,
            "allocation_bid_added",
            message.payload["rationale"],
            message.message_id,
        )

    def add_conflict(self, timestamp: str, location: str, rationale: str, reference: str) -> None:
        conflict = f"{location}: {rationale}"
        self.conflicts.append(conflict)
        self.record(timestamp, "command_center", "conflict_detected", conflict, reference)

    def approve(self, message: Message) -> None:
        self.approvals.append(message)
        self.record(
            message.timestamp,
            message.sender,
            "approval_recorded",
            message.payload["decision"],
            message.message_id,
        )

    def assign(self, timestamp: str, location: str, assignment: dict[str, Any], reference: str) -> None:
        self.assignments[location] = assignment
        self.record(
            timestamp,
            "command_center",
            "dispatch_assignment",
            assignment["rationale"],
            reference,
        )
