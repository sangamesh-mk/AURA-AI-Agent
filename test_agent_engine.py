
import unittest

from agent_engine import AgentEngine
from tools import calculate, get_current_datetime


class TestAgentEngine(unittest.TestCase):
    def setUp(self):
        self.engine = AgentEngine([calculate, get_current_datetime])

    def test_calculator_tool(self):
        result = self.engine.execute_tool(
            "calculate", {"expression": "20 + 22"}
        )
        self.assertEqual(result, 42)

    def test_datetime_tool(self):
        result = self.engine.execute_tool("get_current_datetime", {})
        self.assertIsInstance(result, str)
        self.assertTrue(result)

    def test_unknown_tool(self):
        result = self.engine.execute_tool("delete_everything", {})
        self.assertIn("not registered", result)

    def test_invalid_arguments(self):
        result = self.engine.execute_tool("calculate", None)
        self.assertIn("arguments must be a dictionary", result)

    def test_tool_exception(self):
        def failing_tool():
            raise RuntimeError("Test failure")

        engine = AgentEngine([failing_tool])
        result = engine.execute_tool("failing_tool", {})
        self.assertIn("Tool execution failed", result)


if __name__ == "__main__":
    unittest.main()
