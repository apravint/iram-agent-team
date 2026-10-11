"""Unit tests for ToolGate pre-execution safety firewall integration."""

import unittest
from src.tools.firewall_filter import validate_and_gate_command
from src.graph.state import TeamState, ToolAuditEntry
from src.graph.nodes import reviewer_node


class TestFirewallIntegration(unittest.TestCase):

    def test_safe_commands_approved(self):
        safe_commands = [
            "pytest tests/",
            "python3 -m unittest",
            "ls -la src/",
            "git status",
            "cat README.md"
        ]
        for cmd in safe_commands:
            is_safe, reason, audit = validate_and_gate_command(cmd)
            self.assertTrue(is_safe, f"Expected safe for: {cmd}")
            self.assertEqual(audit.status, "APPROVED")

    def test_destructive_commands_blocked(self):
        destructive_commands = [
            "rm -rf /",
            "rm -rf /*",
            "mkfs.ext4 /dev/sda1",
            "dd if=/dev/zero of=/dev/sda bs=1M",
            ":(){ :|:& };:"
        ]
        for cmd in destructive_commands:
            is_safe, reason, audit = validate_and_gate_command(cmd)
            self.assertFalse(is_safe, f"Expected blocked for: {cmd}")
            self.assertEqual(audit.status, "BLOCKED")
            self.assertTrue("Blocked" in reason or "Dangerous" in reason)

    def test_reviewer_rejects_on_blocked_firewall_audit(self):
        # If a dangerous command was attempted, reviewer must reject
        state = TeamState(
            task="System cleanup",
            tests_passed=True,
            audit_trail=[
                ToolAuditEntry(
                    tool_name="run_command",
                    command="rm -rf /",
                    status="BLOCKED",
                    reason="Critical deletion blocked"
                )
            ]
        )
        
        result = reviewer_node(state)
        self.assertFalse(result["review_approved"])
        self.assertEqual(result["status"], "CHANGES_REQUESTED")
        self.assertTrue(any("blocked by ToolGate" in comment for comment in result["review_comments"]))


if __name__ == "__main__":
    unittest.main()
