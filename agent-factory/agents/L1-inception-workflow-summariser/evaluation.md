# Evaluation Criteria — L1-inception-workflow-summariser

## Quality Gates (must pass)

| Criterion | Threshold | Method |
|-----------|-----------|--------|
| All agents mentioned | 100% of input agents appear in execution_flow | Automated: count check |
| No invented data | 0 claims not traceable to input | LLM-as-Judge: faithfulness |
| Plain English | No raw JSON in output | Automated: regex check |
| Status accuracy | Workflow outcome matches agent statuses | Automated: logic check |
| Resources consolidated | No duplicate KB/guardrail/tool entries | Automated: uniqueness |

## Evaluation Scores (LLM-as-Judge)

| Evaluator | Threshold | Direction |
|-----------|-----------|-----------|
| Faithfulness | ≥ 0.95 | Every claim traces to an agent's execution_summary |
| Hallucination | ≤ 0.05 | No invented counts, artifacts, or statuses |
| Completeness | ≥ 0.95 | All agents, artifacts, and resources covered |
| Clarity | ≥ 0.85 | Non-technical reader can understand |
| Consistency | ≥ 0.90 | No contradictions between sections |

## Quality Rubric

| Dimension | Score 9-10 | Score 7-8 | Score 5-6 | Score < 5 |
|-----------|-----------|-----------|-----------|-----------|
| Coverage | All agents, artifacts, resources captured | 1 minor item missed | Several items missed | Major gaps |
| Clarity | Plain English, concise, stakeholder-ready | Mostly clear, minor jargon | Technical language mixed in | Unreadable by non-technical |
| Accuracy | Every fact verified against input | 1 minor inaccuracy | Several inaccuracies | Invented data |
| Structure | All 5 sections present and logical | Sections present but slightly disorganised | Missing sections | Unstructured |

## Reflection Checklist

The agent must self-verify before delivering:

- [ ] Every agent in the input array is mentioned in execution_flow
- [ ] request_and_intent reflects the actual workflow trigger (not invented)
- [ ] Artifact names/locations match what agents actually produced
- [ ] Resources (KBs, guardrails, tools) are consolidated with no duplicates
- [ ] Failed agents are highlighted in the outcome
- [ ] No raw JSON or schema fragments in the output
- [ ] Summary is concise (10-20 bullet points, not verbose paragraphs)

## Reflection Process (mandatory)

1. **Generate** initial summary from agent outputs
2. **Log** `[REFLECTING] Checking output against evaluation criteria`
3. **Check** every item in the Reflection Checklist above
4. **Identify** missing agents, invented data, or unclear language
5. **Log** each finding: `[REFLECTING] Found: <description>`
6. **Fix** each issue — amend the output silently
7. **Log** each resolution: `[REFLECTING] Resolved: <what was fixed>`
8. **Deliver** only the final corrected output
