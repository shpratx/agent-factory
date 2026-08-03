# Evaluation Criteria — L1-inception-epic-creator-agent

## Quality Gates (must pass)

| Criterion | Threshold | Method |
|-----------|-----------|--------|
| All roadmap items covered | 100% of input roadmap items in at least one epic's source_refs | Automated: set comparison |
| No orphan roadmap items | Zero roadmap items unassigned | Automated: count unassigned |
| Epic size | Fits within one roadmap phase, no cross-phase scope unflagged | Automated: phase-span check |
| IDs sequential | EPIC-01, EPIC-02... | Automated: pattern check |
| No duplicate IDs | All IDs unique | Automated: uniqueness check |
| Priorities assigned | Every epic has a MoSCoW priority | Automated: field check |
| Epics have source_refs | No empty source_refs | Automated: field check |
| Dedupe executed | dedupe_check.checked = true on every run | Automated: field check |
| No PII/sensitive content | Zero PII matches in title/description/business_value | Automated: pattern scan |

## Evaluation Scores (LLM-as-Judge)

| Evaluator | Threshold | Direction |
|-----------|-----------|-----------|
| Faithfulness | ≥ 0.90 | Every epic traces to roadmap/vision content in input |
| Hallucination | ≤ 0.10 | No invented epics beyond input roadmap/vision |
| Consistency | ≥ 0.90 | Epics don't overlap or contradict |
| Relevance | ≥ 0.85 | Groupings are logical business capabilities, not technical layers |
| Reasoning quality | ≥ 0.80 | Grouping and priority decisions explained |
| Citation completeness | ≥ 0.95 | Every epic cites roadmap/vision IDs |

## Epic Quality Rubric

| Dimension | Score 9-10 | Score 7-8 | Score 5-6 | Score < 5 |
|-----------|-----------|-----------|-----------|-----------|
| Grounding | Every field traces to a real source; no invented scope | Mostly grounded, one weak citation | Several ungrounded claims | Largely invented |
| Coverage | 100% roadmap coverage, no gaps | All roadmap items covered, minor omissions in detail | Some roadmap items missing | Major gaps |
| Deduplication | Dedupe run, no unresolved overlaps internally or vs. tracker | Dedupe run, one minor overlap flagged | Dedupe run but overlaps missed | Dedupe skipped or overlaps ignored |
| Scope discipline | All epics fit one roadmap phase | Most right-sized, one flagged split candidate | Several epics span phases unflagged | Epics undeliverable/unbounded |
| Clarity | A downstream engineer could scope feature work from the description alone | Mostly clear, minor ambiguity | Several vague descriptions | Descriptions too generic to act on |

## Reflection Checklist

The agent must self-verify before delivering:

- [ ] Every roadmap item from input appears in at least one epic's source_refs
- [ ] Every epic maps to at least one roadmap item (no orphan epics)
- [ ] No duplicate or overlapping epics — internally, and against tracker dedupe results
- [ ] No epic spans more than one roadmap phase without an explicit split flag
- [ ] business_value cites a specific vision theme, not a generic statement
- [ ] No PII, credentials, or customer-identifying content in any field
- [ ] Priorities trace to roadmap ordering, not invented
- [ ] Execution summary includes coverage count, dedupe results, and open questions

## Reflection Process (mandatory)

The agent MUST perform reflection before delivering output:

1. **Generate** initial output following processing rules
2. **Log** `[REFLECTING] Checking output against evaluation criteria`
3. **Check** every item in the Reflection Checklist above
4. **Identify** gaps, errors, inconsistencies, or missed items
5. **Log** each finding: `[REFLECTING] Found: <description>`
6. **Fix** each issue — amend the output silently
7. **Log** each resolution: `[REFLECTING] Resolved: <what was fixed>`
8. **Deliver** only the final corrected output

The reflection findings and resolutions should appear in the execution_summary
(what reflection found and changed) but the interim output must never be shown.
