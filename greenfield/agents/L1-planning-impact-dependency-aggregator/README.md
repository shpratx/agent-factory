# L1-planning-impact-dependency-aggregator

## Purpose

After L1-planning-impact-dependency-mapper produces three separate artifacts and both
independent evaluators (L1-planning-impact-assessment-evaluator, then
L1-planning-dependency-graph-evaluator) have verified and potentially corrected them, some
downstream consumers (human reviewers, confluence publishers, the backlog prioritizer's context
window) benefit from having the impact assessment and the visual dependency graph in a single
document. This agent performs that concatenation and nothing else: it pulls
`L1-impact-assessment.md` and `L1-dependency-graph.mmd`, combines them verbatim into
`L1-impact-assessment-dependency-graph.md`, and saves the result.

## What does it do?

- Reads `L1-impact-assessment.md` and `L1-dependency-graph.mmd` from blob storage
- Validates both are present, non-empty, and reference the same product
- Concatenates: impact assessment content first, horizontal rule, `## Dependency Graph` heading,
  then the Mermaid source in a fenced code block
- Saves the combined artifact to blob storage and returns an `AgentOutput`

## How does it work?

1. Retrieve both source artifacts in full via blob storage reader
2. Validate both are present and non-empty; confirm product name consistency
3. Concatenate verbatim — no edits, no re-derivation, no analysis
4. Save `L1-impact-assessment-dependency-graph.md` to blob storage
5. Self-check (nothing added/removed), then emit `AgentOutput`

## Input

- **Source:** direct input, file upload, or blob storage reader tool (see INPUT PROTOCOL in the
  prompt)
- **Required:** `folder_name`
- **Optional:** `impact_assessment_md`, `dependency_graph_mmd` — full text if provided directly

## Output

- **Type:** `impact_dependency_aggregation`
- **Items:** `product_name`, `source_artifacts` (references to both source files),
  `aggregation_method` (`verbatim-concatenation`), `sections_included`
- **Artifacts:** `L1-impact-assessment-dependency-graph.md`
- **Summary:** `execution_summary` covers sources consumed, tools invoked, blob storage location

## Evaluation

This agent's `evaluation.md` checks that the combined document is a verbatim pass-through of
both sources with no additions or omissions. No deep analytical evaluation is needed — the
quality of the source artifacts is the responsibility of the upstream mapper and its independent
evaluators.

## Composition

```
agents/L1-planning-impact-dependency-aggregator/
├── spec.yaml
├── evaluation.md
├── output_schema.json
├── README.md
├── examples/
│   ├── input-01-happy-path.json
│   ├── output-01-happy-path.json
│   ├── input-02-edge-case.json
│   └── output-02-edge-case.json
└── golden/v1.0.0/
    ├── input-golden-01-aggregation.json
    └── golden-01-aggregation.json

prompts/L1-planning-impact-dependency-aggregator/
└── instructions.md
```
