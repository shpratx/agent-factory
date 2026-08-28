# Evaluation — L1-planning-impact-assessor

This is the generator's own basic self-check only. Deep, independent re-derivation is delegated
downstream to ONE single evaluator agent (not part of this pack):
- an impact-assessment evaluator, which re-checks the catalog/CMDB findings against
  L1-impact-assessment.md, and independently re-derives the cycle_check/critical_path from the
  JSON graph items.

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
- [ ] The embedded mermaid graph in L1-impact-assessment.md matches the JSON graph items node-for-node, edge-for-edge, including
      cycle annotations when FAIL
- [ ] No `summary`/`*_summary` item field contains the full artifact text instead of a
      distillation

## Scores (≥ threshold to pass)
| Evaluator | ≥ | Checks |
|-----------|---|--------|
| Faithfulness | 0.90 | Every item traces to prd_output / service_catalog / cmdb_export / Phase A |
| Hallucination | ≤ 0.10 | No invented FR, CI, service, node, or edge |
| Consistency | 0.90 | Phase B never contradicts Phase A; JSON items and the embedded mermaid graph never diverge |
| Relevance | 0.85 | The single artifact (L1-impact-assessment.md) is directly usable by its named downstream consumers |
| Reasoning quality | 0.80 | Blast-radius, edge-direction, and cycle/critical-path decisions explained |
| Citation completeness | 0.95 | Components Identified rows cite FR-NNN; graph nodes cite source_requirement |

## Reflection Checklist
- [ ] Phase order respected: Impact Assessment first, Dependency Graph second, same run
- [ ] All required sections/items present in both phases, no placeholder text
- [ ] IDs (FR-NNN, node ids) valid, kebab-case where required, no duplicates
- [ ] The writer-tool call succeeded and the blob_storage_url is properly recorded in the output

## Reflection Process
1. Generate Phase A → self-check → 2. Generate Phase B from Phase A's own output →
self-check → render mermaid graph → append to document → 3. Run Quality Gates above → 4. Fix silently →
5. Write L1-impact-assessment.md and deliver final combined AgentOutput JSON only. Do NOT print interim output.
