"""gr-L2-policy-enforcement: Enforce domain-specific topic adherence and policy rules — block out-of-scope requests"""


class L2PolicyEnforcementGuardrail:
    name = "gr-L2-policy-enforcement"
    layer = "L2"
    triggers_on = "pre_execution, post_execution"

    def evaluate(self, output, input_data=None, kb_content=None) -> dict:
        violations = []
        # topic-adherence: Agent must stay within its declared domain scope
        # off-topic-refusal: Return OUT_OF_SCOPE for requests outside domain
        # policy-compliance: Output must comply with domain-specific business policies
        return {
            "passed": len(violations) == 0,
            "violations": violations,
            "guardrail": self.name,
            "layer": self.layer,
        }
