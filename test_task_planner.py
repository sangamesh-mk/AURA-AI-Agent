
import unittest

from task_planner import (
    StepStatus,
    create_plan,
)


class TestTaskPlanner(unittest.TestCase):
    def test_create_plan(self):
        plan = create_plan("Calculate 25 * 4")

        self.assertEqual(plan.goal, "Calculate 25 * 4")
        self.assertEqual(len(plan.steps), 5)
        self.assertFalse(plan.is_complete)

    def test_next_step(self):
        plan = create_plan("Test AURA")

        self.assertEqual(
            plan.next_step().status,
            StepStatus.PENDING,
        )

    def test_complete_steps(self):
        plan = create_plan("Test AURA")

        for index in range(len(plan.steps)):
            plan.start_step(index)
            plan.complete_step(index, "Verified")

        self.assertTrue(plan.is_complete)
        self.assertIsNone(plan.next_step())

    def test_failed_step(self):
        plan = create_plan("Test AURA")

        plan.start_step(0)
        plan.fail_step(0, "Test failure")

        self.assertTrue(plan.has_failed_step)
        self.assertFalse(plan.is_complete)

    def test_cannot_complete_pending_step(self):
        plan = create_plan("Test AURA")

        with self.assertRaises(ValueError):
            plan.complete_step(0, "Done")

    def test_empty_goal_rejected(self):
        with self.assertRaises(ValueError):
            create_plan("   ")


if __name__ == "__main__":
    unittest.main()
