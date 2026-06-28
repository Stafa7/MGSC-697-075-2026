# Evaluation, Safety, And Governance

## Evaluation Plan

Agent-level metrics:

- Message schema validity.
- Permission-boundary compliance.
- Confidence calibration against scenario truth.
- Recommendation completeness.

Interaction-level metrics:

- Conflict detection rate.
- Escalation correctness.
- Duplicate-dispatch prevention.
- Time from observation to assignment in simulation steps.

System-level metrics:

- Critical zones assigned first.
- Unmet critical needs.
- Route safety.
- Resource utilization.
- Number of rollback checkpoints before dispatch.

Human-level metrics:

- Approval burden.
- Clarity of escalation packets.
- Audit-log usefulness.
- Ability to reconstruct why a decision was made.

## Observability

The prototype emits:

- Console transcript of every inter-agent message.
- Final action plan.
- Conflict list.
- Remaining resource inventory.
- Audit log with timestamp, actor, action, rationale, and reference message.

The seed and scenario name form the replay contract. A grader can rerun the same scenario and inspect the same message order and decision rationale.

## Safety Controls

- Role permissions prevent agents from acting outside their boundary.
- Command center is the only agent that can assign dispatches.
- High-risk and scarce-resource decisions require human approval.
- Blocked-route cases create rollback checkpoints before assignment.
- Conflicting field reports are recorded for command-center reconciliation.
- Every dispatch assignment records a rationale and reference message.

## Failure And Abuse Cases

- Spoofed reports: mitigated through sender identity and confidence fields.
- Stale route data: mitigated through route-agent proposals and rollback checkpoints.
- Resource hoarding: mitigated through command-center allocation and global objective scoring.
- Priority inflation: mitigated through typed priorities and triage score rationale.
- Duplicate dispatches: mitigated through centralized assignment state.
- Over-escalation: monitored through approval burden and escalation correctness.

## Rollback

Before dispatching to a zone with a blocked primary route, the routing agent records a rollback checkpoint. The command center can pause or revise an assignment if route confirmation fails. In a production system, rollback would call external dispatch and notification tools through controlled MCP-style interfaces.

## Human In The Loop

The human approver reviews decisions that combine high life-safety stakes, low confidence, blocked routes, or scarce resources. The approval response includes explicit conditions so the system does not treat human approval as a blanket waiver.

## MARL Bridge

Multi-agent reinforcement learning is not appropriate for the live prototype. Disaster-response rewards are sparse, delayed, and ethically sensitive, and the learned policy would be difficult to explain during urgent incidents.

MARL could be useful later in an offline training environment to learn allocation heuristics across many simulated incidents. Any MARL-derived policy would need offline validation, stress testing, human approval gates, and conservative rollout before influencing real decisions.
