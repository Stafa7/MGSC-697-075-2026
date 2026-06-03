from __future__ import annotations

from typing import Annotated

from pydantic import Field

from advising_agent.fixtures import course_lookup, load_courses, load_prerequisites, normalize_course_code
from advising_agent.models import (
    CheckPrerequisitesOutput,
    Difficulty,
    FlagPolicyRiskOutput,
    PolicyRisk,
    SearchCoursesOutput,
    StudentProfile,
)

try:
    from agents import function_tool
except ModuleNotFoundError:

    def function_tool(func=None, **_kwargs):
        if func is None:
            return lambda wrapped: wrapped
        return func


DIFFICULTY_ORDER = {"intro": 0, "intermediate": 1, "advanced": 2}


def search_courses(
    query: Annotated[str | None, Field(description="Keyword, course code, or phrase to search for.")] = None,
    area: Annotated[str | None, Field(description="Optional course area filter.")] = None,
    max_difficulty: Annotated[Difficulty | None, Field(description="Maximum difficulty to include.")] = None,
) -> SearchCoursesOutput:
    """Search the fake course catalog. This never searches real McGill data."""
    courses = load_courses()
    normalized_query = query.lower().strip() if query else None
    normalized_area = area.lower().strip() if area else None
    max_rank = DIFFICULTY_ORDER[max_difficulty] if max_difficulty else None

    matches = []
    for course in courses:
        searchable = " ".join(
            [course.code, course.name, course.area, course.description, *course.keywords]
        ).lower()
        if normalized_query and normalized_query not in searchable:
            continue
        if normalized_area and normalized_area not in course.area.lower():
            continue
        if max_rank is not None and DIFFICULTY_ORDER[course.difficulty] > max_rank:
            continue
        matches.append(course)
    return SearchCoursesOutput(matches=matches)


def check_prerequisites(
    course_code: Annotated[str, Field(description="Course code such as MGSC 605.")],
    completed_courses: Annotated[list[str], Field(description="Course codes already completed.")],
    current_courses: Annotated[list[str], Field(description="Course codes currently in progress.")],
) -> CheckPrerequisitesOutput:
    """Check prerequisite completion for one fake catalog course."""
    normalized = normalize_course_code(course_code)
    courses = course_lookup()
    prerequisites = load_prerequisites()
    if normalized not in courses:
        return CheckPrerequisitesOutput(
            course_code=normalized,
            prerequisites_required=[],
            prerequisites_met=False,
            missing_prerequisites=[],
            unknown_course=True,
        )

    required = prerequisites.get(normalized, [])
    completed = {normalize_course_code(code) for code in completed_courses}
    current = {normalize_course_code(code) for code in current_courses}
    satisfied_completed = [code for code in required if code in completed]
    satisfied_current = [code for code in required if code in current and code not in completed]
    satisfied = set(satisfied_completed) | set(satisfied_current)
    missing = [code for code in required if code not in satisfied]

    return CheckPrerequisitesOutput(
        course_code=normalized,
        prerequisites_required=required,
        prerequisites_met=not missing,
        missing_prerequisites=missing,
        satisfied_by_completed=satisfied_completed,
        satisfied_by_current=satisfied_current,
        unknown_course=False,
    )


def flag_policy_risk(
    proposed_course_codes: Annotated[list[str], Field(description="Course codes being considered.")],
    student_profile: Annotated[StudentProfile, Field(description="The active fake student profile.")],
) -> FlagPolicyRiskOutput:
    """Flag blocking and advisor-approval risks for a proposed fake course plan."""
    courses = course_lookup()
    normalized_codes = [normalize_course_code(code) for code in proposed_course_codes]
    risks: list[PolicyRisk] = []

    known_codes = [code for code in normalized_codes if code in courses]
    unknown_codes = [code for code in normalized_codes if code not in courses]
    for code in unknown_codes:
        risks.append(
            PolicyRisk(
                rule_id="unknown_course",
                name="Unknown course code",
                severity="blocking",
                message=f"{code} is not in the fake fixture catalog.",
                course_codes=[code],
            )
        )

    for code in known_codes:
        prereq = check_prerequisites(
            code,
            student_profile.completed_courses,
            student_profile.current_courses,
        )
        if not prereq.prerequisites_met:
            risks.append(
                PolicyRisk(
                    rule_id="missing_prerequisites_block",
                    name="MissingPrerequisiteBlocker",
                    severity="blocking",
                    message=f"{code} is missing prerequisites: {', '.join(prereq.missing_prerequisites)}.",
                    course_codes=[code],
                )
            )

    total_credits = sum(courses[code].credits for code in known_codes)
    if total_credits > student_profile.max_credits_next_term:
        risks.append(
            PolicyRisk(
                rule_id="max_credits",
                name="Maximum next-term credits",
                severity="approval_required",
                message=(
                    f"Proposed plan has {total_credits} credits, above the "
                    f"{student_profile.max_credits_next_term}-credit limit."
                ),
                course_codes=known_codes,
            )
        )

    if "MGSC 610" in known_codes:
        risks.append(
            PolicyRisk(
                rule_id="capstone_approval",
                name="AdvisorApprovalRequired",
                severity="approval_required",
                message="MGSC 610 Analytics Capstone Project requires advisor approval.",
                course_codes=["MGSC 610"],
            )
        )

    blocking = [risk for risk in risks if risk.severity == "blocking"]
    approval = any(risk.severity == "approval_required" for risk in risks)
    return FlagPolicyRiskOutput(
        risks=risks,
        advisor_approval_required=approval,
        blocking_violation_found=bool(blocking),
        blocking_reason="; ".join(risk.message for risk in blocking) if blocking else None,
    )


search_courses_tool = function_tool(search_courses)
check_prerequisites_tool = function_tool(check_prerequisites)
flag_policy_risk_tool = function_tool(flag_policy_risk)
