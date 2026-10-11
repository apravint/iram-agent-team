"""Node execution functions for Architect, Developer, Tester, and Reviewer."""

import os
from typing import Dict, Any, Optional
from .state import TeamState


def architect_node(state: TeamState, executor: Optional[Any] = None) -> Dict[str, Any]:
    """
    Architect deconstructs the user task into formal technical specifications,
    contracts, invariants, and actionable implementation steps.
    """
    task = state.task
    
    spec = (
        f"### Technical Specification for: {task}\n\n"
        f"#### Core Objectives:\n"
        f"- Implement modular, verifiable functionality meeting the requirements.\n"
        f"- Maintain zero regressions across existing test suites.\n\n"
        f"#### Acceptance Criteria:\n"
        f"1. 100% of unit tests must execute cleanly without errors.\n"
        f"2. Strict input validation and deterministic error handling.\n"
        f"3. All changes must comply with ToolGate safety policies.\n"
    )
    
    plan = [
        f"1. Analyze existing code structure for '{task}'",
        "2. Implement required interfaces and functions",
        "3. Write/Update test suites to cover edge cases",
        "4. Execute tests and verify zero regressions",
        "5. Final code review and security audit"
    ]
    
    return {
        "spec": spec,
        "plan": plan,
        "status": "SPECIFIED"
    }


def developer_node(state: TeamState, executor: Optional[Any] = None) -> Dict[str, Any]:
    """
    Developer writes code, fixes test regressions, and addresses reviewer feedback.
    """
    iteration = state.iteration_count + 1
    files_modified = list(state.files_modified)
    
    return {
        "iteration_count": iteration,
        "status": "IMPLEMENTED",
        "files_modified": files_modified
    }


def tester_node(state: TeamState, executor: Optional[Any] = None) -> Dict[str, Any]:
    """
    QA Engineer executes the configured test command and records the verification outcome.
    """
    if executor is None:
        from ..tools.mcp_client import LocalToolExecutor
        executor = LocalToolExecutor()
        
    cmd = state.test_command
    success, output, audit = executor.execute_command(cmd)
    
    audits = list(state.audit_trail)
    if audit:
        audits.append(audit)
    
    return {
        "test_output": output,
        "tests_passed": success,
        "audit_trail": audits,
        "status": "TESTS_PASSED" if success else "TESTS_FAILED"
    }


def reviewer_node(state: TeamState, executor: Optional[Any] = None) -> Dict[str, Any]:
    """
    Security and Code Reviewer audits final code diffs and approves completion.
    """
    has_blocked_tools = any(a.status == "BLOCKED" for a in state.audit_trail)
    
    if state.tests_passed and not has_blocked_tools:
        return {
            "review_approved": True,
            "review_comments": ["All test assertions passed.", "ToolGate security checks approved."],
            "status": "APPROVED"
        }
    else:
        comments = []
        if not state.tests_passed:
            comments.append("Rejection: Test suite has not yet achieved 100% pass rate.")
        if has_blocked_tools:
            comments.append("Rejection: One or more tool commands were blocked by ToolGate firewall.")
            
        return {
            "review_approved": False,
            "review_comments": comments,
            "status": "CHANGES_REQUESTED"
        }
