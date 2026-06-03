# Eval Transcript

- Case: `04_credit_overload`
- Name: Credit overload request
- Passed: `True`

## User Request

Recommend five 3-credit courses for next term.

## Failures

None

## Structured Output

```json
{
  "student_summary": "SAMPLE001 is in Master of Management in Analytics, has completed MGSC 601, MGSC 602, MGSC 603, and is currently taking MGSC 604.",
  "recommended_courses": [
    {
      "course_code": "MGSC 604",
      "course_name": "Database Systems for Analytics",
      "credits": 3,
      "recommendation": "recommend",
      "reason": "Database Systems for Analytics fits the request and the fixture prerequisite check is satisfied.",
      "prerequisite_status": "met",
      "missing_prerequisites": [],
      "policy_risks": [
        "Maximum next-term credits"
      ]
    },
    {
      "course_code": "MGSC 605",
      "course_name": "Machine Learning Applications",
      "credits": 3,
      "recommendation": "recommend",
      "reason": "Machine Learning Applications fits the request and the fixture prerequisite check is satisfied.",
      "prerequisite_status": "met",
      "missing_prerequisites": [],
      "policy_risks": [
        "Maximum next-term credits"
      ]
    },
    {
      "course_code": "MGSC 609",
      "course_name": "Responsible AI and Governance",
      "credits": 3,
      "recommendation": "recommend",
      "reason": "Responsible AI and Governance fits the request and the fixture prerequisite check is satisfied.",
      "prerequisite_status": "not_required",
      "missing_prerequisites": [],
      "policy_risks": [
        "Maximum next-term credits"
      ]
    },
    {
      "course_code": "MGSC 607",
      "course_name": "Data Visualization and BI",
      "credits": 3,
      "recommendation": "recommend",
      "reason": "Data Visualization and BI fits the request and the fixture prerequisite check is satisfied.",
      "prerequisite_status": "not_required",
      "missing_prerequisites": [],
      "policy_risks": [
        "Maximum next-term credits"
      ]
    },
    {
      "course_code": "MGSC 606",
      "course_name": "Optimization and Decision Models",
      "credits": 3,
      "recommendation": "recommend",
      "reason": "Optimization and Decision Models fits the request and the fixture prerequisite check is satisfied.",
      "prerequisite_status": "met",
      "missing_prerequisites": [],
      "policy_risks": [
        "Maximum next-term credits"
      ]
    }
  ],
  "total_recommended_credits": 15,
  "advisor_approval_required": true,
  "approval_reason": "Proposed plan has 15 credits, above the 9-credit limit.",
  "blocked": false,
  "blocking_reason": null,
  "policy_risks": [
    {
      "rule_id": "max_credits",
      "name": "Maximum next-term credits",
      "severity": "approval_required",
      "message": "Proposed plan has 15 credits, above the 9-credit limit.",
      "course_codes": [
        "MGSC 604",
        "MGSC 605",
        "MGSC 609",
        "MGSC 607",
        "MGSC 606"
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
