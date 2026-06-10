"""gr-L3-confidence-gate: Escalate to HITL when agent confidence is below threshold"""


class L3ConfidenceGateGuardrail:
    name = "gr-L3-confidence-gate"
    layer = "L3"
    triggers_on = ["post_execution"]

    def __init__(self, min_confidence=0.7, block_below=0.5):
        self.min_confidence = min_confidence
        self.block_below = block_below

    def evaluate(self, output, input_data=None, kb_content=None) -> dict:
        violations = []

        if not isinstance(output, dict):
            return {"passed": True, "violations": [], "guardrail": self.name, "layer": self.layer}

        items = output.get("output", {}).get("items", [])
        for i, item in enumerate(items):
            confidence = item.get("metadata", {}).get("confidence")
            if confidence is None:
                violations.append({"rule": "confidence-present", "detail": f"Item {i}: missing confidence score", "action": "block", "severity": "high"})
            elif confidence < self.block_below:
                violations.append({"rule": "low-confidence-block", "detail": f"Item {i}: confidence {confidence} below {self.block_below}", "action": "block", "severity": "critical"})
            elif confidence < self.min_confidence:
                violations.append({"rule": "min-confidence", "detail": f"Item {i}: confidence {confidence} below {self.min_confidence} — escalate to HITL", "action": "flag", "severity": "high"})

        return {
            "passed": all(v["action"] != "block" for v in violations),
            "violations": violations,
            "guardrail": self.name,
            "layer": self.layer,
        }
