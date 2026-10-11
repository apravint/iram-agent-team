"""Telemetry and Observability tracing engine compatible with Opik and OpenTelemetry."""

import time
import json
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field


class SpanRecord(BaseModel):
    """Represents a discrete agent step or tool invocation."""
    name: str
    role: str
    start_time: float
    end_time: float = 0.0
    duration_ms: float = 0.0
    inputs: Dict[str, Any] = Field(default_factory=dict)
    outputs: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class AgentTeamTracer:
    """Collects distributed traces and metrics for the agent team."""
    
    def __init__(self, trace_id: Optional[str] = None):
        self.trace_id = trace_id or f"trace-{int(time.time() * 1000)}"
        self.spans: List[SpanRecord] = []

    def start_span(self, name: str, role: str, inputs: Dict[str, Any] = None) -> SpanRecord:
        """Starts a new trace span."""
        span = SpanRecord(
            name=name,
            role=role,
            start_time=time.time(),
            inputs=inputs or {}
        )
        self.spans.append(span)
        return span

    def end_span(self, span: SpanRecord, outputs: Dict[str, Any] = None, metadata: Dict[str, Any] = None):
        """Finalizes a span with execution duration and outputs."""
        span.end_time = time.time()
        span.duration_ms = round((span.end_time - span.start_time) * 1000, 2)
        span.outputs = outputs or {}
        if metadata:
            span.metadata.update(metadata)

    def export_summary(self) -> Dict[str, Any]:
        """Exports a trace summary for logging or Opik/OpenLLMetry integration."""
        total_duration = sum(s.duration_ms for s in self.spans)
        return {
            "trace_id": self.trace_id,
            "total_spans": len(self.spans),
            "total_duration_ms": round(total_duration, 2),
            "spans": [s.model_dump() for s in self.spans]
        }
