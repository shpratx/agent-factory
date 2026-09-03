# L1-inception-feature-decomposer-evaluator

## Purpose

This agent is the automated quality gate for `L1-inception-feature-decomposer`. It reads a candidate `L1-features.json`, its parent `L1-epics.json`, and the original `L1-prd.md` from blob storage, independently re-derives what correct Features should look like using the same SOP rules the core agent follows, scores the candidate against 8 mandatory gates, automatically corrects every safely-fixable issue, and overwrites `L1-features.json` in place with the corrected output plus a final decision (`approved`, `fixed_and_approved`, or `escalate_to_hitl`).

## What does it do?

- Contains the **full instruction set of L1-inception-feature-decomposer** (embedded in its prompt) so it can independently author reference-correct Features mentally.
- Reads `L1-features.json` (the candidate), `L1-epics.json` (the parent Epic set), and `L1-prd.md` (the original source) from the same blob storage folder in a single blob-storage-reader call.
- Scores the candidate against **8 named gates**: `faithfulness`, `completeness`, `schema_compliance`, `regulatory_accuracy`, `epic_traceability`, `delivery_sequencing`, `user_story_quality`, `acceptance_criteria_quality` — each 0.0-1.0, with `overall_score` (0-10) and `pass` derived from them.
- Also applies every Quality Gate and Reflection Checklist item from the core Feature Decomposer's own `evaluation.md` (inherited verbatim into this evaluator's `evaluation.md` Section A).
- Identifies every failing gate as a `finding` (`id`, `gate`, `status`, `detail`).
- **Automatically corrects** every fixable finding directly from the parent Epic or existing Feature content — never invents replacement content — logging each as a `fix` (`id`, `finding_id`, `description`, `before`, `after`, `reasoning`).
- Verifies every Feature's **`mvp_classification`** (`Foundational`/`Incremental`) against the Foundational Classification Test and structural signals from kb-features-best-practices §2.5, correcting misclassifications and generic `mvp_rationale` text, and enforcing that no Foundational Feature depends on an Incremental Feature.
- **Never guesses** when a fix would require information not present in the parent Epic — leaves that finding unresolved, which drives `final_decision` toward `escalate_to_hitl`.
- Produces corrected `content.items` that is schema-compliant with `L1-inception-feature-decomposer`'s own Feature schema.
- Issues a `final_decision`: `approved`, `fixed_and_approved`, or `escalate_to_hitl`.
- **Overwrites the SAME blob file** the core Feature Decomposer wrote — `L1-features.json` — via the attached **blob-storage-writer** tool, so downstream agents always read the latest, evaluated version under one name.

## How does it work?

1. **Ingest** `L1-features.json`, `L1-epics.json`, and `L1-prd.md` via blob-storage-reader in one call.
2. **Re-derive** (mentally) the reference-correct Features using the same Processing Rules as L1-inception-feature-decomposer.
3. **Score** all 8 named gates plus the inherited core Quality Gates against the candidate.
4. **Identify** every failing gate as a `finding` with a sequential `id`, `gate`, `status`, and `detail`.
5. **Correct** every fixable finding into the corrected `content.items`, logging `before`/`after`/`reasoning` in `fixes_applied`.
6. **Leave unresolved** any finding that cannot be safely fixed — no assumptions introduced; this drives `escalate_to_hitl`.
7. **Decide**: `final_decision` per the decision logic in `evaluation.md` Section B.2.
8. **Reflect**: self-check against the Evaluator Reflection Checklist, silently fix the evaluation itself if gaps are found.
9. **Persist**: call blob-storage-writer with `folder_name` (same as input), `file_name = "L1-features.json"` (overwriting the core agent's own output), `content` = the complete final AgentOutput verbatim.
10. **Emit** the final AgentOutput (including `content.artifacts[]` with the blob location) plus a plain-text `execution_summary`.

## Input

- **Source:** `blob_storage` ONLY — via the attached blob-storage-reader tool. This agent does NOT accept `direct_input` or `file_upload`.
- **Required:** `folder_name` — blob storage folder containing `L1-features.json`, `L1-epics.json`, and `L1-prd.md`, also the destination folder for the overwritten output.

## Output

- **Envelope:** AgentOutput v2 — `agent_id`, `agent_version`, `execution_id`, `workflow_execution_id` (inherited), `status`, `content`.
- **`content.items`** — the corrected Features set, in the exact same shape as `L1-inception-feature-decomposer`'s own `content.items`.
- **`content.evaluation`**:
  - `scores` — the 8 named gates, each 0.0-1.0.
  - `overall_score` — 0-10, average of the 8 scores * 10.
  - `pass` — true unless `final_decision == "escalate_to_hitl"`.
  - `findings[]` — every gate outcome, with `id`, `gate`, `status` (`pass`/`fail`), `detail`.
  - `fixes_applied[]` — one entry per fixed finding, with `id`, `finding_id`, `description`, `before`, `after`, `reasoning`.
  - `final_decision` — `approved` | `fixed_and_approved` | `escalate_to_hitl`.
- **`content.artifacts[]`** — the `L1-features.json` blob artifact this execution overwrote, with the literal `blob_storage_url` — never fabricated.
- **`content.execution_summary`** — plain-text bullets covering gate results, finding/fix counts, final decision rationale, and what reflection found/changed.
- **Knowledge Bases:** `kb-features-best-practices` (v1.1, including §2.5 Foundational/Incremental MVP classification) and `kb-epics-best-practices` (v1.1), both attached at runtime.
- **Tools:** `blob-storage-reader` (fetch candidate + parent Epics + PRD), `blob-storage-writer` (overwrite `L1-features.json` in place) — both attached at runtime.

## Composition

```
agents/L1-inception-feature-decomposer-evaluator/
├── spec.yaml
├── evaluation.md
├── output_schema.json
├── README.md
├── examples/
│   ├── input-01-approved-after-correction.json
│   ├── output-01-approved-after-correction.json
│   ├── input-02-rejected-missing-info.json
│   └── output-02-rejected-missing-info.json
└── golden/v1.0.0/
    ├── input-golden-01-approved.json
    ├── golden-01-approved.json
    ├── input-golden-02-rejected.json
    └── golden-02-rejected.json

prompts/L1-inception-feature-decomposer-evaluator/
└── instructions.md
```
