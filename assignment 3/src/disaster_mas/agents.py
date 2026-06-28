"""Agent implementations with explicit permission boundaries."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .blackboard import Blackboard
from .contracts import Message


def _priority_rank(priority: str) -> int:
    return {"low": 1, "normal": 2, "high": 3, "critical": 4}[priority]


@dataclass
class Agent:
    name: str
    permissions: set[str]

    def ensure_permission(self, permission: str) -> None:
        if permission not in self.permissions:
            raise PermissionError(f"{self.name} cannot perform '{permission}'")


class ScoutAgent(Agent):
    def __init__(self) -> None:
        super().__init__("scout", {"observe"})

    def observe(self, reports: list[dict[str, Any]]) -> list[Message]:
        self.ensure_permission("observe")
        messages = []
        for index, report in enumerate(reports, start=1):
            injured = report["injured_people"]
            stranded = report["stranded_people"]
            priority = "critical" if injured >= 4 or stranded >= 12 else "high" if stranded >= 5 else "normal"
            messages.append(
                Message(
                    timestamp=f"T+{index:02d}",
                    sender=self.name,
                    receiver="command_center",
                    message_type="observation_report",
                    priority=priority,
                    location=report["location"],
                    payload=report,
                    confidence=report["confidence"],
                    requires_human_approval=False,
                    correlation_id=f"incident-{report['location'].lower().replace(' ', '-')}",
                )
            )
        return messages


class MedicalAgent(Agent):
    def __init__(self) -> None:
        super().__init__("medical", {"triage"})

    def triage(self, blackboard: Blackboard) -> list[Message]:
        self.ensure_permission("triage")
        messages = []
        for location, reports in blackboard.reports.items():
            report = max(reports, key=lambda item: item.confidence + item.payload["injured_people"])
            injured = report.payload["injured_people"]
            stranded = report.payload["stranded_people"]
            score = injured * 3 + stranded
            priority = "critical" if score >= 18 else "high" if score >= 8 else "normal"
            rationale = f"Triage score {score}: {injured} injured and {stranded} stranded"
            messages.append(
                Message(
                    timestamp=f"T+1{len(messages)}",
                    sender=self.name,
                    receiver="command_center",
                    message_type="triage_recommendation",
                    priority=priority,
                    location=location,
                    payload={"triage_score": score, "recommended_care": priority, "rationale": rationale},
                    confidence=min(0.95, report.confidence + 0.08),
                    requires_human_approval=priority == "critical" and report.confidence < 0.7,
                    correlation_id=report.correlation_id,
                )
            )
        return messages


class RoutingAgent(Agent):
    def __init__(self) -> None:
        super().__init__("routing", {"route"})

    def plan_routes(self, blackboard: Blackboard) -> list[Message]:
        self.ensure_permission("route")
        messages = []
        for location in blackboard.reports:
            route = blackboard.route_status[location]
            selected = route["alternate"] if route["primary_blocked"] else route["primary"]
            priority = "high" if route["primary_blocked"] else "normal"
            rationale = (
                f"Primary route {route['primary']} blocked; use {route['alternate']}"
                if route["primary_blocked"]
                else f"Primary route {route['primary']} available"
            )
            messages.append(
                Message(
                    timestamp=f"T+2{len(messages)}",
                    sender=self.name,
                    receiver="command_center",
                    message_type="route_proposal",
                    priority=priority,
                    location=location,
                    payload={
                        "selected_route": selected,
                        "primary_blocked": route["primary_blocked"],
                        "travel_minutes": route["travel_minutes"],
                        "rationale": rationale,
                    },
                    confidence=0.86 if not route["primary_blocked"] else 0.76,
                    requires_human_approval=route["primary_blocked"] and route["travel_minutes"] > 20,
                    correlation_id=f"incident-{location.lower().replace(' ', '-')}",
                )
            )
        return messages


class LogisticsAgent(Agent):
    def __init__(self) -> None:
        super().__init__("logistics", {"bid"})

    def bid(self, blackboard: Blackboard) -> list[Message]:
        self.ensure_permission("bid")
        messages = []
        for location, triage in blackboard.triage.items():
            route = blackboard.routes[location]
            priority_bonus = _priority_rank(triage.priority) * 15
            triage_bonus = triage.payload["triage_score"]
            delay_penalty = route.payload["travel_minutes"]
            blocked_penalty = 6 if route.payload["primary_blocked"] else 0
            score = priority_bonus + triage_bonus - delay_penalty - blocked_penalty
            resources = {
                "rescue_teams": 1,
                "ambulances": 1 if triage.priority in {"high", "critical"} else 0,
                "boats": 1 if route.payload["primary_blocked"] else 0,
                "supply_kits": 1,
            }
            messages.append(
                Message(
                    timestamp=f"T+3{len(messages)}",
                    sender=self.name,
                    receiver="command_center",
                    message_type="allocation_bid",
                    priority=triage.priority,
                    location=location,
                    payload={
                        "score": score,
                        "requested_resources": resources,
                        "rationale": (
                            f"Bid score {score} combines {triage.priority} triage, triage score {triage_bonus}, "
                            f"{route.payload['travel_minutes']} minute route, and route risk"
                        ),
                    },
                    confidence=min(triage.confidence, route.confidence),
                    requires_human_approval=triage.priority == "critical" and score < 20,
                    correlation_id=triage.correlation_id,
                )
            )
        return messages


class HumanApproverAgent(Agent):
    def __init__(self) -> None:
        super().__init__("human_approver", {"approve"})

    def review(self, escalation: Message, timestamp: str = "T+41") -> Message:
        self.ensure_permission("approve")
        decision = "approved_with_conditions"
        return Message(
            timestamp=timestamp,
            sender=self.name,
            receiver="command_center",
            message_type="approval_decision",
            priority=escalation.priority,
            location=escalation.location,
            payload={
                "decision": decision,
                "conditions": "Dispatch only after confirming route status by radio check.",
                "rationale": "Life-safety benefit outweighs delay risk with explicit route confirmation.",
            },
            confidence=0.9,
            requires_human_approval=False,
            correlation_id=escalation.correlation_id,
        )


class CommandCenterAgent(Agent):
    def __init__(self, human: HumanApproverAgent) -> None:
        super().__init__("command_center", {"coordinate", "assign", "escalate"})
        self.human = human

    def ingest_observations(self, blackboard: Blackboard, messages: list[Message]) -> list[str]:
        self.ensure_permission("coordinate")
        transcript = []
        for message in messages:
            blackboard.add_report(message)
            transcript.append(self._line(message, "recorded observation"))
        self._detect_conflicts(blackboard)
        return transcript

    def ingest_recommendations(self, blackboard: Blackboard, messages: list[Message]) -> list[str]:
        self.ensure_permission("coordinate")
        transcript = []
        for message in messages:
            if message.message_type == "triage_recommendation":
                blackboard.add_triage(message)
            elif message.message_type == "route_proposal":
                blackboard.add_route(message)
            elif message.message_type == "allocation_bid":
                blackboard.add_bid(message)
            transcript.append(self._line(message, message.payload["rationale"]))
        return transcript

    def allocate(self, blackboard: Blackboard) -> list[str]:
        self.ensure_permission("assign")
        transcript = []
        remaining = dict(blackboard.resources)
        ranked_bids = sorted(blackboard.bids.values(), key=lambda bid: bid.payload["score"], reverse=True)
        clock = 40
        for bid in ranked_bids:
            route = blackboard.routes[bid.location]
            requested = bid.payload["requested_resources"]
            constrained_request = {key: value for key, value in requested.items() if value > 0}
            shortage = [key for key, value in constrained_request.items() if remaining.get(key, 0) < value]
            needs_approval = bid.requires_human_approval or route.requires_human_approval or bool(shortage)
            approval_message = None
            if needs_approval:
                escalation = self._escalate(bid, shortage, f"T+{clock}")
                clock += 1
                blackboard.record(
                    escalation.timestamp,
                    self.name,
                    "human_escalation",
                    escalation.payload["rationale"],
                    escalation.message_id,
                )
                transcript.append(self._line(escalation, escalation.payload["rationale"]))
                approval_message = self.human.review(escalation, f"T+{clock}")
                clock += 1
                blackboard.approve(approval_message)
                transcript.append(self._line(approval_message, approval_message.payload["decision"]))
            allocated = {}
            for resource, amount in constrained_request.items():
                available = remaining.get(resource, 0)
                take = min(available, amount)
                if take:
                    allocated[resource] = take
                    remaining[resource] = available - take
            assignment = {
                "location": bid.location,
                "priority": bid.priority,
                "route": route.payload["selected_route"],
                "allocated_resources": allocated,
                "status": "partial" if shortage else "assigned",
                "approval": approval_message.payload["decision"] if approval_message else "not_required",
                "rationale": f"Selected bid score {bid.payload['score']} using route {route.payload['selected_route']}",
            }
            assignment_message = Message(
                timestamp=f"T+{clock}",
                sender=self.name,
                receiver="blackboard",
                message_type="dispatch_assignment",
                priority=bid.priority,
                location=bid.location,
                payload=assignment,
                confidence=bid.confidence,
                requires_human_approval=False,
                correlation_id=bid.correlation_id,
            )
            clock += 1
            blackboard.assign(assignment_message.timestamp, bid.location, assignment, assignment_message.message_id)
            transcript.append(self._line(assignment_message, assignment["rationale"]))
        blackboard.resources = remaining
        return transcript

    def _detect_conflicts(self, blackboard: Blackboard) -> None:
        for location, reports in blackboard.reports.items():
            if len(reports) < 2:
                continue
            stranded_counts = {report.payload["stranded_people"] for report in reports}
            water_levels = {report.payload["water_level"] for report in reports}
            if len(stranded_counts) > 1 or len(water_levels) > 1:
                blackboard.add_conflict(
                    "T+09",
                    location,
                    "Conflicting field reports require command-center reconciliation",
                    reports[-1].message_id,
                )

    def _escalate(self, bid: Message, shortage: list[str], timestamp: str) -> Message:
        self.ensure_permission("escalate")
        reason = "High-risk or scarce-resource allocation needs human approval"
        if shortage:
            reason = f"Resource shortage for {', '.join(shortage)} requires human approval"
        return Message(
            timestamp=timestamp,
            sender=self.name,
            receiver="human_approver",
            message_type="escalation_request",
            priority=bid.priority,
            location=bid.location,
            payload={"rationale": reason, "bid": bid.payload},
            confidence=bid.confidence,
            requires_human_approval=True,
            correlation_id=bid.correlation_id,
        )

    @staticmethod
    def _line(message: Message, summary: str) -> str:
        return (
            f"{message.timestamp} {message.message_id} "
            f"{message.sender}->{message.receiver} "
            f"{message.message_type.upper()} [{message.priority}] "
            f"{message.location}: {summary}"
        )
