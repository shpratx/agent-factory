# Evaluation Criteria — L2-schreiber-foods-inception-epic-creator

## Quality Gates (must pass)

| Criterion | Threshold | Method |
|---|---:|---|
| Permitted source sections only | 100% | Citation section check |
| Required Jira headings | 100% | Markdown heading check |
| Epic name convention | 3–5 words, `Domain - Capability` | Pattern and word-count check |
| Out-of-scope fidelity | Exact source content, if supplied | Text comparison |
| Technical implementation leakage | 0 implementation details | Manual/LLM review |
| External links | Exactly 2 placeholders | Markdown check |

## Evaluation Scores (LLM-as-Judge)

| Evaluator | Threshold | Direction |
|---|---:|---|
| Faithfulness | ≥ 0.95 | Every claim traces to an allowed source section |
| Hallucination | ≤ 0.05 | No invented capability, constraint, or risk |
| Container principle | ≥ 0.95 | Explains what and why, never how |
| Concision | ≥ 0.90 | Scannable, low cognitive load |
| Citation completeness | ≥ 0.95 | Every output element has source metadata |

## Reflection Checklist

- [ ] Used only Executive Summary, Requirements, Out of Scope, Constraints, and Risks.
- [ ] Did not include a traceability matrix, compound split, assumptions, open questions, or glossary content.
- [ ] The Epic describes the strategic capability and user value, not solution architecture or delivery tasks.
- [ ] Scope contains only macro capability pillars.
- [ ] Out-of-scope text is carried over exactly when present.
- [ ] Constraints and risks are high-level and business-critical only.
- [ ] The exact required Jira Markdown headings and two artifact placeholders are present.
- [ ] All output items contain confidence, reasoning, citation, and trajectory metadata.

## Reflection Process (mandatory)

1. Generate a draft from permitted sections only.
2. Log internally: `[REFLECTING] Checking output against evaluation criteria`.
3. Review every checklist item and silently fix all defects.
4. Record fixes concisely in `execution_summary`.
5. Deliver only the corrected final output; never reveal interim reasoning or reflection logs.
