# gr-L1-prd-composition-quality

**Layer:** L1
**Triggers on:** post_execution (output rail) — fires when `L1-requirements-prd-composer-evaluator` concludes
**On fail:** Retry once, then escalate to HITL
**Implementation:** LLM-driven (Colang), prompt-only mode
**Applies to:** `L1-requirements-prd-composer-evaluator` only (`configured_agents`)

## What does it do?

`L1-requirements-prd-composer-evaluator` independently re-derives
`L1-requirements-prd-composer`'s checks and fixes what it can. This
guardrail fires at that point but validates a different thing: the
**resultant** `L1-requirements-prd-composer` output — its own `items`
(`requirements[]`, `assumptions[]`, `constraints[]`, `risks[]`,
`open_questions[]`, `compound_splits[]`, `executive_summary`) plus its
`artifacts[]` pointer to `prd.md`, with the evaluator's fixes resolved
in — is what actually flows downstream to
`L1-planning-impact-assessor` and `L1-planning-dependency-mapper`. This
gate checks that content against the Quality Gate checklist and rubric
score thresholds below, independent of what the evaluator's own
bookkeeping (`final_decision`, `pass`) claims.

### Checklist

- [ ] `requirements[]` populated, ids well-formed, ascending, unique
- [ ] Every statement carried full — never a condensed gloss
- [ ] Every FR carries an `nfrs` table, empty only with an explicit
      "No NFR categories apply"
- [ ] Every FR carries MVP Yes/No **with a stated traceable basis**
- [ ] Every NFR boundary condition carries its own MVP tag; overrides
      to No carry an explicit later-phase basis
- [ ] Every assumption/constraint/risk has ASSUM-/CON-/RISK-NNN id
- [ ] Every assumption/constraint/risk tagged to FR(s) or "program-level"
      and traceable to vision.md or a specific FR
- [ ] No success metrics introduced anywhere
- [ ] Condensed fields ≤ 150 chars; no narrative hidden in `summary`
- [ ] Every TBD boundary condition rolled into `open_questions` and
      every "tbd" open question maps back to a real TBD row
- [ ] `compound_splits[]` ids resolve within `requirements[]`
- [ ] `artifacts[]` carries prd.md with a real `blob_storage_url`
- [ ] Executive summary introduces no claim absent from other items
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
(`L1-requirements-prd-composer`'s source data — the evaluated
requirements set, the evaluated NFR set, or `vision.md`) or a code
execution step. It also cannot read the `prd.md` body itself, which
lives in blob storage; only the `items` and `artifacts` in the response
are visible. It can reliably judge:
- Internal consistency of the resultant output (every field populated,
  every rationale genuinely explanatory, no field silently blank)
- Whether the checklist/rubric conditions are met on their face

It CANNOT reliably judge, and does not attempt to check:
- **Drop detection** — whether every FR in the evaluated requirements
  set and every boundary condition in the evaluated NFR set actually
  survived composition (the headline "zero requirements dropped" rule
  requires an external count comparison)
- Whether statements, citations, and boundary conditions are genuinely
  **verbatim** relative to their upstream sources, or were silently
  re-worded or re-classified
- Whether every still-open `vision.md` risk was carried forward, and
  whether an assumption/constraint/risk genuinely originates in
  `vision.md`
- Whether an MVP tag's stated basis is *truthful* to `vision.md`'s
  Roadmap Outline — only that a basis is stated
- Whether the Out of Scope, Glossary, and Traceability Matrix sections
  inside the saved `prd.md` document are correct or even present
- Whether the returned `blob_storage_url` resolves to a real object

If exact-match/lookup validation against external source data is
required, that needs either (a) `original_input` threaded into the
prompt as a second template variable, or (b) a Python-hybrid
implementation (`actions.py`) — both are out of scope for this skill.

## Required Agent-Description Additions

Because this gate cannot see `original_input`, the upstream agents must
self-report enough information in their own output for a prompt-only
checklist gate to judge reliably. Add the following three chunks to
`L1-requirements-prd-composer` and
`L1-requirements-prd-composer-evaluator`'s own Description/Instructions
field (all agents in this system share the same description pattern —
add these under the existing `Don'ts:` / `Reflection:` sections):

**Chunk 1 — Explicit-Statement Requirement**
```
Explicit-Statement Requirement (for downstream quality gates):
- If a source input is genuinely empty, state this explicitly in the
  output (e.g., "No NFR categories apply", "None identified") — never
  leave the field blank or silently omit it.
- If a check was genuinely run and found nothing relevant, state that
  explicitly (e.g., "checked vision.md Roadmap Outline, silent on this
  FR — MVP traced to Priority field") — never let an unchecked field
  look identical to a checked-and-clear field.
- Do NOT conflate "not applicable" with "not checked" anywhere in the
  output.
```

