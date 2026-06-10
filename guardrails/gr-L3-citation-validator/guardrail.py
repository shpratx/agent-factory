"""gr-L3-citation-validator: Ensure every output item has resolvable citations"""


class L3CitationValidatorGuardrail:
    name = "gr-L3-citation-validator"
    layer = "L3"
    triggers_on = ["post_execution"]

    def evaluate(self, output, input_data=None, kb_content=None) -> dict:
        violations = []

        if not isinstance(output, dict):
            return {"passed": False, "violations": [{"rule": "citation-present", "detail": "Output is not valid"}], "guardrail": self.name, "layer": self.layer}

        items = output.get("output", {}).get("items", [])
        for i, item in enumerate(items):
            citations = item.get("metadata", {}).get("citation", [])
            if not citations:
                violations.append({"rule": "citation-present", "detail": f"Item {i}: no citations provided", "action": "block", "severity": "high"})
            else:
                for c in citations:
                    if not c.get("source_reference"):
                        violations.append({"rule": "source-resolvable", "detail": f"Item {i}: citation missing source_reference", "action": "block", "severity": "high"})

        return {
            "passed": len(violations) == 0,
            "violations": violations,
            "guardrail": self.name,
            "layer": self.layer,
        }
