"""gr-L1-pii-detection: Detect and mask personally identifiable information in input and output"""
import re

PII_PATTERNS = {
    "email": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
    "phone": r'\b(?:\+?1[-.\s]?)?(?:\(?\d{3}\)?[-.\s]?)?\d{3}[-.\s]?\d{4}\b',
    "ssn": r'\b\d{3}-\d{2}-\d{4}\b',
    "credit_card": r'\b(?:\d{4}[-\s]?){3}\d{4}\b',
    "uk_nino": r'\b[A-Z]{2}\d{6}[A-Z]\b',
}


class L1PiiDetectionGuardrail:
    name = "gr-L1-pii-detection"
    layer = "L1"
    triggers_on = ["pre_execution", "post_execution"]

    def evaluate(self, output, input_data=None, kb_content=None) -> dict:
        violations = []
        text = str(output) if output else ""

        for pii_type, pattern in PII_PATTERNS.items():
            matches = re.findall(pattern, text)
            if matches:
                violations.append({
                    "rule": "pii-patterns",
                    "detail": f"Detected {pii_type}: {len(matches)} occurrence(s)",
                    "action": "block",
                    "severity": "critical",
                })

        return {
            "passed": len(violations) == 0,
            "violations": violations,
            "guardrail": self.name,
            "layer": self.layer,
        }
