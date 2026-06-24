# Evaluation Criteria — L1-inception-vision-generator

## Quality Gates (must pass)

| Criterion | Threshold | Method |
|-----------|-----------|--------|
| All 5 sections present | 100% | Automated: check headings |
| Executive Summary ≤ 10 sentences | Pass/Fail | Automated: sentence count |
| MVP features table has ≥ 5 rows | Pass/Fail | Automated: row count |
| Out-of-scope table has ≥ 3 rows | Pass/Fail | Automated: row count |
| Success metrics have measurable targets | 100% | LLM-as-Judge |
| No placeholder text remaining | 0 placeholders | Automated: regex `{{.*}}` |
| Artifact uploaded successfully | 200 response | Automated: blob upload status |

## Evaluation Scores (LLM-as-Judge)

| Evaluator | Threshold | Direction |
|-----------|-----------|-----------|
| Faithfulness | ≥ 0.90 | Every claim traces to domain KB or stated input |
| Hallucination | ≤ 0.10 | No invented market data, statistics, or regulations |
| Consistency | ≥ 0.90 | No contradictions between sections |
| Relevance | ≥ 0.85 | Content directly serves the stated idea |
| Reasoning quality | ≥ 0.80 | Business decisions explained |
| Domain grounding | ≥ 0.90 | Feature areas, users, constraints reflect domain KB |
| Specificity | ≥ 0.85 | Concrete metrics, not vague aspirations |

## Quality Rubric

| Dimension | Score 9-10 | Score 7-8 | Score 5-6 | Score < 5 |
|-----------|-----------|-----------|-----------|-----------|
| Structure | All 5 sections complete with all subsections | All 5 sections, minor subsections missing | Major subsections missing | Sections missing entirely |
| Domain alignment | Every feature/user/constraint grounded in KB | Most grounded, 1-2 inferred reasonably | Mix of grounded and generic | Generic document, KB ignored |
| MVP clarity | Clear boundary, explicit in/out scope, testable criteria | Mostly clear, 1-2 ambiguous features | Blurred MVP/vision boundary | No clear MVP boundary |
| Market insight | Specific competitors, quantified opportunity, clear drivers | Named drivers and users, some quantification | Generic market statements | No market analysis |
| Actionability | Team could start requirements extraction immediately | Minor clarifications needed | Significant gaps before actionable | Not actionable |

## Reflection Checklist

The agent must self-verify before delivering:

- [ ] All 5 major sections present (Executive Summary, Business Context, Full Scope Vision, MVP Scope, Risks)
- [ ] Executive Summary is 3-5 sentences max
- [ ] Problem Statement is specific, not generic platitudes
- [ ] Business Drivers cite domain-specific context from KB
- [ ] Target Users table has ≥ 3 user types with domain-relevant roles
- [ ] Success Metrics have numeric targets, not "improve" or "increase"
- [ ] Feature Areas are domain-specific capabilities (not generic like "user management")
- [ ] Integration Points reference real systems from the domain
- [ ] User Journeys are end-to-end with numbered steps and outcomes
- [ ] MVP features have clear rationale for inclusion
- [ ] Out-of-scope features explain why deferred
- [ ] Constraints/Assumptions state "Risk if wrong"
- [ ] Risks table has Likelihood + Impact + Mitigation
- [ ] Open Questions feed into requirements analysis
- [ ] No vague language: "world-class", "seamless", "intuitive", "best-in-class"
- [ ] No technology/implementation decisions (that belongs in HLD)
- [ ] Document reads as complete — not a template with gaps

## Reflection Process (mandatory)

1. **Generate** initial vision document following template structure
2. **Log** `[REFLECTING] Checking output against evaluation criteria`
3. **Check** every item in the Reflection Checklist above
4. **Identify** gaps, vague language, ungrounded claims, or missing sections
5. **Log** each finding: `[REFLECTING] Found: <description>`
6. **Fix** each issue — amend the output silently
7. **Log** each resolution: `[REFLECTING] Resolved: <what was fixed>`
8. **Deliver** only the final corrected output

## Writing Quality Rules

These rules apply to the generated markdown document content:

### Do
- Be specific and measurable ("reduce processing time by 30%", not "make things faster")
- Clearly separate full vision from MVP — no features in MVP that aren't in full vision
- Include "out of scope" lists — they prevent scope creep
- Write for the delivery team, not executives — avoid marketing language
- State assumptions explicitly so they can be challenged
- Include success criteria that can actually be tested
- Use domain terminology from the KB consistently

### Do Not
- Use vague language: "world-class", "seamless", "intuitive", "best-in-class"
- Include technology or implementation details (that belongs in HLD)
- Skip the MVP section or blur its boundary with full vision
- Combine features and user journeys (features = what system does; journeys = how users experience it)
- Assume readers know the business context — write the Problem Statement even if it seems obvious
- Invent statistics or market data not grounded in the domain KB
