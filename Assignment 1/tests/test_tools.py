from advising_agent.fixtures import load_student_profile
from advising_agent.tools import check_prerequisites, flag_policy_risk, search_courses


def test_search_courses_finds_ai_engineering():
    result = search_courses(query="AI engineering")
    assert [course.code for course in result.matches] == ["MGSC 608"]


def test_check_prerequisites_detects_missing_requirement():
    result = check_prerequisites("MGSC 608", ["MGSC 602", "MGSC 603"], [])
    assert not result.prerequisites_met
    assert result.missing_prerequisites == ["MGSC 604", "MGSC 605"]


def test_policy_flags_capstone_approval():
    student = load_student_profile()
    result = flag_policy_risk(["MGSC 610"], student)
    assert result.advisor_approval_required
    assert any(risk.rule_id == "capstone_approval" for risk in result.risks)


def test_policy_flags_credit_overload():
    student = load_student_profile()
    result = flag_policy_risk(["MGSC 604", "MGSC 605", "MGSC 606", "MGSC 607"], student)
    assert result.advisor_approval_required
    assert any(risk.rule_id == "max_credits" for risk in result.risks)

