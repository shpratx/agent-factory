"""gr-L1-secrets-protection: Prevent credentials, API keys, tokens from appearing in output"""
import re

SECRET_PATTERNS = {
    "aws_key": r'AKIA[0-9A-Z]{16}',
    "generic_api_key": r'(?:api[_-]?key|apikey)\s*[:=]\s*["\']?[A-Za-z0-9_\-]{20,}',
    "generic_secret": r'(?:secret|password|token|passwd)\s*[:=]\s*["\']?[^\s"\']{8,}',
    "jwt": r'eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}',
    "private_key": r'-----BEGIN\s+(RSA\s+)?PRIVATE\s+KEY-----',
}


class L1SecretsProtectionGuardrail:
    name = "gr-L1-secrets-protection"
    layer = "L1"
    triggers_on = ["post_execution"]

    def evaluate(self, output, input_data=None, kb_content=None) -> dict:
        violations = []
        text = str(output) if output else ""

        for secret_type, pattern in SECRET_PATTERNS.items():
            if re.search(pattern, text, re.IGNORECASE):
                violations.append({
                    "rule": "credential-patterns",
                    "detail": f"Detected potential {secret_type} in output",
                    "action": "block",
                    "severity": "critical",
                })

        return {
            "passed": len(violations) == 0,
            "violations": violations,
            "guardrail": self.name,
            "layer": self.layer,
        }
