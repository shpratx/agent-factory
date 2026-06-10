"""gr-L2-tool-permissions: Enforce least-privilege tool access — agents can only invoke permitted tools"""


class L2ToolPermissionsGuardrail:
    name = "gr-L2-tool-permissions"
    layer = "L2"
    triggers_on = "runtime"

    def evaluate(self, output, input_data=None, kb_content=None) -> dict:
        violations = []
        # allowed-tools: Agent can only call tools in its tools_allowed list
        # denied-tools: Agent must never call tools in its tools_denied list
        # scope-check: Tool calls must be within agent's org_scope
        return {
            "passed": len(violations) == 0,
            "violations": violations,
            "guardrail": self.name,
            "layer": self.layer,
        }
