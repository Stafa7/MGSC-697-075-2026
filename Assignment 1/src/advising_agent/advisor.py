from __future__ import annotations

import re

from advising_agent.fixtures import course_lookup, load_student_profile, normalize_course_code
from advising_agent.models import AdvisingRecommendation, Course, CourseRecommendation, StudentProfile
from advising_agent.tools import check_prerequisites, flag_policy_risk, search_courses


SCOPE_NOTE = (
    "This recommendation uses a small fake fixture catalog for an AI agents assignment. "
    "It is not official McGill advising."
)


def extract_course_codes(text: str) -> list[str]:
    matches = re.findall(r"\bMGSC[-\s]?\d{3}\b", text.upper())
    return [normalize_course_code(match) for match in matches]


def requested_course_count(text: str, default: int = 3) -> int:
    lower = text.lower()
    word_numbers = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5}
    for word, value in word_numbers.items():
        if re.search(rf"\b{word}\b", lower):
            return value
    match = re.search(r"\b([1-9])\s*(?:course|courses)\b", lower)
    return int(match.group(1)) if match else default


def _course_priority(course: Course, request: str, student: StudentProfile) -> tuple[int, int, str]:
    lower = request.lower()
    interest_text = " ".join(student.interests).lower()
    combined = f"{lower} {interest_text}"
    score = 0
    if course.code in student.completed_courses:
        score -= 100
    if course.area.lower() in combined:
        score += 20
    for keyword in course.keywords:
        if keyword.lower() in combined:
            score += 10
    if "ai engineering" in combined and course.code == "MGSC 605":
        score += 20
    if "ai engineering" in combined and course.code == "MGSC 609":
        score += 15
    if "ai" in combined and ("ai" in course.name.lower() or "machine learning" in course.area.lower()):
        score += 15
    if "data engineering" in combined and course.area == "data engineering":
        score += 15
    if "business intelligence" in combined and course.area == "visualization":
        score += 12
    difficulty_rank = {"intro": 0, "intermediate": 1, "advanced": 2}[course.difficulty]
    return (-score, difficulty_rank, course.code)


def select_candidate_courses(user_request: str, student: StudentProfile) -> list[str]:
    explicit_codes = extract_course_codes(user_request)
    if explicit_codes:
        return explicit_codes

    count = requested_course_count(user_request)
    courses = search_courses(query=None).matches
    sorted_courses = sorted(courses, key=lambda course: _course_priority(course, user_request, student))

    chosen: list[str] = []
    for course in sorted_courses:
        if course.code in student.completed_courses:
            continue
        if course.code == "MGSC 610" and "capstone" not in user_request.lower():
            continue
        prereq = check_prerequisites(course.code, student.completed_courses, student.current_courses)
        if not prereq.prerequisites_met:
            continue
        if len(chosen) >= count:
            break
        chosen.append(course.code)

    return chosen


def _recommendation_for_course(code: str, student: StudentProfile) -> CourseRecommendation:
    courses = course_lookup()
    if code not in courses:
        return CourseRecommendation(
            course_code=code,
            course_name="Unknown fixture course",
            credits=0,
            recommendation="do_not_take",
            reason=f"{code} is not in the fake fixture catalog, so the agent cannot evaluate it.",
            prerequisite_status="missing",
            missing_prerequisites=[],
            policy_risks=["Unknown course code"],
        )

    course = courses[code]
    prereq = check_prerequisites(code, student.completed_courses, student.current_courses)
    if not prereq.prerequisites_required:
        prereq_status = "not_required"
    elif prereq.prerequisites_met:
        prereq_status = "met"
    else:
        prereq_status = "missing"

    if prereq.missing_prerequisites:
        decision = "do_not_take"
        reason = (
            f"Do not take {course.code} yet because prerequisites are missing: "
            f"{', '.join(prereq.missing_prerequisites)}."
        )
    elif course.code == "MGSC 610":
        decision = "consider"
        reason = "This can be considered only with advisor approval because it is the capstone."
    else:
        decision = "recommend"
        reason = f"{course.name} fits the request and the fixture prerequisite check is satisfied."

    return CourseRecommendation(
        course_code=course.code,
        course_name=course.name,
        credits=course.credits,
        recommendation=decision,
        reason=reason,
        prerequisite_status=prereq_status,
        missing_prerequisites=prereq.missing_prerequisites,
        policy_risks=[],
    )


def advise_offline(user_request: str, student: StudentProfile | None = None) -> AdvisingRecommendation:
    """Deterministic fixture-backed advising path used for tests and offline evals."""
    active_student = student or load_student_profile()
    proposed_codes = select_candidate_courses(user_request, active_student)
    recommendations = [_recommendation_for_course(code, active_student) for code in proposed_codes]

    policy = flag_policy_risk(proposed_codes, active_student)
    risk_by_course: dict[str, list[str]] = {}
    for risk in policy.risks:
        for code in risk.course_codes:
            risk_by_course.setdefault(code, []).append(risk.name)

    recommendations = [
        recommendation.model_copy(
            update={"policy_risks": risk_by_course.get(recommendation.course_code, [])}
        )
        for recommendation in recommendations
    ]

    usable_recommendations = [item for item in recommendations if item.recommendation == "recommend"]
    total_credits = sum(item.credits for item in usable_recommendations)
    approval_reasons = [risk.message for risk in policy.risks if risk.severity == "approval_required"]

    next_steps = []
    if policy.blocking_violation_found:
        next_steps.append("Do not enroll in blocked courses until the listed issue is resolved.")
    if approval_reasons:
        next_steps.append("Contact a human advisor for approval before using the flagged plan.")
    if not next_steps:
        next_steps.append("Review the recommendation against the fake fixture assumptions before finalizing.")

    return AdvisingRecommendation(
        student_summary=(
            f"{active_student.student_id} is in {active_student.program}, has completed "
            f"{', '.join(active_student.completed_courses)}, and is currently taking "
            f"{', '.join(active_student.current_courses) or 'no fixture courses'}."
        ),
        recommended_courses=recommendations,
        total_recommended_credits=total_credits,
        advisor_approval_required=policy.advisor_approval_required,
        approval_reason="; ".join(approval_reasons) if approval_reasons else None,
        blocked=policy.blocking_violation_found,
        blocking_reason=policy.blocking_reason,
        policy_risks=policy.risks,
        next_steps=next_steps,
        confidence="high" if proposed_codes else "low",
        fixture_scope_note=SCOPE_NOTE,
    )
