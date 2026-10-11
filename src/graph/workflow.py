"""Cyclic workflow orchestration engine supporting LangGraph and native execution."""

from typing import Dict, Any, Callable
from .state import TeamState
from .nodes import architect_node, developer_node, tester_node, reviewer_node
from ..tools.mcp_client import LocalToolExecutor


def should_continue(state: TeamState) -> str:
    """
    Evaluates whether the team needs another developer iteration or proceeds to review.
    """
    if not state.tests_passed:
        if state.iteration_count >= state.max_iterations:
            return "escalate"
        return "developer"
        
    if not state.review_approved:
        if state.status == "CHANGES_REQUESTED":
            if state.iteration_count >= state.max_iterations:
                return "escalate"
            return "developer"
        return "reviewer"
        
    return "end"


class TeamWorkflowEngine:
    """
    Production-grade cyclic agent workflow engine.
    Orchestrates the Architect -> Developer -> Tester -> Reviewer cycle.
    """
    
    def __init__(self, executor: LocalToolExecutor = None):
        self.executor = executor or LocalToolExecutor()

    def run(self, initial_task: str, test_command: str = "pytest", max_iterations: int = 5) -> TeamState:
        """
        Executes the full multi-agent cycle until tests pass and review is approved.
        """
        state = TeamState(
            task=initial_task,
            test_command=test_command,
            max_iterations=max_iterations
        )
        
        # Step 1: Architect Specification
        arch_res = architect_node(state, self.executor)
        state.spec = arch_res["spec"]
        state.plan = arch_res["plan"]
        state.status = arch_res["status"]
        
        # Step 2: Cyclic Development & Verification Loop
        while True:
            # Developer implementation step
            dev_res = developer_node(state, self.executor)
            state.iteration_count = dev_res["iteration_count"]
            state.status = dev_res["status"]
            
            # QA Testing step
            test_res = tester_node(state, self.executor)
            state.test_output = test_res["test_output"]
            state.tests_passed = test_res["tests_passed"]
            state.audit_trail = test_res["audit_trail"]
            state.status = test_res["status"]
            
            # Route decision
            next_action = should_continue(state)
            
            if next_action == "developer":
                continue
            elif next_action == "escalate":
                state.status = "ESCALATED"
                break
            elif next_action == "reviewer":
                # Review & Security Audit step
                rev_res = reviewer_node(state, self.executor)
                state.review_approved = rev_res["review_approved"]
                state.review_comments = rev_res["review_comments"]
                state.status = rev_res["status"]
                
                if state.review_approved:
                    break
                elif state.iteration_count < state.max_iterations:
                    continue
                else:
                    state.status = "ESCALATED"
                    break
            elif next_action == "end":
                break
                
        return state
