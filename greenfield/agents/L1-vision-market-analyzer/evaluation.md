# Evaluation — L1-vision-market-analyzer

## Quality Gates
- [ ] All required fields present: competitor_matrix, swot (all 4 quadrants), data_sufficiency
- [ ] Every competitor_matrix entry has a non-empty citation with source_reference + retrieved_date
- [ ] Every SWOT item's reasoning names a specific competitor id or idea-brief fact
- [ ] data_sufficiency.status is "insufficient" (not fabricated coverage) when KB + search both returned thin results
- [ ] IDs sequential per category (CM-01...; ST/WK/OP/TH-01...), no gaps or duplicates

## Scores (≥ threshold to pass)
| Evaluator | ≥ | Checks |
|-----------|---|--------|
| Faithfulness | 0.90 | Every competitor claim traces to KB or search citation |
| Hallucination | ≤ 0.10 | No invented competitors or unsupported statistics |
| Consistency | 0.90 | SWOT doesn't contradict the competitor matrix it's derived from |
| Relevance | 0.85 | Competitors reviewed are realistic alternatives for the stated target users |
| Reasoning quality | 0.80 | SWOT reasoning explains derivation, not just restates the statement |
| Citation completeness | 0.95 | 100% of competitor_matrix entries cite a source — this is a BLOCKER, not just scored |

## Reflection Checklist
- [ ] No competitor entry lacks a citation
- [ ] No SWOT item is generic filler unconnected to a specific competitor/fact
- [ ] data_sufficiency rationale is honest, not padded to look thorough

## Reflection Process
1. Generate → 2. Check all items above → 3. Fix silently → 4. Deliver final only
