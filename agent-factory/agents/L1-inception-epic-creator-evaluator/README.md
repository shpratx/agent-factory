# L1-inception-epics-creator-evaluator

## Purpose

This agent is the automated quality gate for `L1-inception-epics-creator`. It reads a candidate `L1-epics.json` and the source `L1-prd.md` from blob storage, independently re-derives what a correct Epic set should look like using the same SOP rules the core agent follows, scores the candidate against 8 mandatory gates, automatically corrects every safely-fixable issue, and overwrites `L1-epics.json` in place with the corrected output plus a final decision (`approved`, `fixed_and_approved`, or `escalate_to_hitl`).

## What does it do?

- Contains the **full instruction set of L1-inception-epics-creator** (embedded in its prompt) so it can independently author a reference-correct Epic mentally, rather than only pattern-matching against a checklist.
- Reads `L1-epics.json` (the candidate) and `L1-prd.md` (the source) from the same blob storage folder in a single blob-storage-reader call.
- Scores the candidate against **8 named gates**: `faithfulness`, `completeness`, `schema_compliance`, `regulatory_accuracy`, `prd_traceability`, `cardinality_compliance`, `title_and_altitude_quality`, `risk_filtering_quality` — each 0.0-1.0, with `overall_score` (0-10) and `pass` derived from them.
- Also applies every Quality Gate and Reflection Checklist item from the core Epics Creator's own `evaluation.md` (inherited verbatim into this evaluator's `evaluation.md` Section A).
- Identifies every failing gate as a `finding` (`id`, `gate`, `status`, `detail`).
- **Automatically corrects** every fixable finding directly from the source PRD or existing Epic content — never invents replacement content — logging each as a `fix` (`id`, `finding_id`, `description`, `before`, `after`, `reasoning`).
- **Never guesses** when a fix would require information not present in the source — leaves that finding unresolved, which drives `final_decision` toward `escalate_to_hitl`.
- Produces corrected `content.items` that is schema-compliant with `L1-inception-epics-creator`'s own Epic schema.
- Issues a `final_decision`: `approved` (no issues), `fixed_and_approved` (issues found and all fixed), or `escalate_to_hitl` (unfixable Critical/Major gap remains, requiring human review).
- **Overwrites the SAME blob file** the core Epics Creator wrote — `L1-epics.json` — via the attached **blob-storage-writer** tool, so downstream agents always read the latest, evaluated version under one name.

## How does it work?

1. **Ingest** both `L1-epics.json` and `L1-prd.md` via blob-storage-reader in one call.
2. **Re-derive** (mentally) the reference-correct Epic set using the same Processing Rules as L1-inception-epics-creator.
3. **Score** all 8 named gates plus the inherited core Quality Gates against the candidate.
4. **Identify** every failing gate as a `finding` with a sequential `id`, `gate`, `status`, and `detail`.
5. **Correct** every fixable finding into the corrected `content.items`, logging `before`/`after`/`reasoning` in `fixes_applied`.
6. **Leave unresolved** any finding that cannot be safely fixed — no assumptions introduced; this drives `escalate_to_hitl`.
7. **Decide**: `final_decision` per the decision logic in `evaluation.md` Section B.2.
8. **Reflect**: self-check against the Evaluator Reflection Checklist, silently fix the evaluation itself if gaps are found.
9. **Persist**: call blob-storage-writer with `folder_name` (same as input), `file_name = "L1-epics.json"` (overwriting the core agent's own output), `content` = the complete final AgentOutput verbatim.
10. **Emit** the final AgentOutput (including `content.artifacts[]` with the blob location) plus a plain-text `execution_summary`.

## Input

- **Source:** `blob_storage` ONLY — via the attached blob-storage-reader tool. This agent does NOT accept `direct_input` or `file_upload`.
- **Required:** `folder_name` — blob storage folder containing both `L1-epics.json` and `L1-prd.md`, also the destination folder for the overwritten output.

## Output

- **Envelope:** AgentOutput v2 — `agent_id`, `agent_version`, `execution_id`, `workflow_execution_id` (inherited), `status`, `content`.
- **`content.items`** — the corrected Epics set, in the exact same shape as `L1-inception-epics-creator`'s own `content.items`.
- **`content.evaluation`**:
  - `scores` — the 8 named gates, each 0.0-1.0.
  - `overall_score` — 0-10, average of the 8 scores * 10.
  - `pass` — true unless `final_decision == "escalate_to_hitl"`.
  - `findings[]` — every gate outcome, with `id`, `gate`, `status` (`pass`/`fail`), `detail`.
  - `fixes_applied[]` — one entry per fixed finding, with `id`, `finding_id`, `description`, `before`, `after`, `reasoning`.
  - `final_decision` — `approved` | `fixed_and_approved` | `escalate_to_hitl`.
- **`content.artifacts[]`** — the `L1-epics.json` blob artifact this execution overwrote, with the literal `blob_storage_url` — never fabricated.
- **`content.execution_summary`** — plain-text bullets covering gate results, finding/fix counts, final decision rationale, and what reflection found/changed.
- **Knowledge Base:** `kb-epics-best-practices` (v1.1, attached at runtime) — same KB the core Epics Creator uses.
- **Tools:** `blob-storage-reader` (fetch candidate + PRD), `blob-storage-writer` (overwrite `L1-epics.json` in place) — both attached at runtime.

## Composition

```
agents/L1-inception-epics-creator-evaluator/
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

prompts/L1-inception-epics-creator-evaluator/
└── instructions.md
```
