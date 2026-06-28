import unittest

from disaster_mas.simulation import run_simulation


class SimulationTests(unittest.TestCase):
    def test_flood_scenario_produces_action_plan_and_audit_log(self):
        result = run_simulation("flood", seed=42)
        self.assertGreaterEqual(len(result.action_plan), 3)
        self.assertTrue(any(event["action"] == "dispatch_assignment" for event in result.audit_log))
        self.assertIn("Library Underpass", result.action_plan)
        self.assertEqual(result.action_plan["Library Underpass"]["route"], "Sherbrooke East")

    def test_conflicting_reports_are_detected(self):
        result = run_simulation("conflicting_reports", seed=42)
        self.assertTrue(result.conflicts)
        self.assertIn("Library Underpass", result.conflicts[0])

    def test_high_risk_or_scarce_resource_decisions_get_human_approval(self):
        result = run_simulation("aftershock", seed=42)
        approvals = [event for event in result.audit_log if event["action"] == "approval_recorded"]
        self.assertTrue(approvals)
        self.assertTrue(any(item["approval"] == "approved_with_conditions" for item in result.action_plan.values()))
        first_location = next(iter(result.action_plan))
        self.assertEqual(first_location, "North Residence")
        self.assertEqual(result.action_plan[first_location]["priority"], "critical")


if __name__ == "__main__":
    unittest.main()
