"""Command-line interface for the IRAM Agent Team engine."""

import argparse
import sys
import os
import yaml
from .graph.workflow import TeamWorkflowEngine
from .telemetry.tracer import AgentTeamTracer


def load_team_config(config_path: str = "config/team.yaml") -> dict:
    if os.path.exists(config_path):
        with open(config_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    return {}


def main():
    parser = argparse.ArgumentParser(
        description="IRAM Autonomous Agent Team Orchestrator with Cyclic Verification & Pre-Execution Safety"
    )
    parser.add_argument(
        "task",
        nargs="?",
        default="Verify project test seams and security boundaries",
        help="The software engineering goal or feature for the team to complete"
    )
    parser.add_argument(
        "--test-cmd",
        default="pytest tests/ -q",
        help="Test runner command for QA verification loop (default: 'pytest tests/ -q')"
    )
    parser.add_argument(
        "--max-iterations",
        type=int,
        default=5,
        help="Maximum developer-tester retry cycles before escalating (default: 5)"
    )
    parser.add_argument(
        "--config",
        default="config/team.yaml",
        help="Path to team role specification YAML"
    )

    args = parser.parse_args()
    
    print("\n" + "=" * 65)
    print("  🚀 IRAM AGENT TEAM: TESTABLE CYCLIC DEVELOPMENT ENGINE")
    print("=" * 65)
    print(f"🎯 Objective     : {args.task}")
    print(f"🧪 Test Runner   : {args.test_cmd}")
    print(f"🔄 Max Cycles    : {args.max_iterations}")
    print("=" * 65 + "\n")
    
    tracer = AgentTeamTracer()
    engine = TeamWorkflowEngine()
    
    span = tracer.start_span("team_execution", role="orchestrator", inputs={"task": args.task})
    state = engine.run(
        initial_task=args.task,
        test_command=args.test_cmd,
        max_iterations=args.max_iterations
    )
    tracer.end_span(span, outputs={"status": state.status, "iterations": state.iteration_count})
    
    print(f"📐 [Architect]   : Specification generated ({len(state.spec)} chars)")
    print(f"💻 [Developer]   : Iterations completed ({state.iteration_count} cycles)")
    print(f"🧪 [QA Tester]   : Status -> {state.status} (Tests Passed: {state.tests_passed})")
    print(f"🛡️ [Reviewer]    : Approval -> {state.review_approved}")
    
    if state.audit_trail:
        blocked = sum(1 for a in state.audit_trail if a.status == "BLOCKED")
        print(f"🔒 [ToolGate]    : {len(state.audit_trail)} commands audited ({blocked} blocked)")
        
    print("\n" + "=" * 65)
    if state.status == "APPROVED":
        print("  ✅ WORKFLOW SUCCESS: CODE VERIFIED AND APPROVED")
    elif state.status == "ESCALATED":
        print("  ⚠️ WORKFLOW ESCALATED: EXCEEDED MAXIMUM ALLOWED RETRIES")
    else:
        print(f"  ℹ️ WORKFLOW STATUS: {state.status}")
    print("=" * 65 + "\n")


if __name__ == "__main__":
    main()
