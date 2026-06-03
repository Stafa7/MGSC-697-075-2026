# Eval Transcript

- Case: `02_missing_prerequisite`
- Name: Missing prerequisite blocked course
- Passed: `True`

## User Request

I want to take MGSC 608 next term, but I have only completed Python and statistics.

## Failures

None

## Structured Output

```json
{
  "student_summary": "SAMPLE001 is in Master of Management in Analytics, has completed MGSC 601, MGSC 602, MGSC 603, and is currently taking MGSC 604.",
  "recommended_courses": [
    {
      "course_code": "MGSC 608",
      "course_name": "AI Engineering Studio",
      "credits": 3,
      "recommendation": "do_not_take",
      "reason": "Do not take MGSC 608 yet because prerequisites are missing: MGSC 605.",
      "prerequisite_status": "missing",
      "missing_prerequisites": [
        "MGSC 605"
      ],
      "policy_risks": [
        "MissingPrerequisiteBlocker"
      ]
    }
  ],
  "total_recommended_credits": 0,
  "advisor_approval_required": false,
  "approval_reason": null,
  "blocked": true,
  "blocking_reason": "MGSC 608 is missing prerequisites: MGSC 605.",
  "policy_risks": [
    {
      "rule_id": "missing_prerequisites_block",
      "name": "MissingPrerequisiteBlocker",
      "severity": "blocking",
      "message": "MGSC 608 is missing prerequisites: MGSC 605.",
      "course_codes": [
        "MGSC 608"
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
