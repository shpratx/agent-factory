<!--
kb-L1-vision-statement-evaluation-rubric · content · evaluation-rubric.md
Layer: L1. Runtime copy of L1-vision-statement-generator/evaluation.md,
consumed by L1-vision-statement-generator-evaluator. Source of truth
is evaluation.md — keep this file in sync with it, do not edit independently.
-->

# Evaluation Rubric — L1-vision-statement-generator

## Quality Gates
- [ ] All required fields present (see output_schema.json's top-level required list)
- [ ] **BLOCKER — Reconciliation:** every constraint_id in regulatory_posture.constraint_summaries appears in at least one open_risks entry's related_ids — coverage, not 1:1 count; grouping related Amber items into one combined risk is fine, a constraint_id appearing in NO entry is not
- [ ] problem_statement/target_users/value_proposition do not contradict idea_brief_items (the upstream source)
- [ ] roadmap phase 1 addresses the single most severe open risk
- [ ] executive_summary introduces no claim absent from the sections below it
- [ ] No Confluence/publishing tool was invoked by this agent (that's L1-confluence-publisher's job)

## Scores (≥ threshold to pass)
| Evaluator | ≥ | Checks |
|-----------|---|--------|
| Faithfulness | 0.90 | Every carried-forward item matches its upstream source |
| Hallucination | ≤ 0.10 | No claim introduced that isn't grounded in one of the three upstream inputs |
| Consistency | 0.95 | Reconciliation check (above) passes fully — this is the highest consistency bar of any Phase 0 agent, since a dropped risk here reaches a human decision-maker |
| Relevance | 0.85 | Roadmap and metrics are usable as-is for Phase 1 planning |
| Reasoning quality | 0.80 | Every north_star_metric and roadmap phase explains its derivation |
| Citation completeness | N/A | This agent synthesizes upstream agent outputs, not KB/external sources — reconciliation check substitutes for citation |

## Reflection Checklist
- [ ] Zero regulatory Amber/Red items missing from open_risks
- [ ] executive_summary written last, after all other sections finalized


## Reflection Process
1. Generate → 2. Check all items above → 3. Fix silently → 4. Deliver final only

---
*Source of truth: L1-vision-statement-generator/evaluation.md — update both together, never let this KB drift from it.*
