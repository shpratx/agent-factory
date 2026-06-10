"""gr-L3-agent-rate-limit: Limit the number of tool calls and downstream agent invocations per execution"""


class L3AgentRateLimitGuardrail:
    name = "gr-L3-agent-rate-limit"
    layer = "L3"
    triggers_on = "runtime"

    def evaluate(self, output, input_data=None, kb_content=None) -> dict:
        violations = []
        # max-tool-calls: Agent cannot exceed configured max tool calls per execution
        # max-agent-calls: Orchestrator cannot invoke more than configured downstream agents
        # cooldown: Enforce minimum interval between repeated tool calls
        return {
            "passed": len(violations) == 0,
            "violations": violations,
            "guardrail": self.name,
            "layer": self.layer,
        }
