# Phase 0 — Idea → Vision: Output Templates & Worked Example

Templates in `templates/` define the required shape of each artifact — every
section marked ✅ is a hard requirement; an evaluator FAILs the gate if it's
missing. Placeholders use `{{snake_case}}`; HTML comments at the top of each
template name the producing/evaluating agent and the upstream artifact it
depends on.

`examples/` is one coherent worked example (a fictional product,
"HarvestLink" — a compliance-enabled producer-to-foodservice marketplace,
food production & distribution domain) run through the full chain, so you
can see exactly how facts must propagate rather than just what the section
headings are:

```
idea-brief.md            (L1-vision-idea-intake)
      │  problem statement, target users, candidate metrics
      ▼
market-analysis.md       (L1-vision-market-analyzer)
      │  consumes idea-brief's problem/users → competitor gap analysis
      ▼
regulatory-feasibility.md (L1-vision-regulatory-feasibility-checker)
      │  consumes idea-brief's geography/category → Green/Amber/Red per constraint
      ▼
vision.md                (L1-vision-statement-generator)  ← FINAL OUTCOME
   reconciles all three inputs:
   - problem/users/value prop carried forward verbatim, not restated differently
   - market-analysis's competitive gap → Market Context section
   - regulatory-feasibility's Amber/Red items → Regulatory Posture, AND every
     Amber/Red item must reappear in Open Risks Carried Forward
   - the single worst risk (the Red item) must become roadmap Phase 1 —
     this is the concrete test of "reconciliation," not just summarization
```

**What to check when validating a real agent's output against these examples:**
- `workflow_execution_id` is identical across all four documents in one run.
- `execution_id` is unique per document.
- Every named entity in a downstream document (problem statement, target
  users, artifact IDs) traces back to an upstream document — no drift, no
  restating the same fact two different ways.
- Every Amber/Red regulatory item survives all the way to `vision.md`'s Open
  Risks section. If one goes missing between `regulatory-feasibility.md` and
  `vision.md`, that's the evaluator's `gr-L1-hallucination-check` /
  `gr-L1-consistency-check` catching a dropped constraint — not a stylistic
  choice by the generator.

The example content is illustrative only — synthetic company names,
regulatory citations, and a fictional product, written to demonstrate the
pipeline's shape. It is not real market research or legal advice, and
shouldn't be reused as either.
