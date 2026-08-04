# gr-L1-market-analysis-quality-gate

**Layer:** L1
**Triggers on:** post_execution (output rail) — fires when `L1-vision-market-analyzer-evaluator` concludes
**On fail:** Retry once, then escalate to HITL
**Implementation:** LLM-driven (Colang) — Python actions preserved for hybrid mode
**Applies to:** `L1-vision-market-analyzer-evaluator` only (`configured_agents`)

## What does it do?

`L1-vision-market-analyzer-evaluator` scores `L1-vision-market-analyzer`'s
draft output against `L1-vision-market-analyzer/evaluation.md` — with an
exhaustive citation check as its primary job — and fixes what it can. This
guardrail fires at that point but validates a different thing: the
**resultant** `L1-vision-market-analyzer` output — its own `items`, with
the evaluator's `fixes_applied` resolved in — is what actually flows to
`L1-vision-statement-generator`. This gate checks THAT content:

1. **Output schema validation** — does the resultant content conform to
   `L1-vision-market-analyzer/output_schema.json` (not the evaluator's own
   output shape)?
2. **Capability checklist / rubric adherence** — does the resultant
   content actually satisfy `L1-vision-market-analyzer/evaluation.md`'s
   Quality Gates (100% citation coverage above all else, sequential IDs,
   SWOT items naming a specific entry, an honest data-sufficiency verdict)?

This is NOT a check on the evaluator's own scores/findings/final_decision
— it's a check on whether evaluation, having concluded, actually produced
schema-valid, citation-complete content ready for the next pipeline step.

**Why it matters:** the evaluator's entire reason for existing is to catch
a missing citation the generator's own self-check overlooked. If the
evaluator reports `fixed_and_approved` but a competitor entry is still
missing its `retrieved_date`, or a fix left a citation's `source_reference`
empty, the exact gap this evaluator exists to close would reach
`L1-vision-statement-generator` anyway. This gate is independent of the
evaluator's own self-report.

### Rules

| # | Rule | Category | Action | Severity |
|---|------|----------|--------|----------|
| 1 | schema-compliance | Schema | block | critical |
| 2 | ids-sequential-no-gaps | Rubric adherence | block | high |
| 3 | citation-completeness-100pct | Rubric adherence | block | critical |
| 4 | swot-reasoning-specific | Rubric adherence | flag | high |
| 5 | data-sufficiency-honest | Rubric adherence | flag | medium |

## How It Works

```
L1-vision-market-analyzer-evaluator concludes (scores, fixes, final_decision)
        ↓
┌────────────────────────────────────────────────────────────────────┐
│  MARKET-ANALYSIS QUALITY GATE (post_execution, fires on evaluator)  │
│                                                                      │
│  Reconstruct RESULTANT content: L1-vision-market-analyzer's items   │
│  with fixes_applied[].before→after resolved in                      │
│                                                                      │
│  DETERMINISTIC (actions.py):                                        │
│  1. Schema: summaries/confidence/reasoning present + within length? │
│  2. CM-NN / ST/WK/OP/TH-NN ids sequential, no gaps/duplicates?      │
│  3. EVERY competitor has BOTH source_reference AND retrieved_date? │
│                                                                      │
│  Any ✗ → BLOCK, retry once, then escalate_to_hitl                    │
│                                                                      │
│  SEMANTIC (self_check_output, LLM):                                  │
│  4. SWOT reasoning names a specific competitor/fact?                 │
│  5. data_sufficiency rationale genuinely honest, not padded?         │
│                                                                      │
│  Any ✗ → BLOCK, retry once, then escalate_to_hitl                    │
│                                                                      │
│  All ✓ → gate passes                                                 │
└────────────────────────────────────────────────────────────────────┘
        ↓
Resultant market-analysis content flows to L1-vision-statement-generator
```

## File Structure

```
gr-L1-market-analysis-quality-gate/
├── config.yml                                # Rail configuration
├── prompts.yml                               # LLM evaluation prompt (5 checks)
├── gr-L1-market-analysis-quality-gate.co     # LLM-only Colang flow
├── market_analysis_quality_gate.co           # Python-hybrid Colang flow (calls actions.py)
├── actions.py                                # Deterministic Python (schema, ID sequencing, citation completeness)
├── spec.yaml                                 # Guardrail specification
└── README.md                                 # This file
```

