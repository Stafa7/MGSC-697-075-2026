from __future__ import annotations

import json
from pathlib import Path

from advising_agent.advisor import advise_offline
from advising_agent.fixtures import PROJECT_ROOT
from advising_agent.models import EvalCase, EvalCaseResult, EvalRunResult


EVAL_CASES_PATH = PROJECT_ROOT / "evals" / "eval_cases.json"
RESULTS_PATH = PROJECT_ROOT / "evals" / "results" / "eval_results.json"
TRANSCRIPT_DIR = PROJECT_ROOT / "evidence" / "run_transcripts"
TRACE_PATH = PROJECT_ROOT / "evidence" / "traces" / "offline_eval_trace.json"


def load_eval_cases() -> list[EvalCase]:
    raw = json.loads(EVAL_CASES_PATH.read_text(encoding="utf-8"))
    return [EvalCase.model_validate(item) for item in raw]


def evaluate_case(case: EvalCase) -> EvalCaseResult:
    output = advise_offline(case.user_request)
    dumped = json.dumps(output.model_dump(), sort_keys=True)
    failures: list[str] = []

    if output.blocked != case.expected_blocked:
        failures.append(f"expected blocked={case.expected_blocked}, got {output.blocked}")
    if output.advisor_approval_required != case.expected_advisor_approval_required:
        failures.append(
            "expected advisor_approval_required="
            f"{case.expected_advisor_approval_required}, got {output.advisor_approval_required}"
        )

    output_codes = {course.course_code for course in output.recommended_courses}
    recommended_codes = {
        course.course_code for course in output.recommended_courses if course.recommendation == "recommend"
    }
    for code in case.expected_course_codes:
        if code not in output_codes:
            failures.append(f"expected output to mention {code}")
    for code in case.forbidden_recommended_course_codes:
        if code in recommended_codes:
            failures.append(f"expected {code} not to be recommended")
    for substring in case.required_substrings:
        if substring.lower() not in dumped.lower():
            failures.append(f"expected output to contain substring: {substring}")

    return EvalCaseResult(
        id=case.id,
        name=case.name,
        passed=not failures,
        failures=failures,
        output=output,
    )


def save_case_transcript(case: EvalCase, result: EvalCaseResult) -> None:
    TRANSCRIPT_DIR.mkdir(parents=True, exist_ok=True)
    path = TRANSCRIPT_DIR / f"{case.id}.md"
    path.write_text(
        "# Eval Transcript\n\n"
        f"- Case: `{case.id}`\n"
        f"- Name: {case.name}\n"
        f"- Passed: `{result.passed}`\n\n"
        "## User Request\n\n"
        f"{case.user_request}\n\n"
        "## Failures\n\n"
        f"{result.failures or 'None'}\n\n"
        "## Structured Output\n\n"
        "```json\n"
        f"{json.dumps(result.output.model_dump(), indent=2)}\n"
        "```\n",
        encoding="utf-8",
    )


def main() -> None:
    cases = load_eval_cases()
    results = [evaluate_case(case) for case in cases]
    for case, result in zip(cases, results, strict=True):
        save_case_transcript(case, result)

    run_result = EvalRunResult(
        total_cases=len(results),
        passed_cases=sum(1 for result in results if result.passed),
        failed_cases=sum(1 for result in results if not result.passed),
        results=results,
    )
    RESULTS_PATH.parent.mkdir(parents=True, exist_ok=True)
    RESULTS_PATH.write_text(
        json.dumps(run_result.model_dump(), indent=2),
        encoding="utf-8",
    )
    TRACE_PATH.parent.mkdir(parents=True, exist_ok=True)
    TRACE_PATH.write_text(
        json.dumps(
            {
                "trace_type": "offline_eval_trace",
                "agent_name": "CourseAdvisingAgent",
                "tool_count": 3,
                "guardrail": "MissingPrerequisiteBlocker",
                "escalation_rule": "AdvisorApprovalRequired",
                "result_summary": run_result.model_dump(),
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    for result in results:
        status = "PASS" if result.passed else "FAIL"
        print(f"{status} {result.id}: {result.name}")
        for failure in result.failures:
            print(f"  - {failure}")
    print(
        f"\n{run_result.passed_cases}/{run_result.total_cases} cases passed. "
        f"Results saved to {RESULTS_PATH}"
    )
    if run_result.failed_cases:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
