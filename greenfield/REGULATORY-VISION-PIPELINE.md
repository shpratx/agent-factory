# Regulatory Feasibility → Viability Scoring → Vision Statement Pipeline

This document describes how three L1 "vision phase" components fit together:

1. **Regulatory Feasibility Checker** (`L1-vision-regulatory-feasibility-checker`), gated by the **Citation Verifier** guardrail
2. **Vision Viability Scorer** (`L1-vision-viability-scorer`)
3. **Vision Statement Generator** (`L1-vision-statement-generator`)

Each generator agent has its own independent **evaluator** agent and a **quality gate** guardrail that fires when that evaluator concludes. Nothing here is decorative — every gate exists because a false negative at that point becomes a compliance or trust problem for a human downstream (the Product Lead).

---

## 1. End-to-end flow

```
L1-vision-idea-intake                 L1-vision-market-analyzer
   (idea-brief.md)                       (market-analysis.md)
        │                                       │
        └───────────────┐         ┌─────────────┘
                         ▼         ▼
        ┌───────────────────────────────────────────┐
        │  L1-vision-regulatory-feasibility-checker  │
        │  in: problem_statement, target_geography    │
        │  out: constraints[], overall_status,        │
        │       open_items[]                          │
        └───────────────────┬─────────────────────────┘
                             │
                    ┌────────▼─────────┐
                    │ gr-L1-citation-   │  output rail, BLOCKER
                    │ verifier          │  every constraint must cite
                    └────────┬─────────┘  a real source_reference +
                             │            specific regulation
                             ▼
        ┌───────────────────────────────────────────┐
        │ L1-vision-regulatory-feasibility-checker-  │
        │ evaluator                                   │
        │ re-derives severity independently, fixes    │
        │ what it can (fixes_applied)                 │
        └───────────────────┬─────────────────────────┘
                             │ post_execution
                    ┌────────▼─────────────────┐
                    │ gr-L1-regulatory-         │  RESULTANT-content gate
                    │ feasibility-quality-gate  │  8 rules, BLOCKER on
                    │                           │  omitted/unmitigated Red
                    └────────┬──────────────────┘
                             │
             regulatory-feasibility.md + items
                             │
   idea-brief.md ──┐        │        ┌── market-analysis.md
                    ▼        ▼        ▼
        ┌───────────────────────────────────────────┐
        │        L1-vision-viability-scorer          │
        │  weighted_score = regulatory×0.40           │
        │                 + market×0.35                │
        │                 + idea×0.25                   │
        │  final_score = min(weighted_score, caps)      │
        │  (a Red constraint or requires_legal_review    │
        │   caps the score below the threshold of 7,     │
        │   regardless of market strength)                │
        │  → viability_score, viability-assessment.md      │
        └───────────────────┬───────────────────────────────┘
                             │ viability_score (number, not re-computed downstream)
        idea_brief_items ────┤
        market_analysis_items ┤
        regulatory_feasibility_items ┤
                             ▼
        ┌───────────────────────────────────────────┐
        │       L1-vision-statement-generator         │
        │  reconciles all three upstream artifacts +   │
        │  viability_score into one document            │
        │  RULE: every Amber/Red constraint_summaries    │
        │  entry MUST be covered by ≥1 open_risks entry  │
        │  → vision.md + items                            │
        └───────────────────┬───────────────────────────┘
                             │
        ┌────────────────────▼──────────────────────┐
        │ L1-vision-statement-generator-evaluator     │
        │ re-checks reconciliation coverage,           │
        │ executive_summary claim-hygiene,             │
        │ honest viability_score reporting              │
        └────────────────────┬──────────────────────┘
                             │ post_execution
                    ┌────────▼─────────────────┐
                    │ gr-L1-vision-statement-   │  RESULTANT-content gate
                    │ quality-gate              │  7 rules, BLOCKER on
                    │                           │  coverage gap
                    └────────┬──────────────────┘
                             │
                    vision.md → Product Lead (HITL approval)
```

