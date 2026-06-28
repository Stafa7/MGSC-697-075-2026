"""Command-line interface for the disaster MAS simulation."""

from __future__ import annotations

import argparse
import json

from .simulation import run_simulation


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the disaster response MAS simulation.")
    parser.add_argument("--scenario", default="flood", choices=["flood", "aftershock", "conflicting_reports"])
    parser.add_argument("--seed", default=42, type=int)
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    result = run_simulation(scenario=args.scenario, seed=args.seed)
    if args.json:
        print(json.dumps(result.__dict__, indent=2, sort_keys=True))
        return

    print("\n".join(result.transcript))
    print("\nFINAL ACTION PLAN")
    for location, assignment in result.action_plan.items():
        print(
            f"- {location}: {assignment['status']} | {assignment['priority']} | "
            f"route={assignment['route']} | resources={assignment['allocated_resources']} | "
            f"approval={assignment['approval']}"
        )
    if result.conflicts:
        print("\nCONFLICTS")
        for conflict in result.conflicts:
            print(f"- {conflict}")
    print("\nAUDIT LOG")
    for event in result.audit_log:
        print(
            f"- {event['timestamp']} {event['actor']} {event['action']} "
            f"ref={event['reference']} :: {event['rationale']}"
        )


if __name__ == "__main__":
    main()
