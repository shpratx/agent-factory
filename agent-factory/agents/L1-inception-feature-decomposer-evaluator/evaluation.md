# Evaluation Criteria — L1-inception-feature-decomposer-evaluator

This evaluator inherits **all** quality gates and reflection checklist items from `L1-inception-feature-decomposer`'s own `evaluation.md` (reproduced in Section A below), since it must be able to independently re-derive what correct Features look like. Section B adds the **8 mandatory named gates** required to score a candidate Features output, plus the correction and decision process unique to this evaluator agent, using the AgentOutput v2 envelope (`agent_id`, `status`, `content.evaluation`).

---

## SECTION A — Inherited Core Feature Decomposer Criteria (from L1-inception-feature-decomposer/evaluation.md)

### A.1 Quality Gates (must pass)

| Criterion | Threshold | Method |
|-----------|-----------|--------|
| Every Feature has a non-null `prd_reference` (inherited from parent Epic) | 100% | Automated: schema `required` check |
| Every Feature has `parent_epic_id` and `source_pillar` populated | 100% | Automated: schema `required` check |
| Features per pillar | 1-4 | Automated: grouping check by `source_pillar` |
| `feature_id` format | `F-\d{2}\.\d+` matching parent epic number | Automated: regex + cross-check |
| Feature title length | 4-8 words | Automated: word-count regex |
| `acceptance_criteria` count | 3-6 | Automated: array length check |
| No Story-level detail (test scripts, UI wireframes, API/schema design, sprint/story points) | 0 occurrences | LLM-judge |
| Every Feature has `mvp_classification` and a specific `mvp_rationale` | 100% | Automated + LLM-judge |
| No Foundational Feature depends on an Incremental Feature | 0 occurrences | Automated: cross-check |
| `content.artifacts[].storage.location` present and non-fabricated | 100% | Automated + LLM-judge |
| Output validates against L1-inception-feature-decomposer's Feature schema | 100% | Automated: JSON Schema validation |

### A.2 Reflection Checklist (applied to the candidate output being evaluated)

- [ ] Every Feature has `parent_epic_id`, `source_pillar`, and a `prd_reference` identical to its parent Epic's `prd_reference`
- [ ] Each pillar decomposed into 1-4 Features
- [ ] `feature_id`s are sequential per epic and match `F-{epic-number}.{sequence}` with the correct epic number
- [ ] No test scripts, UI wireframes, API/schema design, or sprint/story-point detail appears anywhere
- [ ] `out_of_scope`/`constraints` per Feature are inherited only where directly relevant
- [ ] `acceptance_criteria` are outcome-level, 3-6 bullets, and each traces to specific Epic content
- [ ] Every Feature has `mvp_classification` determined via the Foundational Classification Test, with a specific, non-generic `mvp_rationale`
- [ ] No Foundational Feature lists a `dependencies` entry pointing to an Incremental Feature
- [ ] Features are not uniformly all-Foundational or all-Incremental without genuine justification
- [ ] Every item has a complete `metadata` block
- [ ] blob-storage-writer was called correctly, including on INSUFFICIENT_CONTEXT

---

## SECTION B — Evaluator-Specific Gates (mandatory, 8 dimensions)

Every evaluation MUST score all 8 of the following named gates, each 0.0-1.0, in `content.evaluation.scores`. Every gate scoring below 1.0 MUST have at least one corresponding `fail` finding in `content.evaluation.findings[]` (`gate`, `status`, `detail`).

