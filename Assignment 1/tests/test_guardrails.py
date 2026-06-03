from advising_agent.advisor import advise_offline
from advising_agent.guardrails import validate_missing_prerequisite_blocker


def test_missing_prerequisite_blocker_allows_safe_offline_output():
    output = advise_offline("Can I take MGSC 608?")
    valid, violations = validate_missing_prerequisite_blocker(output)

    assert valid
    assert violations == []
    assert output.blocked
    assert output.recommended_courses[0].recommendation == "do_not_take"