**Key invariant across the whole pipeline:** the guardrail wired to an *evaluator* never grades the evaluator's own scores or self-reported `final_decision`. It independently re-derives the rule against the **resultant content** — the generator's `items` with the evaluator's `fixes_applied` merged in — because that resultant content, not the evaluator's opinion of it, is what actually flows to the next stage.

---

## 2. Component 1 — Regulatory Feasibility Checker

`greenfield/agents/L1-vision-regulatory-feasibility-checker/`

| | |
|---|---|
| **Input** | `problem_statement`, `target_geography` (required); `product_category` (optional) — sourced from `L1-vision-idea-intake` |
| **Output** | `constraints[]`, `overall_status`, `open_items[]` → `regulatory-feasibility.md` |
| **KBs** | `kb-L1-regulatory-frameworks-index` (cross-domain), `kb-L2-domain-regulatory` (domain-specific) |
| **Tools** | `tool-L1-regulatory-db-lookup` (read-only), Azure blob reader/writer |
| **Zero-tolerance rule** | A Red constraint with no `mitigation_summary` and `requires_legal_review: false` is an **invalid output**, not a style gap |

Each `constraints[]` item is Green/Amber/Red, with a `citation` object (`source_reference` + `regulation`) that is **required**, not optional — a compliance verdict with no traceable source is indistinguishable from a hallucination.

### Guardrail: `gr-L3-citation-verifier`

`greenfield/guardrails/gr-L3-citation-verifier/`

- **Fires:** output rail, directly on the checker's own response — before its evaluator ever sees it
- **On fail:** Block
- **Checks, per constraint, independently of anything the response claims about itself:**
  - `citation.source_reference` non-empty and not fabricated
  - `citation.regulation` names a specific regulation/section — not a placeholder like "applicable regulations"
  - Citation object present at all; citation array (if any) not empty
- **Explicitly rejects as a substitute:** a `rationale_summary`/`mitigation_summary` that *mentions* a regulation in prose, or the response's own `execution_summary` claiming citations are complete. The gate re-derives the check itself.
- **Implementation:** Prompt-only Colang (`gr-L1-citation-verifier.co`) — three standard `define bot` blocks, no Python, no `define flow`. Detection logic lives in `self_check_input`/`self_check_output` prompts in `config.yml`, mirrored so the same rule set applies whichever rail is wired and so pasted content can be tested standalone.

### Evaluator + quality gate

`L1-vision-regulatory-feasibility-checker-evaluator` (`min_score: 8.5`, the highest bar in Phase 0) re-derives constraint severity independently rather than trusting the generator's self-classification, and fixes what it safely can.

`gr-L1-regulatory-feasibility-quality-gate` then fires on that evaluator's `post_execution` but validates the **resultant** checker output (not the evaluator's scorecard) against 8 rules — schema compliance, amber/red mitigation-or-legal-review (BLOCKER), sequential ids, citation specificity, rationale/status agreement, no severity downgrade, `requires_legal_review` not used as a blanket escape, and the hard **BLOCKER**: no Red constraint discussed in reasoning but missing from the final `constraints[]` array. On fail: retry once, then escalate to HITL.

---

## 3. Component 2 — Vision Viability Scorer

`greenfield/agents/L1-vision-viability-scorer/`

Consumes all three vision-phase source documents (`idea-brief.md`, `market-analysis.md`, `regulatory-feasibility.md`, each from upload or blob storage) and produces a single `viability_score` — the number `L1-vision-statement-generator` receives as an input and is **forbidden from recomputing**.

**Scoring model:**

```
weighted_score = (regulatory_posture × 0.40)
                + (market_opportunity × 0.35)
                + (idea_clarity       × 0.25)

final_score = min(weighted_score, every fired cap)   # a cap is a ceiling, never averaged in
```

| Cap rule | Cap value | Trigger |
|---|---|---|
| `red_constraint` | 6.0 | Any Red constraint in regulatory-feasibility.md |
| `regulatory_overall_red` | 6.0 | Overall regulatory status is Red |
| `requires_legal_review` | 6.5 | Any constraint flagged for legal review |
| `missing_market_analysis` | 6.9 | market-analysis.md absent |

