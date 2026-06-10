"""gr-L1-injection-defence: Detect and block prompt injection patterns in input"""
import re

INJECTION_PATTERNS = [
    r'ignore\s+(all\s+)?previous\s+instructions',
    r'you\s+are\s+now\s+a',
    r'system:\s*',
    r'<\s*system\s*>',
    r'forget\s+(everything|all|your)\s+(above|prior|previous)',
    r'override\s+(your|the)\s+(instructions|rules|prompt)',
    r'do\s+not\s+follow\s+(your|the)\s+(instructions|rules)',
    r'new\s+instructions:',
]


class L1InjectionDefenceGuardrail:
    name = "gr-L1-injection-defence"
    layer = "L1"
    triggers_on = ["pre_execution"]

    def evaluate(self, output, input_data=None, kb_content=None) -> dict:
        violations = []
        text = str(input_data) if input_data else ""

        for pattern in INJECTION_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                violations.append({
                    "rule": "pattern-match",
                    "detail": f"Injection pattern detected: {pattern}",
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
