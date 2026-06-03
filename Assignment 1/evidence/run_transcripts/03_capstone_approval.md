# Eval Transcript

- Case: `03_capstone_approval`
- Name: Capstone requires advisor approval
- Passed: `True`

## User Request

Can I take MGSC 610 Analytics Capstone Project next term?

## Failures

None

## Structured Output

```json
{
  "student_summary": "SAMPLE001 is in Master of Management in Analytics, has completed MGSC 601, MGSC 602, MGSC 603, and is currently taking MGSC 604.",
  "recommended_courses": [
    {
      "course_code": "MGSC 610",
      "course_name": "Analytics Capstone Project",
      "credits": 6,
      "recommendation": "consider",
      "reason": "This can be considered only with advisor approval because it is the capstone.",
      "prerequisite_status": "met",
      "missing_prerequisites": [],
      "policy_risks": [
        "AdvisorApprovalRequired"
      ]
    }
  ],
  "total_recommended_credits": 0,
  "advisor_approval_required": true,
  "approval_reason": "MGSC 610 Analytics Capstone Project requires advisor approval.",
  "blocked": false,
  "blocking_reason": null,
  "policy_risks": [
    {
      "rule_id": "capstone_approval",
      "name": "AdvisorApprovalRequired",
      "severity": "approval_required",
      "message": "MGSC 610 Analytics Capstone Project requires advisor approval.",
      "course_codes": [
        "MGSC 610"
      ]
    }
  ],
  "next_steps": [
    "Contact a human advisor for approval before using the flagged plan."
  ],
  "confidence": "high",
  "fixture_scope_note": "This recommendation uses a small fake fixture catalog for an AI agents assignment. It is not official McGill advising."
}
```
