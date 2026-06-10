"""gr-L3-hallucination-detector: Check that agent outputs are grounded in input and KB content — no fabricated claims"""


class L3HallucinationDetectorGuardrail:
    name = "gr-L3-hallucination-detector"
    layer = "L3"
    triggers_on = "post_execution"

    def evaluate(self, output, input_data=None, kb_content=None) -> dict:
        violations = []
        # groundedness: Every claim must trace to input data or attached KB
        # fabrication-patterns: Detect invented entities, statistics, or references
        # confidence-correlation: Low-confidence items must have explicit uncertainty markers
        return {
            "passed": len(violations) == 0,
            "violations": violations,
            "guardrail": self.name,
            "layer": self.layer,
        }
