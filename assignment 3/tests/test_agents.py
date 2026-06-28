import unittest

from disaster_mas.agents import ScoutAgent


class AgentBoundaryTests(unittest.TestCase):
    def test_scout_cannot_dispatch(self):
        scout = ScoutAgent()
        with self.assertRaises(PermissionError):
            scout.ensure_permission("assign")


if __name__ == "__main__":
    unittest.main()