All caps sit below the `auto_publish_eligible` threshold of **7** — an unresolved regulatory blocker can never be outvoted by a strong market case. `capped: true` keeps the pre-cap and post-cap scores both visible, so a human sees the real gap.

**Output** (`output_schema.json`): `viability_score`, `recommendation` (`auto_publish_eligible` | `human_review_required` — a statement of where the score falls, not a workflow decision), `score_derivation` (weighted/final/capped/threshold), exactly 3 `components` (each with `id`, `weight`, `score`, `confidence`, `traced_to`, `reasoning` ≤40 words), `caps_applied[]`, `inputs_read[]`.

**Verbatim-carriage BLOCKER:** `viability-assessment.md` must contain all three source documents in full, byte-for-byte apart from heading demotion — nothing summarized, trimmed, or corrected. `items` carries only meta-points about that document; the consolidated narrative lives solely in the artifact.

**Quality bar** (`evaluation.md`): Faithfulness ≥0.95, Hallucination ≤0.05, Consistency ≥0.95, Reasoning quality ≥0.85, Citation completeness = 1.00 (hard-gated — a component score with no `traced_to` is a fail, not a deduction). Cap integrity is a BLOCKER: every Red constraint / `requires_legal_review` flag must have a matching `caps_applied` entry, and `final_score` must equal the lowest of `weighted_score` and every fired cap.

---

## 4. Component 3 — Vision Statement Generator

`greenfield/agents/L1-vision-statement-generator/`

| | |
|---|---|
| **Input** | `idea_brief_items`, `market_analysis_items`, `regulatory_feasibility_items` (full items objects from the three upstream agents) + `viability_score` (computed upstream, never recomputed here) |
| **Output** | `executive_summary`, `problem_statement`, `target_users`, `value_proposition`, `market_context`, `regulatory_posture`, `north_star_metrics[]`, `roadmap[]`, `open_risks[]` → `vision.md` |
| **KBs** | none — vision structure is embedded in `instructions.md`; this agent purely reconciles, it doesn't look anything up |

This is a **reconciliation** agent, not a summarizer. Its one hard rule, enforced structurally rather than via JSON Schema (it spans this agent's own upstream inputs, so schema validation alone can't express it):

> Every Amber/Red entry in `regulatory_posture.constraint_summaries` MUST be covered by at least one `open_risks[].related_ids` entry, with a roadmap dependency (`resolves_risk`).

Coverage, not 1:1 cardinality — two thematically related Amber constraints may be grouped into one combined `open_risks` entry. **Dropping a constraint entirely** is the defect this exists to prevent, not the grouping itself.

### Evaluator + quality gate

`L1-vision-statement-generator-evaluator` (`min_score: 8.5`) independently verifies the reconciliation is real: every Amber/Red constraint is covered, `executive_summary` introduces no claim absent elsewhere, and the received `viability_score` is reported honestly rather than silently overridden.

`gr-L1-vision-statement-quality-gate` fires on that evaluator's `post_execution` and re-validates the **resultant** content against 7 rules:

