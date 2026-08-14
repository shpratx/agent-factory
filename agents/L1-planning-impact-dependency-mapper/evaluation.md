# Evaluation — L1-planning-impact-dependency-mapper

This is the generator's own basic self-check only. Deep, independent re-derivation is delegated
downstream to TWO SEPARATE evaluator agents (not part of this pack):
- an impact-assessment evaluator, which re-checks the catalog/CMDB findings against
  L1-impact-assessment.md
- a dependency-graph evaluator, which independently re-derives cycle_check/critical_path from the
  raw nodes/edges in L1-dependency-graph.json

## Quality Gates
- [ ] Phase A ran to completion (or a valid INSUFFICIENT_CONTEXT) before Phase B started
- [ ] Every FR-NNN in prd_output appears in Components Identified (Phase A) AND in some node's
      source_requirement (Phase B) — set membership
- [ ] Every service_catalog entry and every relevant cmdb_export CI was checked, not skipped
- [ ] No CMDB/KB mismatch was silently reconciled instead of flagged
- [ ] Phase B nodes/edges trace 1:1 to Phase A's own Components Identified / External
      Dependencies — no node invented, none dropped
- [ ] cycle_check.status is the output of an actual DFS trace (rationale names the traversal, not
      just "no cycles found")
- [ ] critical_path is the output of an actual longest-path computation; genuine ties are all
      reported, none arbitrarily dropped
- [ ] dependency-graph.mmd matches dependency-graph.json node-for-node, edge-for-edge, including
      cycle annotations when FAIL
- [ ] No `summary`/`*_summary` item field contains the full artifact text instead of a
      distillation

## Scores (≥ threshold to pass)
| Evaluator | ≥ | Checks |
|-----------|---|--------|
| Faithfulness | 0.90 | Every item traces to prd_output / service_catalog / cmdb_export / Phase A |
| Hallucination | ≤ 0.10 | No invented FR, CI, service, node, or edge |
| Consistency | 0.90 | Phase B never contradicts Phase A; JSON and .mmd never diverge |
| Relevance | 0.85 | Both artifacts are directly usable by their named downstream consumers |
| Reasoning quality | 0.80 | Blast-radius, edge-direction, and cycle/critical-path decisions explained |
| Citation completeness | 0.95 | Components Identified rows cite FR-NNN; graph nodes cite source_requirement |

## Reflection Checklist
- [ ] Phase order respected: Impact Assessment first, Dependency Graph second, same run
- [ ] All required sections/items present in both phases, no placeholder text
- [ ] IDs (FR-NNN, node ids) valid, kebab-case where required, no duplicates
- [ ] Both writer-tool calls succeeded and both blob_storage_url fields are recorded distinctly

## Reflection Process
1. Generate Phase A → self-check → save → 2. Generate Phase B from Phase A's own output →
self-check → save JSON → render + save .mmd → 3. Run Quality Gates above → 4. Fix silently →
5. Deliver final combined output only. Do NOT print interim output.
