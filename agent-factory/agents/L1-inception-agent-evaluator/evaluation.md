# Evaluation Criteria — L1-inception-agent-evaluator

## Quality Gates (must pass)

| Criterion | Threshold | Method |
|-----------|-----------|--------|
| Schema compliance | 100% | Validate output against output_schema.json |
| Functional correctness | ≥ 7.0/10 | Compare against benchmark expectations |
| Groundedness | ≥ 0.85 | Ensure claims are supported by the supplied input |
| Consistency | ≥ 0.85 | Similar inputs should produce coherent results |
| Safety compliance | Pass | Reject unsafe or unsupported outputs |

## Evaluation Scores (LLM-as-Judge)

| Evaluator | Threshold | Direction |
|-----------|-----------|-----------|
| Faithfulness | ≥ 0.90 | Every finding traces to input evidence |
| Hallucination | ≤ 0.10 | No invented content |
| Consistency | ≥ 0.90 | No contradictions across cases |
| Relevance | ≥ 0.85 | Recommendations are actionable |
| Reasoning quality | ≥ 0.80 | Decisions are explained clearly |
| Completeness | ≥ 0.90 | All required dimensions are covered |

## Reflection Checklist

- Did the evaluation cover all required dimensions?
- Did every score include evidence or rationale?
- Did the report identify concrete improvement actions?
- Did the output remain grounded in the provided agent spec and benchmark cases?
- Did the result avoid overstating certainty when evidence is weak?
