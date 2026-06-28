import unittest

from disaster_mas.contracts import ContractError, Message


class MessageContractTests(unittest.TestCase):
    def test_invalid_priority_is_rejected(self):
        with self.assertRaises(ContractError):
            Message(
                timestamp="T+00",
                sender="scout",
                receiver="command_center",
                message_type="observation_report",
                priority="urgent",
                location="North Residence",
                payload={},
                confidence=0.9,
                requires_human_approval=False,
                correlation_id="incident-north-residence",
            )

    def test_invalid_confidence_is_rejected(self):
        with self.assertRaises(ContractError):
            Message(
                timestamp="T+00",
                sender="scout",
                receiver="command_center",
                message_type="observation_report",
                priority="high",
                location="North Residence",
                payload={},
                confidence=1.4,
                requires_human_approval=False,
                correlation_id="incident-north-residence",
            )


if __name__ == "__main__":
    unittest.main()