**Two modes:**
- **LLM-only** (`gr-L1-market-analysis-quality-gate.co`): all 5 checks via `self_check_output`.
- **Python-hybrid** (`market_analysis_quality_gate.co`): the 3 deterministic checks (1, 2, 3) reconstruct the resultant content and validate it directly in `actions.py`; the LLM handles the 2 genuinely semantic checks (4, 5).

## Testing

### Option 1: Prompt-Based Testing (LLM Judgement Only)

**Valid resultant output (expected: "yes")** — every competitor cited, sequential ids:

```json
{
  "competitor_matrix": [
    {"id": "CM-01", "name": "Wholesaler A", "positioning_summary": "Volume-focused, low differentiation", "strengths_summary": "Scale, existing distribution", "weaknesses_summary": "No compliance documentation service", "citation": {"source_reference": "kb-L2-domain-market", "retrieved_date": "2026-07-15"}, "confidence": 0.85, "reasoning": "Named category example in the KB, cross-checked against search"}
  ],
  "swot": {
    "strengths": [{"id": "ST-01", "summary": "Compliance-first positioning vs CM-01's volume focus", "confidence": 0.8, "reasoning": "Derived directly from CM-01's weakness"}],
    "weaknesses": [], "opportunities": [], "threats": []
  },
  "data_sufficiency": {"status": "sufficient", "rationale_summary": "3 competitor categories reviewed via KB + search"}
}
```

**Invalid resultant output (expected: "no")** — CM-01 is missing `retrieved_date`, an incomplete citation even after evaluation concluded:

```json
{
  "competitor_matrix": [
    {"id": "CM-01", "name": "Wholesaler A", "positioning_summary": "...", "strengths_summary": "...", "weaknesses_summary": "...", "citation": {"source_reference": "kb-L2-domain-market"}, "confidence": 0.85, "reasoning": "..."}
  ],
  "swot": {"strengths": [], "weaknesses": [], "opportunities": [], "threats": []},
  "data_sufficiency": {"status": "sufficient", "rationale_summary": "..."}
}
```

### Test Cases Matrix

| Test | Mutation | Expected |
|------|----------|----------|
| Clean, fully-cited resultant content | None | "yes" |
| Missing retrieved_date | CM-01.citation has source_reference only | "no" |
| Missing source_reference | CM-02.citation has retrieved_date only | "no" |
| ID gap | CM-01 then CM-03, no CM-02 | "no" |
| Over-length summary | `strengths_summary` > 100 chars | "no" |
| Generic SWOT reasoning | `detail` = "competitive pressure exists" with no id | "no" |
| Padded "sufficient" verdict | data_sufficiency honesty questionable given thin matrix | "no" |

### Option 2: End-to-End Flow Testing (NeMo Guardrails SDK)

```python
from nemoguardrails import LLMRails, RailsConfig

config = RailsConfig.from_path("./gr-L1-market-analysis-quality-gate")
rails = LLMRails(config)

response = await rails.generate_async(
    messages=[{"role": "assistant", "content": "<clean, fully-cited resultant content>"}]
)
assert "blocked" not in response["content"].lower()
print("✅ Fully-cited resultant content passed")

response = await rails.generate_async(
    messages=[{"role": "assistant", "content": "<content missing a retrieved_date>"}]
)
assert "blocked" in response["content"].lower()
print("✅ Incomplete citation blocked")
```

### Option 3: Python Unit Testing (standalone actions.py)

```python
from actions import check_market_analysis_quality_gate

generator_output = json.dumps({"status": "success", "content": {"items": {
    "competitor_matrix": [{
        "id": "CM-01", "name": "Wholesaler A",
        "positioning_summary": "p", "strengths_summary": "s", "weaknesses_summary": "w",
        "citation": {"source_reference": "kb-L2-domain-market"},  # missing retrieved_date
        "confidence": 0.85, "reasoning": "r" * 25,
    }],
    "swot": {"strengths": [], "weaknesses": [], "opportunities": [], "threats": []},
    "data_sufficiency": {"status": "sufficient", "rationale_summary": "x"},
}}})

result = await check_market_analysis_quality_gate(output="{}", generator_output=generator_output)
assert result == True  # missing retrieved_date caught
```
