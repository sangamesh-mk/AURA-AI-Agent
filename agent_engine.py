
from typing import Any, Callable


class AgentEngine:
    """Execute explicitly registered tools with basic error handling."""

    def __init__(self, tools: list[Callable[..., Any]]):
        self.tools = {}

        for tool in tools:
            name = tool.__name__

            if name in self.tools:
                raise ValueError(f"Duplicate tool name: {name}")

            self.tools[name] = tool

    def execute_tool(self, name: str, arguments: dict[str, Any]) -> Any:
        """Execute one registered tool or return a controlled error."""

        if name not in self.tools:
            return f"Tool error: '{name}' is not registered."

        if not isinstance(arguments, dict):
            return "Tool error: arguments must be a dictionary."

        try:
            result = self.tools[name](**arguments)
            return result
        except Exception as error:
            return f"Tool execution failed: {type(error).__name__}: {error}"
