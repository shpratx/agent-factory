# gr-L1-nfr-classification-quality

**Layer:** L1
**Triggers on:** post_execution (output rail) — fires when `L1-requirements-nfr-classifier-evaluator` concludes
**On fail:** Retry once, then escalate to HITL
**Implementation:** LLM-driven (Colang), prompt-only mode
**Applies to:** `L1-requirements-nfr-classifier-evaluator` only (`configured_agents`)

## What does it do?

`L1-requirements-nfr-classifier-evaluator` independently re-derives
`L1-nfr-classifier`'s checks and fixes what it can. This guardrail fires
at that point but validates a different thing: the **resultant**
`L1-nfr-classifier` output — its own `items`
(`nfr_classifications[]`), with the evaluator's fixes resolved in — is
what actually flows downstream to the PRD composer. Because this agent
writes nothing to blob storage, that JSON *is* the artifact of record.
This gate checks that content against the Quality Gate checklist and
rubric score thresholds below, independent of what the evaluator's own
bookkeeping (`final_decision`, `pass`) claims.

### Checklist

- [ ] One entry per FR, well-formed ascending ids, no duplicates
- [ ] Every category drawn from the six-category taxonomy
- [ ] No category repeated within one FR
- [ ] Every boundary condition is a concrete number/rule or the exact
      literal "TBD — needs stakeholder input" — never a vague hedge
- [ ] Every non-TBD boundary condition carries a checkable source in an
      allowed citation form
- [ ] Every non-TBD boundary condition carries an explanatory rationale
- [ ] Every TBD carries source "—" and no rationale
- [ ] No six-category padding; only genuinely applicable categories
- [ ] Empty category sets state "No NFR categories apply" explicitly
- [ ] Boundary conditions are short atomic phrases, not narrative
- [ ] Coverage counts stated match the counts actually written
- [ ] Nothing written to blob storage
- [ ] `execution_summary` present as plain-text bullets with all
      required bullet topics
- [ ] Envelope fields correct (`content.type`, `schema_version`, `wf-` id)

### Rubric thresholds

| Dimension | Threshold |
|---|---|
| Faithfulness | ≥ 0.90 |
| Hallucination | ≤ 0.05 |
| Internal consistency | ≥ 0.90 |
| Relevance | ≥ 0.85 |
| Reasoning quality | ≥ 0.80 |

## Known Limitations (prompt-only mode)

This gate is LLM-driven and has no access to `original_input`
(`L1-nfr-classifier`'s source data — the evaluated requirements set,
`regulatory-feasibility.md`, `kb-L1-nfr-classification-taxonomy`,
`kb-L1-enterprise-architecture`, `kb-L1-enterprise-security`) or a code
execution step. It can reliably judge:
- Internal consistency of the resultant output (every field populated,
  every rationale genuinely explanatory, no field silently blank)
- Whether the checklist/rubric conditions are met on their face

It CANNOT reliably judge, and does not attempt to check:
- Whether the id/order set exactly matches the upstream evaluated
  requirements set — i.e. whether an FR was dropped, added, or renumbered
- Whether a cited source (`regulatory-feasibility.md § X`,
  `kb-L1-enterprise-security § ESN`, `vision.md § X`) genuinely contains
  the number quoted against it
- Whether a TBD was actually resolvable — i.e. whether ES3/ES4 or the
  regulatory-feasibility constraints held an answer that was missed
- Whether a genuinely applicable category was wrongly skipped, beyond
  what the FR's own title/statement makes obvious

If exact-match/lookup validation against external source data is
required, that needs either (a) `original_input` threaded into the
prompt as a second template variable, or (b) a Python-hybrid
implementation (`actions.py`) — both are out of scope for this skill.

## Required Agent-Description Additions

Because this gate cannot see `original_input`, the upstream agents must
self-report enough information in their own output for a prompt-only
checklist gate to judge reliably. Add the following three chunks to
`L1-nfr-classifier` and `L1-requirements-nfr-classifier-evaluator`'s own
Description/Instructions field (all agents in this system share the same
description pattern — add these under the existing `Don'ts:` /
`Reflection:` sections):

**Chunk 1 — Explicit-Statement Requirement**
```
Explicit-Statement Requirement (for downstream quality gates):
- If a source input is genuinely empty, state this explicitly in the
  output (e.g., "empty — no parent enterprise") — never leave the field
  blank or silently omit it.
- If a check was genuinely run and found nothing relevant, state that
  explicitly (e.g., "checked regulatory-feasibility.md and
  kb-L1-enterprise-security, no matching boundary found") — never let an
  unchecked field look identical to a checked-and-clear field.
- Do NOT conflate "not applicable" with "not checked" anywhere in the
  output.
```

