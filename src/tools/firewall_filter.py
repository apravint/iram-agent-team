"""ToolGate integration for pre-execution safety gating."""

import sys
import os
import time
from typing import Tuple, List, Optional
from pydantic import BaseModel, Field

# Ensure ToolGate is importable from standard location
TOOLGATE_PATH = os.path.expanduser("~/toolgate")
if TOOLGATE_PATH not in sys.path and os.path.exists(TOOLGATE_PATH):
    sys.path.insert(0, TOOLGATE_PATH)

try:
    from toolgate.firewall import evaluate_command_risk
    HAS_TOOLGATE = True
except ImportError:
    HAS_TOOLGATE = False


class ToolAuditEntry(BaseModel):
    """Audit log entry for tool execution and security gating."""
    tool_name: str
    command: str
    status: str  # "APPROVED", "BLOCKED", "ERROR", "WARNING"
    reason: Optional[str] = None
    output: Optional[str] = None
    timestamp: float = Field(default_factory=time.time)


def validate_and_gate_command(command: str, tool_name: str = "run_command") -> Tuple[bool, str, ToolAuditEntry]:
    """
    Evaluates a tool execution command through ToolGate's 7-question safety firewall.
    Returns:
        (is_allowed: bool, reason: str, audit_entry: ToolAuditEntry)
    """
    timestamp = time.time()
    
    if not HAS_TOOLGATE:
        # Basic fallback defense
        blocked_keywords = ["rm -rf /", "rm -rf ~", "mkfs", "dd of=/dev/sd", "> /dev/sd"]
        for kw in blocked_keywords:
            if kw in command:
                entry = ToolAuditEntry(
                    tool_name=tool_name,
                    command=command,
                    status="BLOCKED",
                    reason=f"Dangerous keyword matched: {kw}",
                    timestamp=timestamp
                )
                return False, entry.reason, entry
        
        entry = ToolAuditEntry(
            tool_name=tool_name,
            command=command,
            status="APPROVED",
            reason="Basic safety check passed",
            timestamp=timestamp
        )
        return True, "Safe", entry

    risk, flags = evaluate_command_risk(command)
    
    if risk == "DENY":
        reason = f"Blocked by ToolGate Firewall: {'; '.join(flags)}"
        entry = ToolAuditEntry(
            tool_name=tool_name,
            command=command,
            status="BLOCKED",
            reason=reason,
            timestamp=timestamp
        )
        return False, reason, entry
        
    elif risk == "PROMPT":
        reason = f"Flagged by ToolGate for Caution: {'; '.join(flags)}"
        entry = ToolAuditEntry(
            tool_name=tool_name,
            command=command,
            status="WARNING",
            reason=reason,
            timestamp=timestamp
        )
        return True, reason, entry
        
    entry = ToolAuditEntry(
        tool_name=tool_name,
        command=command,
        status="APPROVED",
        reason="Firewall cleared",
        timestamp=timestamp
    )
    return True, "Safe", entry
