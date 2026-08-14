# gr-L1-citation-verifier

**Layer:** L1
**Triggers on:** output (output rail) — fires directly on `L1-vision-regulatory-feasibility-checker`'s own response, before the evaluator sees it
**On fail:** Block
**Implementation:** LLM-driven (Colang), Prompt-Only Mode — three standard `define bot` blocks, no `define flow`, no Python dependency
**Applies to:** `L1-vision-regulatory-feasibility-checker` (`configured_agents`, wired via that agent's `spec.yaml` `context.guardrails` as a BLOCKER)

## What does it do?

Every constraint this agent emits is a compliance claim — "this activity requires licensing," "this needs a Red rating." Per `output_schema.json`, each `constraints[]` item's `citation` object is `required` and must carry both `source_reference` (the machine-readable pointer to the attached KB/regulatory-db source) and `regulation` (the specific named regulation or section). Without both, the claim is unverifiable — indistinguishable from a hallucination dressed up as a citation.

This guardrail checks the citation objects directly, independent of anything the response says about itself.

**What it validates (per constraint):**
- `citation.source_reference` is non-empty, non-null — the primary pass/fail field
- `citation.regulation` is non-empty and names a specific regulation/section, not a generic placeholder ("applicable regulations", "relevant law", "comply with regulations")
- Every constraint has a citation object at all — checked unconditionally, even if none of them do
- A citation array, if present, is not empty
- `source_reference` plausibly resolves to a real, attached KB/document/regulatory-db source, not a fabricated name

**What it explicitly does NOT accept as a substitute:**
- A populated `rationale_summary`, `mitigation_summary`, or `reasoning` that names a regulation in prose — only the citation object's own fields count
- The agent's own self-assessment (`execution_summary`, a "guardrails evaluated" note, etc.) claiming citations are complete — this guardrail re-derives the check itself and disregards the response's own verdict

**Why it matters:** citations are the traceability chain from a Green/Amber/Red verdict back to the regulation that drives it. A constraint with `citation.source_reference: ""` is a compliance-critical claim with no way to verify it — exactly the false-negative risk `L1-vision-regulatory-feasibility-checker`'s own business case calls out as zero-tolerance.

## How It Works

```
L1-vision-regulatory-feasibility-checker generates output
        ↓
┌──────────────────────────────────────────────────────────┐
│  CITATION CHECK (self_check_output)                        │
│                                                              │
│  Scan every citation-like field, at any nesting depth,      │
│  across every constraint individually — no averaging:       │
│  • source_reference non-empty? → ✓/✗                        │
│  • regulation specific, not a placeholder? → ✓/✗             │
│  • citation object present at all? → ✓/✗                     │
│  • citation array (if any) non-empty? → ✓/✗                  │
│  • source plausibly real, not fabricated? → ✓/✗              │
│                                                              │
│  Any constraint failing any check → BLOCK                   │
│  All constraints cited and specific → deliver output        │
└──────────────────────────────────────────────────────────┘
        ↓
Fully-cited output proceeds to L1-vision-regulatory-feasibility-checker-evaluator
```

## File Structure

```
gr-L1-citation-verifier/
├── config.yml                    # Rail config + self_check_input/self_check_output prompts (merged, Prompt-Only Mode)
├── gr-L1-citation-verifier.co    # Prompt-Only Colang flow (3 standard define bot blocks, JSON verdict)
├── spec.yaml                     # Guardrail specification
└── README.md                     # This file
```

**Prompt-Only Mode:** `gr-L1-citation-verifier.co` relies entirely on NeMo's built-in `self check output` flow (`config.yml` `rails.output.flows`). It defines no custom flow — just the three standard `define bot` responses (`refuse to respond`, `inform cannot answer`, `inform answer unknown`), all returning the same structured JSON verdict (`detected`, `verdict`, `reason`, `severity`, `category`, `rail`). The detection logic lives entirely in the `self_check_*` prompts in `config.yml`.

`config.yml` carries the same rule set twice — once as `self_check_input` (over `{{ user_input }}`), once as `self_check_output` (over `{{ bot_response }}`) — so the gate reads identically whichever rail is wired up, and standalone prompt testing works with pasted content landing in either slot.

**Polarity:** `"yes"` = violation (block), `"no"` = safe. This matches NeMo's built-in self-check convention and the L1 quality-gate guardrails.

## Testing

### Option 1: Prompt-Based Testing (LLM Judgement Only)

**Valid output (expected: "no"):**

```json
{"constraints": [{"id": "CON-01", "name": "Food business registration", "status": "Red", "citation": {"source_reference": "kb-L2-domain-regulatory#food-safety", "regulation": "Food Safety Act 1990, s.19"}, "rationale_summary": "Registration required before trading", "mitigation_summary": "Register with local authority 28 days before trading start", "requires_legal_review": false, "confidence": 0.9, "reasoning": "Directly required for any food business"}]}
```

**Invalid output (expected: "yes") — missing source_reference:**

```json
{"constraints": [{"id": "CON-01", "name": "Food business registration", "status": "Red", "citation": {"source_reference": "", "regulation": "Food Safety Act 1990, s.19"}, "rationale_summary": "Registration required before trading", "mitigation_summary": "Register before trading", "requires_legal_review": false, "confidence": 0.9, "reasoning": "..."}]}
```

**Invalid output (expected: "yes") — generic regulation placeholder:**

```json
{"constraints": [{"id": "CON-01", "name": "Food business registration", "status": "Amber", "citation": {"source_reference": "kb-L2-domain-regulatory#food-safety", "regulation": "applicable regulations"}, "rationale_summary": "...", "mitigation_summary": "...", "requires_legal_review": false, "confidence": 0.8, "reasoning": "..."}]}
```

Paste the `self_check_output` prompt from `config.yml` with each output above (or `self_check_input` if you are pasting the payload as user input).

### Test Cases Matrix

| Test | Mutation | Expected |
|------|----------|----------|
| Fully cited constraint, specific regulation | None | "no" |
| Missing `source_reference` | `source_reference: ""` | "yes" |
| Generic `regulation` placeholder | `regulation: "applicable regulations"` | "yes" |
| Missing citation object entirely | `citation` key absent | "yes" |
| Empty citation array | `citations: []` | "yes" |
| Fabricated source | `source_reference: "kb-fake-nonexistent"` | "yes" |
| Multiple constraints, one missing citation | Constraint 2 has no citation | "yes" |
| Detailed `rationale_summary` naming a regulation, but empty `citation.regulation` | Sibling field populated, citation field empty | "yes" |
| Response's own `execution_summary` claims citations complete, but a constraint's citation is empty | Self-assessment present and wrong | "yes" |
| Green constraint, terse but specific citation | None | "no" |
| `INSUFFICIENT_CONTEXT` envelope, no constraints produced | No citable content | "no" |

### Option 2: End-to-End Flow Testing (NeMo Guardrails SDK)

```python
from nemoguardrails import LLMRails, RailsConfig

config = RailsConfig.from_path("./gr-L1-citation-verifier")
rails = LLMRails(config)

response = await rails.generate_async(
    messages=[{"role": "assistant", "content": "<fully-cited constraints JSON>"}]
)
assert "blocked" not in response["content"].lower()
print("Fully-cited output passed through")

response = await rails.generate_async(
    messages=[{"role": "assistant", "content": "<constraint with empty source_reference>"}]
)
assert "blocked" in response["content"].lower()
print("Uncited constraint blocked")
```
