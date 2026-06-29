# Evaluation Criteria — L1-inception-requirements-extractor-agent

## Quality Gates (must pass)

| Criterion | Threshold | Method |
|-----------|-----------|--------|
| IDs sequential | FR-01... / NFR-01... / CON-01... / ASM-01... / GAP-01... / DEP-01... / DR-01... / INT-01... / SM-01... / RSK-01... | Automated: pattern check |
| No duplicate IDs | All IDs unique across categories | Automated: uniqueness check |
| Priorities assigned | Every FR and NFR has MoSCoW priority | Automated: field check |
| Citations present | Every FR and NFR has citation.source_reference | Automated: field check |
| Reasoning present | Every item across all 10 categories has reasoning field | Automated: field check |
| No empty required fields | id, title/description populated per category schema | Automated: null check |
| No invented features | Every requirement traces to input text | LLM-as-Judge: faithfulness |
| Confidence calibrated | Explicit = 0.9+, inferred = 0.7-0.8 | Automated: range check |
| PII flagged correctly | Data requirements with personal attributes have pii=true | Automated: keyword match |
| Risk likelihood/impact valid | Only High/Medium/Low values | Automated: enum check |
| PRD generated | artifacts array contains prd_document with valid blob location | Automated: field check |
| PRD follows template | All sections from kb-L1-prd-document-template present in output | LLM-as-Judge: structure match |

## Evaluation Scores (LLM-as-Judge)

| Evaluator | Threshold | Direction |
|-----------|-----------|-----------|
| Faithfulness | ≥ 0.90 | Every requirement traces to input phrase |
| Hallucination | ≤ 0.10 | No invented capabilities or features |
| Consistency | ≥ 0.90 | Requirements don't contradict each other |
| Relevance | ≥ 0.85 | Requirements are actionable, not vague |
| Reasoning quality | ≥ 0.80 | Categorisation decisions explained |
| Citation completeness | ≥ 0.95 | Every item cites exact input phrase |
| Completeness | ≥ 0.85 | Input's capabilities adequately captured |

## Requirements Quality Rubric

| Dimension | Score 9-10 | Score 7-8 | Score 5-6 | Score < 5 |
|-----------|-----------|-----------|-----------|-----------|
| Extraction | All stated features captured + implied ones flagged | Most stated captured, 1-2 missed | Several features missed | Major gaps |
| Categorisation | All 10 categories correctly separated | Mostly correct, 1-2 miscategorised | Several miscategorised | Categories confused |
| Priority | MoSCoW aligned with input language strength | Mostly correct priorities | Several wrong priorities | Random |
| Gaps & Assumptions | Genuine gaps identified with impact + question | Most gaps real, 1 over-flagged | Under-flagged (missing obvious gaps) | No gaps identified |
| Measurability | NFRs have quantifiable criteria | Most measurable, 1 vague | Several vague NFRs | No measurable criteria |
| Dependencies | Only explicitly mentioned or strongly implied dependencies | Mostly correct, 1 inferred without basis | Several invented dependencies | Hallucinated dependencies |
| Data & Privacy | Entities correctly identified, PII flagged accurately | Mostly correct, 1 PII mislabel | Several entities missed or PII wrong | No data requirements extracted |
| Integrations | Only stated system connections captured | Mostly correct, 1 inferred | Invented integrations present | Hallucinated integrations |
| Success Metrics | Only from explicit targets in input; vague ones raised as gaps | Mostly from input, 1 inferred loosely | Metrics invented without basis | Made-up KPIs |
| Risks | Genuine risks from input context or implied by architecture | Mostly valid, 1 generic | Several generic/template risks | Irrelevant risks |

## Reflection Checklist

The agent must self-verify before delivering:

- [ ] All explicitly stated capabilities have a corresponding FR
- [ ] NFRs are measurable (time, percentage, uptime — not "fast" or "secure")
- [ ] Constraints are fixed decisions, not capabilities (technology choices, not features)
- [ ] Assumptions are genuinely inferred, not fabricated
- [ ] Gaps are actionable — each has an impact statement and suggested question
- [ ] Dependencies are only extracted when input explicitly mentions external systems/teams
- [ ] Data requirements correctly flag PII (name, email, phone, DOB, financial = PII)
- [ ] Integration requirements only include systems mentioned or strongly implied by the input
- [ ] Success metrics are only extracted from explicit targets in input; vague aspirations go to gaps
- [ ] Risks are traceable to stated concerns or inherent technical risks of the described architecture
- [ ] No requirement contradicts another
- [ ] Confidence scores match: explicit statements = 0.9+, inferences = 0.7-0.8
- [ ] All items have reasoning field populated
- [ ] PRD document generated following kb-L1-prd-document-template structure
- [ ] PRD sections populated from extracted requirements (FRs→section 5, NFRs→section 6, etc.)
- [ ] PRD uploaded to blob storage at correct path (/<workflow_execution_id>/prd/)
- [ ] Artifacts array in output contains valid blob location URL
- [ ] Execution summary includes all 10 category counts and coverage assessment

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
