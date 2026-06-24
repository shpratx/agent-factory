# L1-inception-agent-evaluator

## Purpose

Evaluates any agent against a reusable quality rubric using benchmark scenarios, schema checks, and a structured scoring model. This package acts as a production-ready template for building consistent agent evaluation workflows.

## What does it do?

Takes an agent definition plus a set of benchmark cases and produces a scored report that covers:
- Functional correctness
- Completeness
- Groundedness
- Consistency
- Safety and compliance
- Output structure and schema validity
- Improvement recommendations

## How does it work?

1. Receives the target agent name, description, and evaluation cases
2. Validates the input contract and benchmark format
3. Assesses the agent's outputs against the rubric
4. Scores each dimension on a 0-10 scale
5. Returns an overall pass/fail decision with evidence and suggested fixes

## Input

- Source: direct_input or agent_output
- Required: agent_name, agent_spec, evaluation_cases
- Optional: scoring_weights, evaluation_mode

## Output

- Type: evaluation_report
- Includes: overall_score, status, dimension scores, evidence, recommendations, summary

## Composition

```
agents/L1-inception-agent-evaluator/
├── spec.yaml
├── evaluation.md
├── output_schema.json
├── README.md
├── examples/
└── golden/v1.0.0/

prompts/L1-inception-agent-evaluator/
└── instructions.md
```
