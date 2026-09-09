# Evaluation Criteria — L1-inception-epics-creator-evaluator

This evaluator inherits **all** quality gates and reflection checklist items from `L1-inception-epics-creator`'s own `evaluation.md` (reproduced in Section A below), since it must be able to independently re-derive what a correct Epic looks like. Section B adds the **8 mandatory named gates** required to score a candidate Epics output, plus the correction and decision process unique to this evaluator agent, using the AgentOutput v2 envelope (`agent_id`, `status`, `content.evaluation`).

---

## SECTION A — Inherited Core Epics Creator Criteria (from L1-inception-epics-creator/evaluation.md)

### A.1 Quality Gates (must pass)

| Criterion | Threshold | Method |
|-----------|-----------|--------|
| Every Epic has a non-null `prd_reference.file_path` | 100% | Automated: schema `required` check on `prd_reference` |
| Macro feature pillars per Epic | 3–6 | Automated: array length check |
| Out of Scope bullets per Epic | 1–6 | Automated: array length check |
| Epic title length | 3–5 words | Automated: word-count regex on `title` |
| `epic_id` format | `EP-\d{2}` | Automated: regex validation |
| Risks contain only Critical Compliance categories | 100% | Automated: enum check on `category` |
| No forbidden PRD sections present in Epic fields | 0 occurrences | Automated + LLM-judge |
| `reference_links` non-empty | ≥1 | Automated: array length check |
| No Feature/Story/task-level decomposition inside `macro_feature_pillars` | 0 occurrences | LLM-judge |
| `target_date` is verbatim-or-null | 100% | LLM-judge |
| Multi-Epic split correctness (kb-epics-best-practices §2.5) | 100% | LLM-judge |
| Output validates against L1-inception-epics-creator's Epic schema | 100% | Automated: JSON Schema validation |
| `content.artifacts[].storage.location` present and non-fabricated | 100% | Automated + LLM-judge |

### A.2 Reflection Checklist (applied to the candidate output being evaluated)

- [ ] Every Epic has `prd_reference.file` and `prd_reference.file_path` populated
- [ ] Macro feature pillars count is between 3 and 6 per Epic
- [ ] No Traceability Matrix, Compound Requirement Split, Open Questions, Assumptions, or Glossary content appears anywhere
- [ ] Risks section contains only FDA/SQF/HACCP/USDA/recall/plant-shutdown-critical items
- [ ] Out of Scope has 1–6 condensed bullets
- [ ] Constraints are strategic-altitude only
- [ ] Title is 3–5 words, Title Case, capability-focused
- [ ] `reference_links` includes at least a Full PRD link
- [ ] `epic_id`s are sequential (EP-01, EP-02, ...)
- [ ] Every item has a complete `metadata` block
- [ ] `macro_feature_pillars` contain capability phrases only — no Feature/Story/task-level decomposition
- [ ] Every `target_date` is verbatim or `null`
- [ ] PRD-to-Epic cardinality followed kb-epics-best-practices §2.5
- [ ] blob-storage-writer was called correctly, including on INSUFFICIENT_CONTEXT

---

## SECTION B — Evaluator-Specific Gates (mandatory, 8 dimensions)

Every evaluation MUST score all 8 of the following named gates, each 0.0-1.0, in `content.evaluation.scores`. Every gate scoring below 1.0 MUST have at least one corresponding `fail` finding in `content.evaluation.findings[]` (`gate`, `status`, `detail`).