| # | Rule | Kind |
|---|---|---|
| 1 | Schema compliance (against the *generator's* output schema) | block, deterministic |
| 2 | `NSM-NN`/`OR-NN` ids sequential; roadmap phases sequential | block, deterministic |
| 3 | **Reconciliation coverage complete** — every `constraint_id` ∈ union of `open_risks.related_ids` | **BLOCKER**, deterministic |
| 4 | Roadmap phase 1 resolves the worst (Red-traced) open risk, if one exists | flag, deterministic |
| 5 | `executive_summary` introduces no claim absent elsewhere | flag, semantic (LLM) |
| 6 | No Confluence/publishing tool invoked (publishing is a separate Utility agent's job) | flag, deterministic |
| 7 | `viability_score` reported honestly, cross-checked against `original_input` | block, deterministic |

Two implementations exist for this gate: an LLM-only Colang flow (`gr-L1-vision-statement-quality-gate.co`) running all 7 checks via `self_check_output`, and a Python-hybrid flow (`vision_statement_quality_gate.co` + `actions.py`) that runs the 6 deterministic checks directly in code and defers only rule 5 (genuinely semantic) to the LLM.

**Why this is the last automated checkpoint:** nothing downstream of this evaluator catches a dropped regulatory finding — a human (the Product Lead) does, reading `vision.md` and reasonably assuming nothing was silently lost. `regulatory_posture.constraint_summaries` and `open_risks` live on the same output, so the coverage check is entirely self-contained — no upstream lookup required, which makes a slip-through here especially avoidable.

---

## 5. Guardrail pattern used throughout

All three quality-gate guardrails in this pipeline share one shape, distinct from an ordinary output-schema check:

1. They are wired to the **evaluator**, not the generator (`configured_agents` in `spec.yaml`).
2. They fire at the evaluator's `post_execution` — after the evaluator has already scored and fixed what it could.
3. They **do not** grade the evaluator's own `scores`/`findings`/`final_decision`.
4. They reconstruct the **resultant content** (generator `items` + evaluator `fixes_applied` merged in) and re-derive the one non-negotiable rule for that stage directly against it — independent of what the evaluator claims it fixed.
5. On fail: retry once, then escalate to HITL (except the citation verifier, which is a hard block at the generator's own output, one step earlier in the chain).

This means a bug in the evaluator's own bookkeeping — a `fixed_and_approved` verdict that's wrong, a `fixes_applied` entry that didn't actually land — still gets caught, because the gate never trusts the evaluator's report; it only trusts what the resultant content itself says.

| Guardrail | Fires on | Validates | BLOCKER rule |
|---|---|---|---|
| `gr-L3-citation-verifier` | `L1-vision-regulatory-feasibility-checker` output | Every constraint has a real, specific citation | Missing/generic/fabricated citation |
| `gr-L1-regulatory-feasibility-quality-gate` | `L1-vision-regulatory-feasibility-checker-evaluator` post_execution | Resultant checker output | No Red constraint omitted or left unmitigated |
| `gr-L1-vision-statement-quality-gate` | `L1-vision-statement-generator-evaluator` post_execution | Resultant statement-generator output | No Amber/Red constraint uncovered by `open_risks` |

---

## 6. File map

```
greenfield/
├── agents/
│   ├── L1-vision-regulatory-feasibility-checker/            spec.yaml, output_schema.json, evaluation.md
│   ├── L1-vision-regulatory-feasibility-checker-evaluator/  spec.yaml, output_schema.json, evaluation.md
│   ├── L1-vision-viability-scorer/                          output_schema.json, evaluation.md
│   ├── L1-vision-statement-generator/                       spec.yaml, output_schema.json, evaluation.md
│   └── L1-vision-statement-generator-evaluator/             spec.yaml, output_schema.json, evaluation.md
├── prompts/
│   ├── L1-vision-regulatory-feasibility-checker/instructions.md
│   ├── L1-vision-regulatory-feasibility-checker-evaluator/instructions.md
│   ├── L1-vision-viability-scorer/instructions.md
│   ├── L1-vision-statement-generator/instructions.md
│   └── L1-vision-statement-generator-evaluator/instructions.md
├── guardrails/
│   ├── gr-L3-citation-verifier/               config.yml, gr-L1-citation-verifier.co, spec.yaml, README.md
│   ├── gr-L1-regulatory-feasibility-quality-gate/  config.yml, *.co, spec.yaml, README.md
│   └── gr-L1-vision-statement-quality-gate/   config.yml, prompts.yml, *.co, actions.py, spec.yaml, README.md
└── phase-0/
    ├── knowledge-bases/kb-L1-regulatory-feasibility-evaluation-rubric/
    ├── templates/regulatory-feasibility.template.md
    └── examples/regulatory-feasibility.md
```
