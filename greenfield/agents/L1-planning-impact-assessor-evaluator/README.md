# L1-planning-impact-assessment-evaluator

## Purpose

L1-planning-impact-dependency-mapper produces two things from the same
PRD: an impact assessment (capability check + technical-touch findings
against existing systems) and a dependency graph (nodes, edges,
cycle_check, critical_path, rendered as both JSON and Mermaid). This
agent is the single, independent evaluator over that entire output. It
replaces what would otherwise be two separate evaluators
(`L1-planning-impact-assessor-evaluator` and
`L1-planning-dependency-mapper-evaluator`) with one gate, since both
target the same generator and the same downstream consumer
(`L1-planning-backlog-prioritizer`). Nothing from either original
evaluator's independence guarantees is dropped in the merge — this agent
never accepts a generator-declared value as evidence of its own
correctness, on either the impact-assessment side or the graph side.

## What does it do?

- Re-fetches `service_catalog` and `cmdb_export` independently and
  re-derives the capability check and every relevant CI's
  touched/not-touched status from them plus
  `kb-L1-enterprise-architecture`
- Checks export freshness and HarvestLink contamination against the
  generator's stated freshness finding
- Re-runs DFS cycle detection and, if acyclic, an independent
  longest-path walk to re-derive `critical_path` (including honest tie
  detection)
- Spot-checks edge direction against `impact-assessment.md`'s stated
  prerequisite language
- Verifies `dependency-graph.mmd` is a 1:1 structural rendering of
  `dependency-graph.json` — node/edge counts, directions, shapes, styles,
  and cycle/critical-path annotations
- Fixes mechanically-recoverable gaps (a touched/not-touched row, a
  reversed edge with a clear source citation, a missed tie, a dropped FR,
  a wrong MMD shape/style) and writes the correction back to every
  artifact it appears in, at the SAME blob storage location
- Escalates genuine disagreements (an ambiguous cycle direction, a
  stale/contaminated export) to HITL rather than guessing

## How does it work?

1. Ingest `generator_output` and independently re-fetch `service_catalog`, `cmdb_export`, `impact-assessment.md`, `dependency-graph.json`, `dependency-graph.mmd`
2. Re-derive the capability check and technical-touch findings; check freshness/contamination
3. Re-run DFS cycle detection; if acyclic, re-run longest-path and compare against `critical_path`
4. Spot-check edge directions and node/FR grounding
5. Parse the `.mmd` and structurally verify it against the `.json`
6. Apply mechanical fixes across every affected artifact, or escalate genuine disagreements
7. Emit `final_decision` and fire `gr-L1-impact-assessment-quality-gate` once, only on the final successful iteration

## Input

- **Source:** agent_output from `L1-planning-impact-dependency-mapper`
- **Required:** `generator_output` — the generator's full output including `content.items` and `content.artifacts`
- **Optional:** `original_input` — used only for `prd_output` grounding, never trusted for `service_catalog`/`cmdb_export` passthrough

## Output

- **Type:** `evaluation_result`
- **Items:** `scores`, `overall_score`, `pass`, `findings[]` (tagged by `gate`: capability-check, technical-touch, freshness-contamination, fr-component-coverage, cycle-check, critical-path, edge-direction, grounding, mmd-structural), `fixes_applied[]`, `final_decision`
- **Metadata:** every finding cites a specific `ci_id`, `service_id`, `FR-id`, node id, or edge (from/to); every fix states its reasoning and which artifact(s) it was written back to
- **Summary:** plain-text bullets covering re-derivation results for both halves of the output, any mismatch found and whether fixed or escalated, MMD verification detail, artifacts verified, KBs/tools/guardrails used, gaps flagged

## Composition

```
agents/L1-planning-impact-assessment-evaluator/
├── spec.yaml
├── evaluation.md
├── output_schema.json
├── README.md
├── examples/
│   ├── input-01-typical.json
│   ├── output-01-typical.json
│   ├── input-02-edge-case.json
│   └── output-02-edge-case.json
└── golden/v1.0.0/

prompts/L1-planning-impact-assessment-evaluator/
└── instructions.md
```