| # | Gate name | What Is Assessed | Fail Condition |
|---|-----------|-------------------|-----------------|
| 1 | `faithfulness` | Every Feature field traces to an actual phrase/field in the parent Epic | Any field cannot be traced to the parent Epic |
| 2 | `completeness` | Every `macro_feature_pillars` entry in the parent Epic(s) decomposed into at least 1 Feature | A pillar present in the Epic has zero corresponding Features |
| 3 | `schema_compliance` | Candidate validates against `L1-inception-feature-decomposer`'s Feature schema exactly | Any schema validation failure |
| 4 | `regulatory_accuracy` | Inherited `out_of_scope`/`constraints` text matches the parent Epic verbatim and is directly relevant to the Feature's slice | Constraint/out-of-scope text misquoted, or blanket-copied without relevance |
| 5 | `epic_traceability` | `feature_id` epic-number matches `parent_epic_id`; every `prd_reference` matches the parent Epic's `prd_reference` exactly | Any `feature_id`/`parent_epic_id` mismatch or `prd_reference` drift |
| 6 | `delivery_sequencing` | `dependencies[]` reference real sibling `feature_id`s and are evidence-grounded; `mvp_classification` correctly applies the Foundational Classification Test; no Foundational-depends-on-Incremental violations | A `dependencies` entry points to a non-existent Feature, is unsupported by Epic evidence, or an `mvp_classification` contradicts the Feature's actual role |
| 7 | `user_story_quality` | Feature titles/descriptions stay at capability altitude, 4-8 words, no Story/technical-task leakage | Content present that belongs at the Story/technical-design layer |
| 8 | `acceptance_criteria_quality` | 3-6 outcome-level, testable, source-grounded acceptance criteria per Feature | Acceptance criteria read like test scripts, are generic, or are fabricated |

### B.1 Correction Process (mandatory)

For every `fail` finding:
1. Assign a sequential `id` (FND-01, FND-02, ...) in `findings[]`, with `gate`, `status: "fail"`, and `detail` explaining the issue.
2. Determine whether it CAN be safely corrected using only the parent Epic or already-present Feature content (e.g., correcting a mis-copied `prd_reference`, re-wording an over-long title, removing an unsupported dependency, reclassifying `mvp_classification` using evident Epic content, splitting an overloaded Feature).
3. If fixable: apply the correction directly into the corrected `content.items`, and record it in `fixes_applied[]` with a sequential `id` (FIX-01, ...), the `finding_id` it resolves, `description`, `before`, `after`, `reasoning`.
4. If NOT safely fixable (would require inventing information not present in the parent Epic): do NOT guess. Leave the finding unresolved (no matching `fixes_applied` entry) — this drives `final_decision` toward `"escalate_to_hitl"`.
5. `content.items` always reflects every safe fix applied, even if some other findings remain unresolved.

### B.2 Final Decision Logic

| `final_decision` | Condition |
|----------|-----------|
| `"approved"` | All 8 gates score 1.0 and zero findings failed. `content.items` is identical to the candidate. |
| `"fixed_and_approved"` | One or more findings failed, and ALL were fixed. `content.items` differs from the candidate and now passes all gates. |
| `"escalate_to_hitl"` | One or more failed findings could not be safely fixed (required source information is unavailable, e.g. the parent Epic itself is missing/unreadable). `content.items` still contains all safe fixes applied, but at least one finding remains unresolved. |

> **Rule:** `"escalate_to_hitl"` is never used simply because minor, cosmetic issues exist — only when a genuinely blocking, unfixable gap remains.

`overall_score` = average of the 8 gate scores * 10, rounded to 2 decimals. `pass` = true unless `final_decision == "escalate_to_hitl"`.

### B.3 Evaluator Reflection Checklist

- [ ] All 8 gates are present in `scores`, each with a corresponding entry logic in `findings[]` if below 1.0
- [ ] Every failed finding has a unique sequential `id`, correct `gate` back-reference, and accurate `detail`
- [ ] Every fixed finding has a corresponding entry in `fixes_applied[]` with accurate `before`/`after`/`reasoning`
- [ ] Every unresolved finding correctly drives `final_decision` toward `escalate_to_hitl` — never silently dropped
- [ ] `content.items` validates against `L1-inception-feature-decomposer`'s Feature schema
- [ ] `final_decision` matches the logic in B.2 exactly
- [ ] No new hallucinated content was introduced while fixing
- [ ] Every Feature's `feature_id` epic-number matches its `parent_epic_id`
- [ ] `content.artifacts[]` references `L1-features.json` (the same filename the core agent wrote, overwritten in place) with a non-fabricated `storage.location`
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
