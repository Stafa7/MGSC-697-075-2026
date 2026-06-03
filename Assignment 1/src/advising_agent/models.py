from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


Difficulty = Literal["intro", "intermediate", "advanced"]
RecommendationDecision = Literal["recommend", "consider", "do_not_take"]
PrerequisiteStatus = Literal["met", "missing", "not_required"]
PolicySeverity = Literal["info", "warning", "approval_required", "blocking"]
Confidence = Literal["low", "medium", "high"]


class Course(BaseModel):
    code: str = Field(pattern=r"^MGSC \d{3}$")
    name: str
    credits: int = Field(ge=1, le=6)
    area: str
    difficulty: Difficulty
    description: str
    keywords: list[str] = Field(default_factory=list)


class StudentProfile(BaseModel):
    student_id: str
    program: str
    completed_courses: list[str] = Field(default_factory=list)
    current_courses: list[str] = Field(default_factory=list)
    interests: list[str] = Field(default_factory=list)
    max_credits_next_term: int = Field(default=9, ge=0)
    academic_standing: str = "good"
    advisor_approval_flags: list[str] = Field(default_factory=list)


class PrerequisiteResult(BaseModel):
    course_code: str
    prerequisites_required: list[str] = Field(default_factory=list)
    prerequisites_met: bool
    missing_prerequisites: list[str] = Field(default_factory=list)
    satisfied_by_completed: list[str] = Field(default_factory=list)
    satisfied_by_current: list[str] = Field(default_factory=list)
    unknown_course: bool = False


class PolicyRisk(BaseModel):
    rule_id: str
    name: str
    severity: PolicySeverity
    message: str
    course_codes: list[str] = Field(default_factory=list)


class CourseRecommendation(BaseModel):
    course_code: str
    course_name: str
    credits: int = Field(ge=0)
    recommendation: RecommendationDecision
    reason: str
    prerequisite_status: PrerequisiteStatus
    missing_prerequisites: list[str] = Field(default_factory=list)
    policy_risks: list[str] = Field(default_factory=list)


class AdvisingRecommendation(BaseModel):
    student_summary: str
    recommended_courses: list[CourseRecommendation] = Field(default_factory=list)
    total_recommended_credits: int = Field(ge=0)
    advisor_approval_required: bool
    approval_reason: str | None = None
    blocked: bool
    blocking_reason: str | None = None
    policy_risks: list[PolicyRisk] = Field(default_factory=list)
    next_steps: list[str] = Field(default_factory=list)
    confidence: Confidence
    fixture_scope_note: str


class SearchCoursesOutput(BaseModel):
    matches: list[Course] = Field(default_factory=list)


class CheckPrerequisitesOutput(PrerequisiteResult):
    pass


class FlagPolicyRiskOutput(BaseModel):
    risks: list[PolicyRisk] = Field(default_factory=list)
    advisor_approval_required: bool
    blocking_violation_found: bool
    blocking_reason: str | None = None


class EvalCase(BaseModel):
    id: str
    name: str
    user_request: str
    edge_or_failure: bool = False
    expected_blocked: bool
    expected_advisor_approval_required: bool
    expected_course_codes: list[str] = Field(default_factory=list)
    forbidden_recommended_course_codes: list[str] = Field(default_factory=list)
    required_substrings: list[str] = Field(default_factory=list)


class EvalCaseResult(BaseModel):
    id: str
    name: str
    passed: bool
    failures: list[str] = Field(default_factory=list)
    output: AdvisingRecommendation


class EvalRunResult(BaseModel):
    total_cases: int
    passed_cases: int
    failed_cases: int
    results: list[EvalCaseResult]

