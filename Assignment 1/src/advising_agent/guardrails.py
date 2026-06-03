from __future__ import annotations

from advising_agent.models import AdvisingRecommendation

try:
    from agents import GuardrailFunctionOutput, output_guardrail
except ModuleNotFoundError:
    GuardrailFunctionOutput = None

    def output_guardrail(func=None, **_kwargs):
        if func is None:
            return lambda wrapped: wrapped
        return func


def missing_prerequisite_violations(output: AdvisingRecommendation) -> list[str]:
    violations = []
    for course in output.recommended_courses:
        if course.recommendation in {"recommend", "consider"} and course.missing_prerequisites:
            violations.append(
                f"{course.course_code} was {course.recommendation} despite missing "
                f"{', '.join(course.missing_prerequisites)}."
            )
    return violations


def validate_missing_prerequisite_blocker(output: AdvisingRecommendation) -> tuple[bool, list[str]]:
    violations = missing_prerequisite_violations(output)
    return (not violations, violations)


@output_guardrail(name="MissingPrerequisiteBlocker")
async def missing_prerequisite_blocker(_context, _agent, output: AdvisingRecommendation):
    """Block final outputs that recommend courses with unmet prerequisites."""
    violations = missing_prerequisite_violations(output)
    if GuardrailFunctionOutput is None:
        return {"tripwire_triggered": bool(violations), "output_info": {"violations": violations}}
    return GuardrailFunctionOutput(
        tripwire_triggered=bool(violations),
        output_info={"violations": violations},
    )

