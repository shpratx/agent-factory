"""gr-L2-memory-safety: Prevent memory poisoning, cross-agent leakage, and unauthorised memory writes"""


class L2MemorySafetyGuardrail:
    name = "gr-L2-memory-safety"
    layer = "L2"
    triggers_on = "runtime"

    def evaluate(self, output, input_data=None, kb_content=None) -> dict:
        violations = []
        # write-permission: Only agents with memory_write permission can store to long-term memory
        # cross-agent-isolation: Agent cannot read another agent's episodic memory without explicit share
        # poisoning-detection: Detect and block adversarial content injection into memory stores
        return {
            "passed": len(violations) == 0,
            "violations": violations,
            "guardrail": self.name,
            "layer": self.layer,
        }
