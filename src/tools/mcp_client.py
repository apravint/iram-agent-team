"""Model Context Protocol (MCP) and Local Tool Execution Engine."""

import subprocess
import os
from typing import Dict, Any, Tuple
from .firewall_filter import validate_and_gate_command, ToolAuditEntry


class LocalToolExecutor:
    """Safely executes tool calls dispatched by developer and QA agents."""
    
    def __init__(self, working_dir: str = "."):
        self.working_dir = os.path.abspath(working_dir)

    def execute_command(self, command: str) -> Tuple[bool, str, ToolAuditEntry]:
        """
        Validates command via ToolGate firewall, then executes in subshell if safe.
        """
        is_safe, reason, audit = validate_and_gate_command(command, tool_name="run_command")
        if not is_safe:
            return False, reason, audit

        try:
            result = subprocess.run(
                command,
                shell=True,
                cwd=self.working_dir,
                capture_output=True,
                text=True,
                timeout=120
            )
            output = result.stdout
            if result.stderr:
                output += ("\n[STDERR]\n" + result.stderr) if output else result.stderr
            
            audit.output = output[:2000]  # Cap audit preview
            return result.returncode == 0, output, audit
        except subprocess.TimeoutExpired:
            audit.status = "TIMEOUT"
            audit.output = "Command timed out after 120 seconds."
            return False, audit.output, audit
        except Exception as e:
            audit.status = "ERROR"
            audit.output = str(e)
            return False, str(e), audit

    def read_file(self, filepath: str) -> Tuple[bool, str]:
        """Safely reads a text file within or relative to the workspace."""
        full_path = os.path.abspath(os.path.join(self.working_dir, filepath))
        if not os.path.exists(full_path):
            return False, f"File not found: {filepath}"
        try:
            with open(full_path, "r", encoding="utf-8", errors="replace") as f:
                return True, f.read()
        except Exception as e:
            return False, str(e)

    def write_file(self, filepath: str, content: str) -> Tuple[bool, str]:
        """Writes content to a file, creating directories if needed."""
        full_path = os.path.abspath(os.path.join(self.working_dir, filepath))
        try:
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, "w", encoding="utf-8") as f:
                f.write(content)
            return True, f"Successfully wrote {len(content)} bytes to {filepath}"
        except Exception as e:
            return False, str(e)
