# gr-L1-regulatory-feasibility-quality-gate

**Layer:** L1
**Triggers on:** output — fires at `L1-vision-regulatory-feasibility-checker-evaluator`'s post_execution
**On fail:** Retry once, then escalate to HITL
**Implementation:** LLM-driven (Colang), Prompt-Only Mode — returns a structured JSON verdict via NeMo's built-in `self check output` flow; no `define flow`, no Python dependency
**Applies to:** `L1-vision-regulatory-feasibility-checker-evaluator` only (`configured_agents`)

## What does it do?

`L1-vision-regulatory-feasibility-checker-evaluator` re-derives constraint
severity independently and fixes what it can — a false negative here (an
unmitigated Red constraint slipping through) is a compliance risk, not a
quality nuance. This guardrail fires at that point but validates a
different thing: the **resultant** `L1-vision-regulatory-feasibility-checker`
output — its own `items`, with the evaluator's `fixes_applied` resolved in
— is what actually flows to `L1-vision-statement-generator`. This gate
checks THAT content, independently re-derived from
`L1-vision-regulatory-feasibility-checker/evaluation.md` (also mirrored as
`kb-L1-regulatory-feasibility-evaluation-rubric` for the evaluator's own
runtime use):

1. **Output schema validation** — does the resultant content conform to
   `L1-vision-regulatory-feasibility-checker/output_schema.json` (not the
   evaluator's own output shape)?
2. **Rubric adherence** — does the resultant content actually satisfy
   evaluation.md's rubric — above all, the zero-tolerance rule that every
   Amber/Red constraint carries a real mitigation or an explicit
   legal-review flag, and the BLOCKER rule that no Red constraint gets
   silently dropped from the final list — re-checked directly on the
   resultant content, independent of whatever the evaluator claims it
   fixed.

This is NOT a check on the evaluator's own scores/findings/final_decision
— it is an independent re-derivation of the rules this pipeline step
exists to enforce, run against what actually ships downstream.

**Why it matters:** an evaluator reporting `fixed_and_approved` is a claim,
not a guarantee. If a "fix" left `mitigation_summary` null on a Red
constraint with `requires_legal_review: false`, a citation still reads
"applicable regulations" instead of a named section, or a Red constraint
discussed in the reasoning never made it into the final `constraints[]`
array, that is exactly the false negative this gate exists to catch —
before it reaches `L1-vision-statement-generator`, regardless of what the
evaluator's own bookkeeping says.

### Rules

| # | Rule | Category | Action | Severity |
|---|------|----------|--------|----------|
| 1 | schema-compliance | Schema | block | critical |
| 2 | amber-red-mitigation-or-legal-review | Rubric adherence | block | critical |
| 3 | ids-sequential-no-gaps | Rubric adherence | block | high |
| 4 | citation-specificity | Rubric adherence | block | critical |
| 5 | overall-status-rationale-specific | Rubric adherence | flag | high |
| 6 | no-downgraded-severity | Rubric adherence | flag | high |
| 7 | legal-review-not-default-escape | Rubric adherence | flag | medium |
| 8 | no-omitted-red-constraint | Rubric adherence — **BLOCKER** | block | critical |

## How It Works

```
L1-vision-regulatory-feasibility-checker-evaluator concludes
        ↓
┌────────────────────────────────────────────────────────────────────┐
│  REGULATORY-FEASIBILITY QUALITY GATE (post_execution, fires on eval)│
│                                                                      │
│  self_check_output (LLM) reconstructs the RESULTANT content —       │
│  constraints/overall_status/open_items — and checks:                │
│                                                                      │
│  1. Required fields present on every constraint/overall_status       │
│  2. Every Amber/Red: mitigation_summary OR requires_legal_review?    │
│     (zero tolerance, re-checked on the RESULTANT content)           │
│  3. citation.regulation is a specific section, not a generic phrase?│
│  4. CON-NN / OI-NN ids sequential, no gaps/duplicates?               │
│  5. overall_status.rationale_summary names the driving constraint?   │
│  6. severity actually matches what the rationale describes?          │
│  7. requires_legal_review not overused as a blanket escape?          │
│  8. no Red constraint discussed in reasoning but missing from the    │
│     final constraints[] array? (BLOCKER)                            │
│                                                                      │
│  Any ✗ → BLOCK, retry once, then escalate_to_hitl                    │
│  All ✓ → gate passes                                                 │
└────────────────────────────────────────────────────────────────────┘
        ↓
Resultant regulatory-feasibility content flows to L1-vision-statement-generator
```

## File Structure

```
gr-L1-regulatory-feasibility-quality-gate/
├── config.yml                                     # Rail config + self_check_output prompt (merged, Prompt-Only Mode)
├── gr-L1-regulatory-feasibility-quality-gate.co    # Prompt-Only Colang flow (JSON verdict bot blocks)
├── spec.yaml                                       # Guardrail specification
└── README.md                                       # This file
```

**Prompt-Only Mode:** `gr-L1-regulatory-feasibility-quality-gate.co` relies
entirely on NeMo's built-in `self check output` flow. It defines no custom
flow — just the three standard `define bot` responses (`refuse to respond`,
`inform cannot answer`, `inform answer unknown`), all returning the same
structured JSON verdict (`detected`, `verdict`, `reason`, `severity`,
`category`, `rail`). The actual detection logic (all 8 rules above) lives
in the `self_check_output` prompt in `config.yml`.

## Testing

### Option 1: Prompt-Based Testing (LLM Judgement Only)

**Valid resultant output (expected: "yes")** — Red constraint properly mitigated, specific citation:

```json
{
  "constraints": [
    {"id": "CON-01", "name": "Food business registration", "status": "Red", "citation": {"source_reference": "kb-L2-domain-regulatory", "regulation": "Food Safety Act 1990, s.19"}, "rationale_summary": "Registration required before trading; not yet structured for it", "mitigation_summary": "Register with local authority 28 days before trading start", "requires_legal_review": false, "confidence": 0.9, "reasoning": "Directly required for any food business"}
  ],
  "overall_status": {"status": "Amber", "rationale_summary": "CON-01 (Red) has a precedented mitigation, discounted one level per the stated rule"},
  "open_items": []
}
```

**Invalid resultant output (expected: "no")** — same Red constraint, but mitigation_summary is null and requires_legal_review is false, even after evaluation concluded:

```json
{
  "constraints": [
    {"id": "CON-01", "name": "Food business registration", "status": "Red", "citation": {"source_reference": "kb-L2-domain-regulatory", "regulation": "Food Safety Act 1990, s.19"}, "rationale_summary": "Registration required before trading; not yet structured for it", "mitigation_summary": null, "requires_legal_review": false, "confidence": 0.9, "reasoning": "..."}
  ],
  "overall_status": {"status": "Red", "rationale_summary": "..."},
  "open_items": []
}
```

Paste the `self_check_output` prompt from `config.yml` with either payload above. LLM should answer "yes" for the first, "no" for the second.

### Test Cases Matrix

| Test | Mutation | Expected |
|------|----------|----------|
| Clean, fully-mitigated resultant content | None | "yes" |
| Unmitigated Amber/Red | mitigation_summary=null, requires_legal_review=false | "no" |
| Generic citation | regulation = "applicable regulations" | "no" |
| ID gap | CON-01 then CON-03, no CON-02 | "no" |
| Vague overall_status rationale | "some constraints need attention" | "no" |
| Downgraded severity | rationale describes a hard blocker, status="Green" | "no" |
| requires_legal_review overused | every single Amber/Red constraint flagged for legal review | "no" |
| Omitted Red constraint | overall_status rationale references a Red blocker with no matching CON-NN entry | "no" |

### Option 2: End-to-End Flow Testing (NeMo Guardrails SDK)

```python
from nemoguardrails import LLMRails, RailsConfig

config = RailsConfig.from_path("./gr-L1-regulatory-feasibility-quality-gate")
rails = LLMRails(config)

response = await rails.generate_async(
    messages=[{"role": "assistant", "content": "<clean, fully-mitigated resultant content>"}]
)
assert "blocked" not in response["content"].lower()
print("✅ Fully-mitigated resultant content passed")

response = await rails.generate_async(
    messages=[{"role": "assistant", "content": "<unmitigated Red constraint JSON>"}]
)
assert "blocked" in response["content"].lower()
print("✅ Unmitigated Red constraint blocked")
```
