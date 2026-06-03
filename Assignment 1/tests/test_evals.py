from evals.run_evals import evaluate_case, load_eval_cases


def test_all_eval_cases_pass_offline():
    results = [evaluate_case(case) for case in load_eval_cases()]
    assert all(result.passed for result in results), {
        result.id: result.failures for result in results if not result.passed
    }

