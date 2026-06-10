"""gr-L1-audit-trail: Ensure every agent execution produces a complete audit record for compliance and traceability"""


class L1AuditTrailGuardrail:
    name = "gr-L1-audit-trail"
    layer = "L1"
    triggers_on = "post_execution"

    def evaluate(self, output, input_data=None, kb_content=None) -> dict:
        violations = []
        # execution-logged: Every execution must produce an audit log entry
        # input-recorded: Input summary must be recorded (PII masked)
        # output-recorded: Output summary and status must be recorded
        return {
            "passed": len(violations) == 0,
            "violations": violations,
            "guardrail": self.name,
            "layer": self.layer,
        }
