
from dataclasses import dataclass, field
from enum import Enum


class StepStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class TaskStep:
    description: str
    status: StepStatus = StepStatus.PENDING
    result: str | None = None


@dataclass
class TaskPlan:
    goal: str
    steps: list[TaskStep] = field(default_factory=list)

    @property
    def is_complete(self) -> bool:
        return bool(self.steps) and all(
            step.status == StepStatus.COMPLETED
            for step in self.steps
        )

    @property
    def has_failed_step(self) -> bool:
        return any(
            step.status == StepStatus.FAILED
            for step in self.steps
        )

    def next_step(self) -> TaskStep | None:
        for step in self.steps:
            if step.status in (StepStatus.PENDING, StepStatus.IN_PROGRESS):
                return step
        return None

    def start_step(self, index: int) -> None:
        step = self.steps[index]
        if step.status != StepStatus.PENDING:
            raise ValueError("Only pending steps can be started.")
        step.status = StepStatus.IN_PROGRESS

    def complete_step(self, index: int, result: str) -> None:
        step = self.steps[index]
        if step.status != StepStatus.IN_PROGRESS:
            raise ValueError("Only in-progress steps can be completed.")
        step.result = result
        step.status = StepStatus.COMPLETED

    def fail_step(self, index: int, reason: str) -> None:
        step = self.steps[index]
        if step.status != StepStatus.IN_PROGRESS:
            raise ValueError("Only in-progress steps can fail.")
        step.result = reason
        step.status = StepStatus.FAILED


def create_plan(goal: str) -> TaskPlan:
    """Create a simple, ordered plan for a user goal."""
    goal = goal.strip()

    if not goal:
        raise ValueError("The goal cannot be empty.")

    return TaskPlan(
        goal=goal,
        steps=[
            TaskStep(f"Understand the goal: {goal}"),
            TaskStep("Identify the required actions and tools"),
            TaskStep("Execute the required actions"),
            TaskStep("Verify the results"),
            TaskStep("Summarize the outcome"),
        ],
    )
