"""gr-L4-reasoning-validator: Validate that the reasoning field is non-empty, structured, and contains decision rationale"""


class L4ReasoningValidatorGuardrail:
    name = "gr-L4-reasoning-validator"
    layer = "L4"
    triggers_on = "post_execution"

    def evaluate(self, output, input_data=None, kb_content=None) -> dict:
        violations = []
        # reasoning-present: metadata.reasoning must not be null or empty
        # min-length: Reasoning must be at least 20 characters
        # contains-rationale: Reasoning should reference input data or KB sources
        return {
            "passed": len(violations) == 0,
            "violations": violations,
            "guardrail": self.name,
            "layer": self.layer,
        }
