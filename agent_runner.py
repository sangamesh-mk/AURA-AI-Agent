
from task_planner import create_plan, StepStatus
from agent_engine import AgentEngine


class AgentRunner:
    """Coordinate task plans and registered tool execution."""

    def __init__(self, engine: AgentEngine):
        self.engine = engine

    def run_tool_task(
        self,
        goal: str,
        tool_name: str,
        arguments: dict,
    ) -> dict:
        plan = create_plan(goal)

        # Step 1: Understand the goal.
        plan.start_step(0)
        plan.complete_step(0, goal)

        # Step 2: Confirm the requested tool exists.
        plan.start_step(1)

        if tool_name not in self.engine.tools:
            plan.fail_step(1, f"Unknown tool: {tool_name}")
            return self._report(plan)

        plan.complete_step(1, f"Selected tool: {tool_name}")

        # Step 3: Execute the registered tool.
        plan.start_step(2)
        result = self.engine.execute_tool(tool_name, arguments)

        if isinstance(result, str) and (
            result.startswith("Tool error:")
            or result.startswith("Tool execution failed:")
        ):
            plan.fail_step(2, result)
            return self._report(plan)

        plan.complete_step(2, str(result))

        # Step 4: Record that execution returned a result.
        plan.start_step(3)
        plan.complete_step(3, "Tool execution returned a result.")

        # Step 5: Summarize the outcome.
        plan.start_step(4)
        plan.complete_step(4, "Task result recorded.")

        return self._report(plan)

    @staticmethod
    def _report(plan) -> dict:
        return {
            "goal": plan.goal,
            "complete": plan.is_complete,
            "failed": plan.has_failed_step,
            "steps": [
                {
                    "description": step.description,
                    "status": step.status.value,
                    "result": step.result,
                }
                for step in plan.steps
            ],
        }
