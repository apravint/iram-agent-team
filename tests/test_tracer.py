"""Unit tests for distributed tracing and observability."""

import time
import unittest
from src.telemetry.tracer import AgentTeamTracer


class TestTracer(unittest.TestCase):

    def test_tracer_lifecycle(self):
        tracer = AgentTeamTracer(trace_id="test-run-1")
        
        # Span 1: Architect
        s1 = tracer.start_span("generate_spec", role="architect", inputs={"task": "Add auth"})
        time.sleep(0.01)
        tracer.end_span(s1, outputs={"spec_length": 500})
        
        # Span 2: Developer
        s2 = tracer.start_span("code_feature", role="developer", inputs={"files": ["auth.py"]})
        time.sleep(0.01)
        tracer.end_span(s2, outputs={"lines_added": 45})
        
        summary = tracer.export_summary()
        self.assertEqual(summary["trace_id"], "test-run-1")
        self.assertEqual(summary["total_spans"], 2)
        self.assertGreater(summary["total_duration_ms"], 0)
        self.assertEqual(summary["spans"][0]["role"], "architect")
        self.assertEqual(summary["spans"][1]["role"], "developer")


if __name__ == "__main__":
    unittest.main()