**Chunk 2 — Anti-Hallucination & Grounding Requirement**
```
Anti-Hallucination & Grounding Requirement:
- Never reference an id (FR-NNN, § section, or equivalent identifier)
  that is not actually present in the source input — never invent one.
- Every rationale must explain the decision (why), not merely restate
  the finding (what) — a rationale that just repeats the field it
  justifies is a failure.
- Any mismatch between two source-of-truth systems must be flagged as a
  finding, never silently reconciled by picking one source.
```

**Chunk 3 — Legitimate-Refusal Status Requirement**
```
Legitimate-Refusal Status Requirement:
- If upstream input is invalid or insufficient to proceed, set
  status: "failed" with an explicit, named reason (e.g.,
  "INSUFFICIENT_CONTEXT") — do not attempt to proceed or partially
  fabricate output.
- Downstream quality gates treat a correctly-labeled failed status as a
  legitimate outcome, not a defect — do not disguise a refusal as a
  low-confidence success.
```

## File Structure

```
gr-L1-nfr-classification-quality/
├── config.yml                                 # Rail configuration (this skill's output)
├── gr-L1-nfr-classification-quality.co        # LLM-only Colang flow (this skill's output)
└── README.md                                  # This file (this skill's output)
```

**Not produced by this skill / not in scope:** `actions.py`, `spec.yaml`,
Python-hybrid Colang flow. If a hybrid implementation is needed later,
build it as a separate, explicit step — do not assume this skill's
output covers it.

## Testing

### Option 1: Prompt-Based Testing (LLM Judgement Only)

Expected **"yes"** (passes):

```json
{
  "status": "success",
  "content": {
    "type": "nfr_classification",
    "schema_version": "1.0",
    "items": {
      "nfr_classifications": [
        {
          "id": "FR-001",
          "title": "Generate compliance report",
          "boundary_conditions": [
            {
              "category": "Performance",
              "boundary_condition": "p95 report generation under 5 seconds for a 12-month range",
              "rationale": "The North-Star Metric ties adoption to sub-5s report turnaround",
              "source": "vision.md § North-Star Metrics"
            },
            {
              "category": "Compliance",
              "boundary_condition": "Retain generated reports for 7 years",
              "rationale": "Retention period is fixed by the cited regulatory constraint",
              "source": "regulatory-feasibility.md § Retention"
            },
            {
              "category": "Scalability",
              "boundary_condition": "TBD — needs stakeholder input",
              "source": "—"
            }
          ],
          "confidence": 0.88,
          "reasoning": "3 categories applied; concurrency ceiling unstated in requirements, vision, regulatory-feasibility and kb-L1-enterprise-security, so left TBD."
        },
        {
          "id": "FR-002",
          "title": "Export compliance report",
          "boundary_conditions": [],
          "confidence": 0.8,
          "reasoning": "No NFR categories apply — export inherits the generation boundaries and introduces no independent constraint."
        }
      ]
    },
    "execution_summary": "• 2 FRs classified, 3 boundary conditions defined, 1 TBD\n• Compliance resolved via regulatory-feasibility.md § Retention"
  }
}
```

Expected **"no"** (fails gates 5, 8, 9):

```json
{
  "status": "success",
  "content": {
    "type": "nfr_classification",
    "schema_version": "1.0",
    "items": {
      "nfr_classifications": [
        {
          "id": "FR-001",
          "title": "Generate compliance report",
          "boundary_conditions": [
            { "category": "Performance", "boundary_condition": "Under 2 seconds", "rationale": "Fast is better", "source": "—" },
            { "category": "Security", "boundary_condition": "Secure by design", "rationale": "Security matters", "source": "—" },
            { "category": "Scalability", "boundary_condition": "Scales as needed", "rationale": "Growth expected", "source": "—" },
            { "category": "Availability", "boundary_condition": "Highly available", "rationale": "Uptime matters", "source": "—" },
            { "category": "Compliance", "boundary_condition": "Compliant", "rationale": "Regulated sector", "source": "—" },
            { "category": "Usability", "boundary_condition": "Intuitive UI", "rationale": "Users like it", "source": "—" }
          ],
          "confidence": 0.95,
          "reasoning": "All categories classified."
        },
        {
          "id": "FR-002",
          "title": "Export compliance report",
          "boundary_conditions": [],
          "confidence": 0.9,
          "reasoning": "Nothing here."
        }
      ]
    },
    "execution_summary": "• 2 FRs classified, 8 boundary conditions defined, 0 TBD"
  }
}
```

### Option 2: End-to-End Flow Testing (NeMo Guardrails SDK)

```python
from nemoguardrails import LLMRails, RailsConfig

config = RailsConfig.from_path("./gr-L1-nfr-classification-quality")
rails = LLMRails(config)

response = await rails.generate_async(
    messages=[{"role": "assistant", "content": "<clean resultant JSON>"}]
)
assert "blocked" not in response["content"].lower()

response = await rails.generate_async(
    messages=[{"role": "assistant", "content": "<invalid resultant JSON>"}]
)
assert "blocked" in response["content"].lower()
```