"""gr-L1-content-safety: Block toxic, harmful, offensive content in input and output"""
import re

HARMFUL_PATTERNS = [
    r'\b(kill|murder|assassinate)\s+(yourself|himself|herself|someone)\b',
    r'\bhow\s+to\s+(make|build|create)\s+(a\s+)?(bomb|weapon|explosive)\b',
    r'\b(suicide|self.harm)\s+(method|instructions|guide)\b',
]


class L1ContentSafetyGuardrail:
    name = "gr-L1-content-safety"
    layer = "L1"
    triggers_on = ["pre_execution", "post_execution"]

    def evaluate(self, output, input_data=None, kb_content=None) -> dict:
        violations = []
        text = str(input_data or "") + " " + str(output or "")

        for pattern in HARMFUL_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                violations.append({
                    "rule": "harmful-content",
                    "detail": "Content flagged as potentially harmful",
                    "action": "block",
                    "severity": "critical",
                })
                break

        return {
            "passed": len(violations) == 0,
            "violations": violations,
            "guardrail": self.name,
            "layer": self.layer,
        }
