"""Simulation orchestration."""

from __future__ import annotations

from dataclasses import dataclass
from random import Random
from typing import Any

from .agents import CommandCenterAgent, HumanApproverAgent, LogisticsAgent, MedicalAgent, RoutingAgent, ScoutAgent
from .blackboard import Blackboard
from .contracts import reset_message_counter
from .scenarios import get_scenario


@dataclass
class SimulationResult:
    scenario: str
    seed: int
    transcript: list[str]
    action_plan: dict[str, dict[str, Any]]
    audit_log: list[dict[str, str]]
    conflicts: list[str]
    remaining_resources: dict[str, int]


def run_simulation(scenario: str = "flood", seed: int = 42) -> SimulationResult:
    reset_message_counter()
    Random(seed)  # Reserved for future stochastic fixtures; seed remains part of replay contract.
    fixture = get_scenario(scenario)
    blackboard = Blackboard(
        scenario_name=scenario,
        route_status=fixture["route_status"],
        resources=fixture["resources"],
    )

    scout = ScoutAgent()
    medical = MedicalAgent()
    routing = RoutingAgent()
    logistics = LogisticsAgent()
    command = CommandCenterAgent(HumanApproverAgent())

    transcript = [f"SCENARIO {scenario} seed={seed}"]

    observations = scout.observe(fixture["reports"])
    transcript.extend(command.ingest_observations(blackboard, observations))

    triage_messages = medical.triage(blackboard)
    transcript.extend(command.ingest_recommendations(blackboard, triage_messages))

    route_messages = routing.plan_routes(blackboard)
    transcript.extend(command.ingest_recommendations(blackboard, route_messages))

    bid_messages = logistics.bid(blackboard)
    transcript.extend(command.ingest_recommendations(blackboard, bid_messages))

    transcript.extend(command.allocate(blackboard))

    audit_log = [
        {
            "timestamp": event.timestamp,
            "actor": event.actor,
            "action": event.action,
            "rationale": event.rationale,
            "reference": event.reference,
        }
        for event in blackboard.audit_log
    ]

    return SimulationResult(
        scenario=scenario,
        seed=seed,
        transcript=transcript,
        action_plan=blackboard.assignments,
        audit_log=audit_log,
        conflicts=blackboard.conflicts,
        remaining_resources=blackboard.resources,
    )
