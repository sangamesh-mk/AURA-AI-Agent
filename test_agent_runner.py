
import unittest

from agent_engine import AgentEngine
from agent_runner import AgentRunner
from tools import calculate


class TestAgentRunner(unittest.TestCase):
    def setUp(self):
        self.runner = AgentRunner(AgentEngine([calculate]))

    def test_successful_calculation(self):
        report = self.runner.run_tool_task(
            "Calculate 25 * 4",
            "calculate",
            {"expression": "25 * 4"},
        )

        self.assertTrue(report["complete"])
        self.assertFalse(report["failed"])
        self.assertEqual(
            report["steps"][2]["result"],
            "100",
        )

    def test_unknown_tool(self):
        report = self.runner.run_tool_task(
            "Perform a task",
            "unknown_tool",
            {},
        )

        self.assertFalse(report["complete"])
        self.assertTrue(report["failed"])

    def test_invalid_arguments(self):
        report = self.runner.run_tool_task(
            "Calculate a value",
            "calculate",
            {},
        )

        self.assertTrue(report["failed"])


if __name__ == "__main__":
    unittest.main()
