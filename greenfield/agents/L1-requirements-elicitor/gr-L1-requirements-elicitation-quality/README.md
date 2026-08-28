# gr-L1-requirements-elicitation-quality

**Layer:** L1
**Triggers on:** post_execution (output rail) — fires when `L1-requirements-elicitor-evaluator` concludes
**On fail:** Retry once, then escalate to HITL
**Implementation:** LLM-driven (Colang), prompt-only mode
**Applies to:** `L1-requirements-elicitor-evaluator` only (`configured_agents`)

## What does it do?

`L1-requirements-elicitor-evaluator` independently re-derives
`L1-requirements-elicitor`'s checks and fixes what it can. This guardrail
fires at that point but validates a different thing: the **resultant**
`L1-requirements-elicitor` output — its own `items`
(`functional_requirements[]`, `compound_splits[]`), with the evaluator's
fixes resolved in — is what actually flows downstream to the NFR
classifier and PRD composer. This gate checks that content against the
Quality Gate checklist and rubric score thresholds below, independent of
what the evaluator's own bookkeeping (`final_decision`, `pass`) claims.

### Checklist

- [ ] Ids sequential from FR-001, no gaps, no duplicates
- [ ] Every FR cites exactly one `vision.md § {section}`
- [ ] No unqualified vague term in any statement
- [ ] Every statement singular — no compound "X and Y" behaviour
- [ ] "shall" used for mandatory capabilities, never "should"/"may"
- [ ] 2–3 concrete pass/fail acceptance criteria per FR, no new scope
- [ ] `depends_on` well-formed and resolvable within the FR set
- [ ] `priority` is High | Medium | Low
- [ ] Statements carried full and verbatim, never a gloss
- [ ] `compound_splits[]` internally consistent with `notes` and the FR set
- [ ] `confidence` + explanatory `reasoning` on every FR
- [ ] Nothing written to blob storage — JSON is the artifact of record
- [ ] `execution_summary` present as plain-text bullets, counts accurate
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
(`L1-requirements-elicitor`'s source data — `vision.md`, the Phase 0
approval record, or `kb-L1-requirements-quality-standard`) or a code
execution step. It can reliably judge:
- Internal consistency of the resultant output (every field populated,
  every rationale genuinely explanatory, no field silently blank)
- Whether the checklist/rubric conditions are met on their face

It CANNOT reliably judge, and does not attempt to check:
- Whether the cited `vision.md § {section}` actually exists, or actually
  supports the FR that cites it
- Whether the statement is genuinely **verbatim** from `vision.md`
- Coverage — whether every testable capability in `vision.md` produced an
  FR, or whether a capability `vision.md` never asked for was invented
- Whether a `priority` value matches `vision.md`'s Roadmap Outline
- Whether a recorded Product Lead `approval_comment` genuinely existed

If exact-match/lookup validation against external source data is
required, that needs either (a) `original_input` threaded into the
prompt as a second template variable, or (b) a Python-hybrid
implementation (`actions.py`) — both are out of scope for this skill.

## Required Agent-Description Additions

Because this gate cannot see `original_input`, the upstream agents must
self-report enough information in their own output for a prompt-only
checklist gate to judge reliably. Add the following three chunks to
`L1-requirements-elicitor` and `L1-requirements-elicitor-evaluator`'s own
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
  explicitly (e.g., "checked, no matching service found") — never let an
  unchecked field look identical to a checked-and-clear field.
- Do NOT conflate "not applicable" with "not checked" anywhere in the
  output.
```

**Chunk 2 — Anti-Hallucination & Grounding Requirement**
```
Anti-Hallucination & Grounding Requirement:
- Never reference an id (FR-NNN, or equivalent identifier) that is not
  actually present in the source input — never invent one.
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
gr-L1-requirements-elicitation-quality/
├── config.yml                                      # Rail configuration (this skill's output)
├── gr-L1-requirements-elicitation-quality.co       # LLM-only Colang flow (this skill's output)
└── README.md                                       # This file (this skill's output)
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
    "type": "requirements",
    "schema_version": "1.0",
    "items": {
      "functional_requirements": [
        {
          "id": "FR-001",
          "title": "Generate compliance report",
          "statement": "The system shall generate a compliance report covering all transactions within a user-selected date range.",
          "citation": "vision.md § Value Proposition",
          "acceptance_criteria": [
            "A report is produced for any valid date range up to 24 months",
            "Every transaction in the selected range appears exactly once"
          ],
          "depends_on": "None",
          "priority": "High",
          "confidence": 0.92,
          "reasoning": "Value Proposition names report generation as the core deliverable; scoped to one capability."
        },
        {
          "id": "FR-002",
          "title": "Export compliance report",
          "statement": "The system shall export a generated compliance report to PDF.",
          "citation": "vision.md § Value Proposition",
          "acceptance_criteria": [
            "Export produces a valid PDF of the generated report",
            "Export is unavailable until a report exists"
          ],
          "depends_on": "FR-001",
          "priority": "Medium",
          "notes": "Split from the compound 'generate and export' clause",
          "confidence": 0.9,
          "reasoning": "Export is independently testable from generation, so it was split rather than passed through."
        }
      ],
      "compound_splits": [
        {
          "source_clause_summary": "Generate and export a compliance report",
          "split_into": ["FR-001", "FR-002"]
        }
      ]
    },
    "execution_summary": "• 2 FRs produced\n• 1 compound clause split into FR-001/FR-002"
  }
}
```

Expected **"no"** (fails gates 3, 4, 10):

```json
{
  "status": "success",
  "content": {
    "type": "requirements",
    "schema_version": "1.0",
    "items": {
      "functional_requirements": [
        {
          "id": "FR-001",
          "title": "Reporting",
          "statement": "The system shall generate a user-friendly compliance report and export it to PDF quickly.",
          "citation": "vision.md § Value Proposition",
          "acceptance_criteria": ["Report looks good"],
          "depends_on": "None",
          "priority": "High",
          "confidence": 0.6,
          "reasoning": "Reporting is needed."
        }
      ],
      "compound_splits": [
        { "source_clause_summary": "Generate and export a report", "split_into": ["FR-004"] }
      ]
    },
    "execution_summary": "• 3 FRs produced"
  }
}
```

### Option 2: End-to-End Flow Testing (NeMo Guardrails SDK)

```python
from nemoguardrails import LLMRails, RailsConfig

config = RailsConfig.from_path("./gr-L1-requirements-elicitation-quality")
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