# Evaluation — L1-vision-viability-scorer

## Quality Gates
- [ ] All required fields present (see output_schema.json's top-level required list)
- [ ] **BLOCKER — Cap integrity:** every Red constraint and every requires_legal_review flag in regulatory-feasibility.md produced a matching entry in caps_applied, and final_score is at or below the lowest cap that fired
- [ ] final_score equals the lowest of weighted_score and every fired cap — a cap was applied as a ceiling, never averaged in
- [ ] Every component's traced_to names real content in the document it claims to score
- [ ] weighted_score reproduces from the three component scores and their weights (0.40 / 0.35 / 0.25)
- [ ] No score was rounded up across the threshold of 7
- [ ] recommendation matches final_score against the threshold
- [ ] The score reflects what the documents say about the idea, not how well the analyses were written or what their evaluators scored them
- [ ] **BLOCKER — Verbatim carriage:** viability-assessment.md contains all three source documents in full, byte-for-byte apart from heading demotion — nothing summarised, trimmed, reworded, or corrected

## Scores (≥ threshold to pass)
| Evaluator | ≥ | Checks |
|-----------|---|--------|
| Faithfulness | 0.95 | Every component score is supported by the cited document content |
| Hallucination | ≤ 0.05 | No mitigation, market number, or user segment introduced that the documents do not contain |
| Consistency | 0.95 | weighted_score, caps_applied, final_score and recommendation all agree with each other |
| Reasoning quality | 0.85 | Each component explains its score against its band, citing ids rather than asserting a judgement |
| Citation completeness | 1.00 | Hard-gated — a component score with no traced_to is a fail, not a deduction |

## Reflection Checklist
- [ ] Zero unresolved regulatory blockers scored above the threshold — an uncapped Red is the defect this agent exists to prevent
- [ ] A thin source document lowered the component's confidence, not its score
- [ ] A below-threshold score was reported exactly as derived — not softened, not rounded up, no cap quietly dropped
- [ ] The capped and pre-cap scores are both visible in score_derivation, so the gap a human sees is the real one
- [ ] viability-assessment.md and items agree — the document never states a score, cap, or component the items contradict
- [ ] A low-scored finding was carried through in its own words, uncorrected — the human reads the same text the score came from

## Reflection Process
1. Generate → 2. Check all items above → 3. Fix silently → 4. Deliver final only
