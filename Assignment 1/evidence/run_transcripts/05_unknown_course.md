# Eval Transcript

- Case: `05_unknown_course`
- Name: Unknown course safe failure
- Passed: `True`

## User Request

Can I take MGSC 999?

## Failures

None

## Structured Output

```json
{
  "student_summary": "SAMPLE001 is in Master of Management in Analytics, has completed MGSC 601, MGSC 602, MGSC 603, and is currently taking MGSC 604.",
  "recommended_courses": [
    {
      "course_code": "MGSC 999",
      "course_name": "Unknown fixture course",
      "credits": 0,
      "recommendation": "do_not_take",
      "reason": "MGSC 999 is not in the fake fixture catalog, so the agent cannot evaluate it.",
      "prerequisite_status": "missing",
      "missing_prerequisites": [],
      "policy_risks": [
        "Unknown course code"
      ]
    }
  ],
  "total_recommended_credits": 0,
  "advisor_approval_required": false,
  "approval_reason": null,
  "blocked": true,
  "blocking_reason": "MGSC 999 is not in the fake fixture catalog.",
  "policy_risks": [
    {
      "rule_id": "unknown_course",
      "name": "Unknown course code",
      "severity": "blocking",
      "message": "MGSC 999 is not in the fake fixture catalog.",
      "course_codes": [
        "MGSC 999"
      ]
    }
  ],
  "next_steps": [
    "Do not enroll in blocked courses until the listed issue is resolved."
  ],
  "confidence": "high",
  "fixture_scope_note": "This recommendation uses a small fake fixture catalog for an AI agents assignment. It is not official McGill advising."
}
```
