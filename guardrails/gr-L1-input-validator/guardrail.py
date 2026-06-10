"""gr-L1-input-validator: Validate incoming requests match expected structure"""


class L1InputValidatorGuardrail:
    name = "gr-L1-input-validator"
    layer = "L1"
    triggers_on = ["pre_execution"]

    def __init__(self, required_parameters=None, max_lengths=None):
        self.required_parameters = required_parameters or []
        self.max_lengths = max_lengths or {}

    def evaluate(self, output, input_data=None, kb_content=None) -> dict:
        violations = []
        params = input_data.get("parameters", {}) if isinstance(input_data, dict) else {}

        for field in self.required_parameters:
            if field not in params or params[field] is None or params[field] == "":
                violations.append({"rule": "required-fields", "detail": f"Missing required parameter: {field}", "action": "block", "severity": "critical"})

        for field, max_len in self.max_lengths.items():
            val = params.get(field, "")
            if isinstance(val, str) and len(val) > max_len:
                violations.append({"rule": "length-limits", "detail": f"{field} exceeds max length {max_len}", "action": "block", "severity": "medium"})

        return {
            "passed": len(violations) == 0,
            "violations": violations,
            "guardrail": self.name,
            "layer": self.layer,
        }
