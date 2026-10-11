"""Unit tests for agent team state and cyclic workflow routing."""

import unittest
from src.graph.state import TeamState
from src.graph.workflow import TeamWorkflowEngine, should_continue
from src.tools.mcp_client import LocalToolExecutor
from src.tools.firewall_filter import ToolAuditEntry


class MockToolExecutor(LocalToolExecutor):
    """Mock executor allowing controllable test pass/fail simulation."""
    
    def __init__(self, fail_count: int = 0):
        super().__init__()
        self.fail_count = fail_count
        self.call_count = 0

    def execute_command(self, command: str):
        self.call_count += 1
        audit = ToolAuditEntry(
            tool_name="run_command",
            command=command,
            status="APPROVED",
            reason="Mock execution"
        )
        if self.call_count <= self.fail_count:
            return False, "AssertionError: 2 != 3 (Simulated failure)", audit
        return True, "100% tests passed (Simulated success)", audit


class TestStateAndWorkflow(unittest.TestCase):

    def test_initial_state_defaults(self):
        state = TeamState(task="Build Fibonacci function")
        self.assertEqual(state.task, "Build Fibonacci function")
        self.assertFalse(state.tests_passed)
        self.assertFalse(state.review_approved)
        self.assertEqual(state.iteration_count, 0)
        self.assertEqual(state.max_iterations, 5)
        self.assertEqual(state.status, "INITIALIZED")

    def test_successful_first_iteration_workflow(self):
        executor = MockToolExecutor(fail_count=0)
        engine = TeamWorkflowEngine(executor=executor)
        
        state = engine.run(
            initial_task="Implement math utility",
            test_command="pytest",
            max_iterations=3
        )
        
        self.assertEqual(state.status, "APPROVED")
        self.assertTrue(state.tests_passed)
        self.assertTrue(state.review_approved)
        self.assertEqual(state.iteration_count, 1)
        self.assertIn("### Technical Specification", state.spec)

    def test_cyclic_retry_and_recovery(self):
        # Fails twice, passes on 3rd attempt
        executor = MockToolExecutor(fail_count=2)
        engine = TeamWorkflowEngine(executor=executor)
        
        state = engine.run(
            initial_task="Fix concurrency bug",
            test_command="pytest",
            max_iterations=5
        )
        
        self.assertEqual(state.status, "APPROVED")
        self.assertTrue(state.tests_passed)
        self.assertTrue(state.review_approved)
        self.assertEqual(state.iteration_count, 3)

    def test_escalation_on_persistent_failure(self):
        # Always fails, exceeds max_iterations
        executor = MockToolExecutor(fail_count=10)
        engine = TeamWorkflowEngine(executor=executor)
        
        state = engine.run(
            initial_task="Impossible task",
            test_command="pytest",
            max_iterations=3
        )
        
        self.assertEqual(state.status, "ESCALATED")
        self.assertFalse(state.tests_passed)
        self.assertFalse(state.review_approved)
        self.assertEqual(state.iteration_count, 3)


if __name__ == "__main__":
    unittest.main()
