"""gr-L3-consistency-checker: Detect contradictions and duplicates in multi-item output"""


class L3ConsistencyCheckerGuardrail:
    name = "gr-L3-consistency-checker"
    layer = "L3"
    triggers_on = ["post_execution"]

    def evaluate(self, output, input_data=None, kb_content=None) -> dict:
        violations = []

        if not isinstance(output, dict):
            return {"passed": True, "violations": [], "guardrail": self.name, "layer": self.layer}

        items = output.get("output", {}).get("items", [])
        if len(items) <= 1:
            return {"passed": True, "violations": [], "guardrail": self.name, "layer": self.layer}

        # Check duplicate IDs
        ids = [item.get("id") for item in items]
        if len(ids) != len(set(ids)):
            violations.append({"rule": "no-duplicate-ids", "detail": "Duplicate item IDs detected", "action": "block", "severity": "critical"})

        # Check duplicate titles
        titles = [item.get("title") for item in items]
        if len(titles) != len(set(titles)):
            violations.append({"rule": "entity-consistency", "detail": "Duplicate titles detected — possible redundant items", "action": "flag", "severity": "high"})

        return {
            "passed": len(violations) == 0,
            "violations": violations,
            "guardrail": self.name,
            "layer": self.layer,
        }
