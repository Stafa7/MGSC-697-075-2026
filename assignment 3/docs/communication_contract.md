# Communication Contract

## Message Schema

| Field | Type | Required | Purpose |
| --- | --- | --- | --- |
| `message_id` | string | yes | Unique audit and replay identifier |
| `timestamp` | string | yes | Deterministic simulation timestamp |
| `sender` | string | yes | Producing agent |
| `receiver` | string | yes | Target agent or shared state |
| `message_type` | string | yes | Typed intent |
| `priority` | string | yes | `low`, `normal`, `high`, or `critical` |
| `location` | string | yes | Incident zone |
| `payload` | object | yes | Structured message content |
| `confidence` | number | yes | Confidence from 0.0 to 1.0 |
| `requires_human_approval` | boolean | yes | Escalation flag |
| `correlation_id` | string | yes | Incident thread identifier |

## Message Types

- `observation_report`
- `triage_recommendation`
- `route_proposal`
- `allocation_bid`
- `escalation_request`
- `approval_decision`
- `dispatch_assignment`
- `conflict_notice`

## Routing Rules

- Scout sends field observations to command center.
- Command center writes validated observations to blackboard state.
- Medical reads observations and returns triage recommendations.
- Routing reads incident zones and route status, then returns route proposals.
- Logistics reads triage and route proposals, then returns allocation bids.
- Command center escalates high-risk, low-confidence, or scarce-resource decisions to the human approver.
- Dispatch assignments are written only by command center after required approvals.

## Shared State

The blackboard stores:

- Incident reports by location.
- Medical triage by location.
- Route proposals by location.
- Allocation bids by location.
- Dispatch assignments by location.
- Remaining resources.
- Conflict notices.
- Human approvals.
- Immutable audit events.

## Escalation Triggers

- Critical triage with low confidence.
- Blocked primary route with long alternate travel time.
- Allocation bid that requests unavailable scarce resources.
- Any decision where local agent objectives conflict with global life-safety or auditability constraints.
