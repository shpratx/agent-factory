"""gr-L1-output-schema-validator: Ensure agent output conforms to AgentOutput contract"""

REQUIRED_ROOT_FIELDS = ["agent_id", "agent_version", "execution_id", "input_summary", "output"]
REQUIRED_OUTPUT_FIELDS = ["type", "schema_version"]
REQUIRED_ITEM_METADATA = ["confidence", "reasoning", "citation", "trajectory"]


class L1OutputSchemaValidatorGuardrail:
    name = "gr-L1-output-schema-validator"
    layer = "L1"
    triggers_on = ["post_execution"]

    def evaluate(self, output, input_data=None, kb_content=None) -> dict:
        violations = []

        if not isinstance(output, dict):
            violations.append({"rule": "schema-compliance", "detail": "Output must be a JSON object", "action": "block", "severity": "critical"})
            return {"passed": False, "violations": violations, "guardrail": self.name, "layer": self.layer}

        for field in REQUIRED_ROOT_FIELDS:
            if field not in output:
                violations.append({"rule": "required-fields", "detail": f"Missing root field: {field}", "action": "block", "severity": "critical"})

        out = output.get("output", {})
        for field in REQUIRED_OUTPUT_FIELDS:
            if field not in out:
                violations.append({"rule": "required-fields", "detail": f"Missing output field: {field}", "action": "block", "severity": "critical"})

        items = out.get("items", [])
        if items:
            for i, item in enumerate(items):
                meta = item.get("metadata", {})
                for mf in REQUIRED_ITEM_METADATA:
                    if mf not in meta:
                        violations.append({"rule": "field-presence", "detail": f"Item {i}: missing metadata.{mf}", "action": "block", "severity": "high"})

        return {
            "passed": len(violations) == 0,
            "violations": violations,
            "guardrail": self.name,
            "layer": self.layer,
        }