| # | Gate name | What Is Assessed | Fail Condition |
|---|-----------|-------------------|-----------------|
| 1 | `faithfulness` | Every Epic field traces to an actual phrase/section in the source PRD (`L1-prd.md`, or the Epic's own `prd_reference.file_path` if it differs) | Any field cannot be traced to the PRD |
| 2 | `completeness` | All PRD content that should have produced an Epic field was captured — no qualifying macro-capability or Critical-Compliance risk is missing | A qualifying pillar/risk/out-of-scope item present in the PRD is absent from the Epic |
| 3 | `schema_compliance` | Candidate validates against `L1-inception-epics-creator`'s Epic schema exactly (required fields, enums, patterns, array bounds) | Any schema validation failure |
| 4 | `regulatory_accuracy` | Risk `category`/`severity`/`target_date` and constraint text are factually correct copies/summaries of the PRD | A `target_date`, risk `category`, or `severity` misrepresents the PRD text |
| 5 | `prd_traceability` | Every Epic's `prd_reference` resolves to the actual PRD location it was generated from | `prd_reference` missing, fabricated, or pointing to the wrong file |
| 6 | `cardinality_compliance` | Correct number of Epics for the PRD's initiative structure per kb-epics-best-practices §2.5 (1 Epic per cohesive capability; multiple only for genuinely distinct initiatives) | Epic count doesn't match the PRD's actual initiative structure |
| 7 | `title_and_altitude_quality` | Title 3-5 words Title Case; pillars 5-8 words capability-level; no leaked Feature/Story/technical detail; formatting rules (paragraph length, bullet nesting) | Any altitude/formatting rule violated |
| 8 | `risk_filtering_quality` | Only Critical Compliance Threshold risks retained; no general delivery/engineering/training/vendor risks leaked in | Any non-qualifying risk included, or a qualifying risk omitted |

### B.1 Correction Process (mandatory)

For every `fail` finding:
1. Assign a sequential `id` (FND-01, FND-02, ...) in `findings[]`, with `gate`, `status: "fail"`, and `detail` explaining the issue.
2. Determine whether it CAN be safely corrected using only the source PRD or already-present Epic content (e.g., re-extracting a mis-copied date, re-wording an over-long title using the PRD's own language, removing a hallucinated pillar, moving leaked Feature/Story detail out of a pillar).
3. If fixable: apply the correction directly into the corrected `content.items`, and record it in `fixes_applied[]` with a sequential `id` (FIX-01, ...), the `finding_id` it resolves, `description`, `before`, `after`, `reasoning`.
4. If NOT safely fixable (would require inventing information not present in the PRD): do NOT guess. Leave the finding unresolved (no matching `fixes_applied` entry) — this drives `final_decision` toward `"escalate_to_hitl"`.
5. `content.items` always reflects every safe fix applied, even if some other findings remain unresolved.

### B.2 Final Decision Logic

| `final_decision` | Condition |
|----------|-----------|
| `"approved"` | All 8 gates score 1.0 and zero findings failed. `content.items` is identical to the candidate. |
| `"fixed_and_approved"` | One or more findings failed, and ALL were fixed. `content.items` differs from the candidate and now passes all gates. |
| `"escalate_to_hitl"` | One or more failed findings could not be safely fixed (required source information is unavailable). `content.items` still contains all safe fixes applied, but at least one finding remains unresolved. |

> **Rule:** `"escalate_to_hitl"` is never used simply because minor, cosmetic issues exist — only when a genuinely blocking, unfixable gap remains. Minor fixable issues alone always resolve to `"fixed_and_approved"`.

`overall_score` = average of the 8 gate scores * 10, rounded to 2 decimals. `pass` = true unless `final_decision == "escalate_to_hitl"`.

### B.3 Evaluator Reflection Checklist

- [ ] All 8 gates are present in `scores`, each with a corresponding entry logic in `findings[]` if below 1.0
- [ ] Every failed finding has a unique sequential `id`, correct `gate` back-reference, and accurate `detail`
- [ ] Every fixed finding has a corresponding entry in `fixes_applied[]` with accurate `before`/`after`/`reasoning`
- [ ] Every unresolved finding correctly drives `final_decision` toward `escalate_to_hitl` — never silently dropped
- [ ] `content.items` validates against `L1-inception-epics-creator`'s Epic schema
- [ ] `final_decision` matches the logic in B.2 exactly
- [ ] No new hallucinated content was introduced while fixing
- [ ] `content.artifacts[]` references `L1-epics.json` (the same filename the core agent wrote, overwritten in place) with a non-fabricated `storage.location`
- [ ] `execution_summary` is plain text bullets, not JSON

### B.4 Evaluator Reflection Process (mandatory)

1. **Evaluate** candidate output against all 8 gates and Section A's checklist
2. **Log** `[REFLECTING] Checking evaluation against evaluation.md Section B criteria`
3. **Check** every item in B.3's checklist
4. **Identify** any missed findings, incorrect fixable/unfixable calls, or decision-logic errors
5. **Log** each finding: `[REFLECTING] Found: <description>`
6. **Fix** the evaluation itself — amend scores, findings, fixes, or decision as needed
7. **Log** each resolution: `[REFLECTING] Resolved: <what was fixed>`
8. **Deliver** only the final, corrected evaluation output

Reflection findings appear in `execution_summary` but interim output is never shown.