**Chunk 2 — Anti-Hallucination & Grounding Requirement**
```
Anti-Hallucination & Grounding Requirement:
- Never reference an id (FR-NNN, ASSUM-NNN, CON-NNN, RISK-NNN, or
  equivalent identifier) that is not actually present in the source
  input — never invent one.
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
gr-L1-prd-composition-quality/
├── config.yml                              # Rail configuration (this skill's output)
├── gr-L1-prd-composition-quality.co        # LLM-only Colang flow (this skill's output)
└── README.md                               # This file (this skill's output)
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
    "type": "prd",
    "schema_version": "1.0",
    "items": {
      "executive_summary": {
        "summary": "Compliance reporting platform for regulated mid-market lenders; MVP covers report generation and PDF export.",
        "confidence": 0.9,
        "reasoning": "Written last; every claim restates FR-001, FR-002 and the assumptions below."
      },
      "compound_splits": [
        { "source_clause_summary": "Generate and export a compliance report", "split_into": ["FR-001", "FR-002"] }
      ],
      "assumptions": [
        {
          "short_title": "ASSUM-001 Source data completeness",
          "summary": "Transaction feed is assumed complete at report time; vision.md never validated feed latency.",
          "underlies_or_affects": ["FR-001"],
          "confidence": 0.85,
          "reasoning": "vision.md § Problem implies completeness but records no validation."
        }
      ],
      "constraints": [
        {
          "short_title": "CON-001 Seven-year retention",
          "summary": "Reports must be retained 7 years, fixing storage design.",
          "underlies_or_affects": ["FR-001"],
          "confidence": 0.95,
          "reasoning": "vision.md § Regulatory Posture states the retention obligation."
        }
      ],
      "risks": [
        {
          "short_title": "RISK-001 Regulatory change mid-build",
          "summary": "Reporting schema may change before launch, invalidating fixed templates.",
          "underlies_or_affects": "program-level",
          "confidence": 0.8,
          "reasoning": "Carried verbatim from vision.md § Open Risks; still open."
        }
      ],
      "requirements": [
        {
          "id": "FR-001",
          "title": "Generate compliance report",
          "statement": "The system shall generate a compliance report covering all transactions within a user-selected date range.",
          "citation": "vision.md § Value Proposition",
          "mvp": "Yes",
          "mvp_basis": "vision.md § Roadmap Outline Phase 1 scopes report generation",
          "nfrs": [
            { "category": "Performance", "boundary_condition": "p95 report generation under 5 seconds for a 12-month range", "source": "vision.md § North-Star Metrics", "mvp": "Yes", "mvp_basis": "inherits FR-001" },
            { "category": "Scalability", "boundary_condition": "TBD — needs stakeholder input", "source": "—", "mvp": "Yes", "mvp_basis": "inherits FR-001" }
          ],
          "confidence": 0.92,
          "reasoning": "Carried verbatim; MVP traced to Roadmap Phase 1."
        },
        {
          "id": "FR-002",
          "title": "Export compliance report",
          "statement": "The system shall export a generated compliance report to PDF.",
          "citation": "vision.md § Value Proposition",
          "mvp": "Yes",
          "mvp_basis": "Priority High in evaluated requirements; Roadmap Outline silent",
          "nfrs": [],
          "nfr_note": "No NFR categories apply",
          "confidence": 0.88,
          "reasoning": "Empty NFR table carried forward explicitly rather than omitted."
        }
      ],
      "open_questions": [
        { "type": "tbd", "fr_id": "FR-001", "category": "Scalability", "summary": "Concurrency ceiling unspecified — needs stakeholder input" }
      ]
    },
    "artifacts": [
      {
        "id": "artifact-001",
        "type": "document",
        "name": "prd.md",
        "format": "markdown",
        "storage": { "provider": "blob_storage", "location": "https://blob.example.net/wf-8c21/prd.md" },
        "description": "Composed PRD for Phase 1",
        "produced_by": "L1-requirements-prd-composer"
      }
    ],
    "execution_summary": "• 2 FRs composed, 1 assumption, 1 constraint, 1 risk\n• 1 TBD rolled into open questions"
  }
}
```

Expected **"no"** (fails gates 4, 6, 11, 14):

```json
{
  "status": "success",
  "content": {
    "type": "prd",
    "schema_version": "1.0",
    "items": {
      "executive_summary": { "summary": "A best-in-class platform targeting 40% market share in year one.", "confidence": 0.9, "reasoning": "Summary." },
      "compound_splits": [],
      "assumptions": [
        { "short_title": "Data is fine", "summary": "Data will be fine.", "underlies_or_affects": [], "confidence": 0.5, "reasoning": "Assumed." }
      ],
      "constraints": [],
      "risks": [],
      "requirements": [
        {
          "id": "FR-001",
          "title": "Generate compliance report",
          "statement": "The system shall generate a compliance report...",
          "citation": "vision.md § Value Proposition",
          "nfrs": [
            { "category": "Scalability", "boundary_condition": "TBD — needs stakeholder input", "source": "—" }
          ],
          "confidence": 0.7,
          "reasoning": "Composed."
        }
      ],
      "open_questions": []
    },
    "artifacts": [
      {
        "id": "artifact-",
        "type": "document",
        "name": "prd.md",
        "format": "markdown",
        "storage": { "provider": "blob_storage", "location": "<blob_storage_url>" },
        "description": "PRD",
        "produced_by": "L1-requirements-prd-composer"
      }
    ],
    "execution_summary": "• 3 FRs composed"
  }
}
```

### Option 2: End-to-End Flow Testing (NeMo Guardrails SDK)

```python
from nemoguardrails import LLMRails, RailsConfig

config = RailsConfig.from_path("./gr-L1-prd-composition-quality")
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