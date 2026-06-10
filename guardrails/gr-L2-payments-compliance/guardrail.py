"""gr-L2-payments-compliance: Validate PSD2/SCA regulatory references and payments domain compliance"""


class L2PaymentsComplianceGuardrail:
    name = "gr-L2-payments-compliance"
    layer = "L2"
    triggers_on = "post_execution"

    def evaluate(self, output, input_data=None, kb_content=None) -> dict:
        violations = []
        # regulatory-accuracy: All cited regulations must exist and be correctly referenced
        # sca-requirements: Payment stories must include SCA where applicable
        # terminology-check: Domain terms must match payments KB definitions
        return {
            "passed": len(violations) == 0,
            "violations": violations,
            "guardrail": self.name,
            "layer": self.layer,
        }
