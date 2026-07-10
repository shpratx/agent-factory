# Evaluation Criteria — L1-inception-ai-evaluation-agent-app-builder-and-scoring-orchestrator

## Quality Gates (must pass)

| Criterion | Threshold | Method |
|-----------|-----------|--------|
| Required sections present | Includes App Blueprint, Evaluation Logic, Data Model, UI Specification, Reliability Controls, Security Notes, Delivery Checklist | Automated: section check |
| Task inputs covered | Includes task name, description, success criteria, failure modes, output type, difficulty | Automated: field check |
| Scoring logic defined | Programmatic checks, rubric scoring, weighting, PASS/FAIL threshold included | Automated: field check |
| UI and responsive guidance included | React/Tailwind and responsive accessibility guidance present | Automated: field check |
| Security controls present | Secret handling, logging, data minimization, retention guidance included | Automated: field check |
| Output grounded in task | No invented requirements beyond the supplied context | LLM-as-Judge: faithfulness |

## Evaluation Scores (LLM-as-Judge)

| Evaluator | Threshold | Direction |
|-----------|-----------|-----------|
| Completeness | ≥ 0.90 | All required sections and implementation details are covered |
| Relevance | ≥ 0.90 | The specification is practical and aligned to the task |
| Consistency | ≥ 0.90 | The sections align and do not contradict each other |
| Actionability | ≥ 0.85 | The output is specific enough for implementation |
| Security awareness | ≥ 0.90 | The spec addresses secrets, logging, and data minimization |

## Reflection Checklist

- [ ] The specification defines screen-by-screen behavior and component responsibilities
- [ ] The evaluation logic includes programmatic checks, Claude judging, retries, schema validation, and threshold logic
- [ ] The data model defines result object schemas and aggregation behavior
- [ ] UI guidance includes React, Tailwind, responsiveness, accessibility, and loading states
- [ ] Reliability controls include validation, retries, backoff, timeouts, error states, and telemetry
- [ ] Security notes cover environment variables, secret masking, and data minimization
- [ ] The delivery checklist provides implementation tasks and acceptance checks
