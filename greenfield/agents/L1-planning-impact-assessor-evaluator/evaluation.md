# Evaluation — L1-planning-impact-assessment-evaluator

## Quality Gates
- [ ] service_catalog and cmdb_export were independently re-fetched, not read from original_input passthrough
- [ ] capability_check re-derived from the fresh service_catalog, not accepted from matched_service_id/is_duplicate alone
- [ ] every relevant CI's touched/not-touched status independently re-derived from cmdb_export.relationships + KB narrative
- [ ] export_metadata.exported_at freshness and HarvestLink contamination checked on the fresh export, not the generator's copy
- [ ] cycle_check independently re-derived via this evaluator's own DFS, not read from the generator's field
- [ ] critical_path independently re-derived via this evaluator's own longest-path walk (depends-on/blocks only), ties checked
- [ ] a sample of edge directions (every "blocks" edge + every critical-path edge) spot-checked against impact-assessment.md's prerequisite language
- [ ] dependency-graph.mmd node count, edge count, edge directions, shapes, and edge styles verified against dependency-graph.json
- [ ] if cycle_check is FAIL: cycle nodes carry classDef cycleNode + %% CYCLE: comment in the .mmd
- [ ] if cycle_check is PASS: a %% CRITICAL PATH: comment exists for every tied chain
- [ ] every FR in the PRD maps to a component with a blast-radius rationale and appears in some node's source_requirement[]
- [ ] no fix invents a service, CI, dependency, node, or edge absent from the real data
- [ ] any fix touching impact-assessment.md, dependency-graph.json, or dependency-graph.mmd is written back to that SAME blob location before final_decision
- [ ] gr-L1-impact-assessment-quality-gate fired exactly once, on the final successful iteration only

## Scores (≥ threshold to pass)
| Evaluator | ≥ | Checks |
|-----------|---|--------|
| Faithfulness | 0.90 | Every finding traces to a re-fetched/re-derived source, not the generator's claim |
| Hallucination | ≤ 0.05 | No invented service, CI, node, edge, or dependency |
| Consistency | 0.95 | items and all three artifacts (md, json, mmd) never diverge post-fix |
| Relevance | 0.85 | Findings are actionable and cite a specific id |
| Reasoning quality | 0.85 | Every fix and every escalation states its source-grounded reasoning |
| Citation completeness | 0.95 | Every finding cites a ci_id, service_id, FR-id, node id, or edge (from/to) |

## Reflection Checklist
- [ ] Did I actually re-fetch service_catalog/cmdb_export, or reuse the generator's copy?
- [ ] Did I actually run DFS and longest-path myself, or just compare fields?
- [ ] Did I count nodes/edges in the .mmd text, or assume it matches the JSON?
- [ ] Is every mechanical fix grounded in impact-assessment.md or kb-L1-enterprise-architecture, with no invented entity?
- [ ] Does every fixed_and_approved decision correspond to artifacts actually overwritten at their original locations?
- [ ] Was the quality-gate guardrail fired only once, on the final iteration?

## Reflection Process
1. Re-fetch and re-derive independently → 2. Compare against generator's declared values → 3. Fix mechanically-recoverable gaps or escalate genuine disagreements → 4. Sync every touched artifact → 5. Deliver final result only, no interim output.
