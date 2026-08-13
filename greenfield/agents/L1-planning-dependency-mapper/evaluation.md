# Evaluation — L1-planning-dependency-mapper

## Quality Gates
- [ ] `cycle_check` was produced by an ACTUAL depth-first-search traversal
      (recursion-stack back-edge detection) over every node/edge — never
      asserted PASS because the graph "looks" acyclic
- [ ] `critical_path` was produced by an ACTUAL longest-path computation over
      `depends-on`/`blocks` edges only (`integrates-with` excluded, non-blocking
      by definition) — never asserted from eyeballing the longest-looking chain
- [ ] A genuine TIE in longest-path length is reported honestly as a tie,
      naming every chain that shares the maximum length — never arbitrarily
      resolved to a single "winner" to make the output look simpler
- [ ] Edge direction is UNIFORM: `from` is always upstream/prerequisite, `to`
      is always downstream/dependent, for every edge regardless of `type`
      (`depends-on`, `blocks`, `integrates-with` all follow the same rule)
- [ ] Every FR-NNN in prd.md appears in at least one node's `source_requirement`
      — checked by set membership against prd.md's full FR list, not by
      counting nodes and assuming coverage
- [ ] Every component and external dependency named in impact-assessment.md
      has a corresponding node — no silent drop
- [ ] Node ids are kebab-case (`^[a-z0-9-]+$`), unique, no duplicates
- [ ] If `cycle_check.status` is FAIL, overall AgentOutput `status` is
      `"failed"` (escalate) — a cyclic graph is never silently "fixed" by
      dropping the offending edge and reporting success
- [ ] `dependency-graph.mmd` node count equals `dependency-graph.json` `nodes[]`
      count exactly — 1:1, no additions or omissions
- [ ] `dependency-graph.mmd` edge count equals `dependency-graph.json` `edges[]`
      count exactly — 1:1, no additions or omissions
- [ ] No edge direction is flipped in `dependency-graph.mmd` relative to
      `dependency-graph.json` — `from` and `to` ids match verbatim
- [ ] Node shapes in `dependency-graph.mmd` are correct per `node.type`:
      `"component"` → rectangle `{id}["{label}"]`;
      `"external-dependency"` → stadium `{id}(["{label}"])`
- [ ] Edge styles in `dependency-graph.mmd` are correct per `edge.type`:
      `"blocks"` → `-->|blocks|`;
      `"depends-on"` → `-->|depends on|`;
      `"integrates-with"` → `-.->|integrates with|` (dashed, non-blocking)
- [ ] If `cycle_check.status` is FAIL: every node in `cycles_found` carries a
      `classDef cycleNode` highlight and a `%% CYCLE: ...` comment in the `.mmd`
      — a visually "clean" diagram over a cyclic JSON graph is a fail finding
- [ ] If `cycle_check.status` is PASS: a `%% CRITICAL PATH: ...` comment line
      exists in the `.mmd` for every tied chain reported in `critical_path`
- [ ] `dependency-graph.mmd` was saved AFTER step 8 self-check passed — an
      unverified graph must not be rendered as final
- [ ] Both blob storage locations are recorded: `dependency-graph.json` and
      `dependency-graph.mmd` under their respective schema keys

## Scores (≥ threshold to pass)
| Evaluator | ≥ | Checks |
|-----------|---|--------|
| Faithfulness | 0.90 | Every node/edge traces to a real impact-assessment.md component or external dependency |
| Hallucination | ≤ 0.10 | No node, edge, FR coverage, or MMD element invented beyond impact-assessment.md / prd.md |
| Consistency | 0.90 | `cycle_check` and `critical_path` are consistent with the actual edge set; `dependency-graph.mmd` is a 1:1 rendering of `dependency-graph.json` |
| Relevance | 0.85 | Output is directly usable as topological-sort input by backlog-prioritizer |
| Reasoning quality | 0.80 | `critical_path.rationale` states the actual path length and any tie, not just a list of ids |
| Citation completeness | N/A | This agent grounds against impact-assessment.md/prd.md directly, not a KB — `source_requirement` and node `label` substitute for citation |

## Reflection Checklist
- [ ] DFS cycle check was actually run (traced node-by-node), not eyeballed
- [ ] Longest-path computation was actually run edge-by-edge over the
      blocking subset, not eyeballed
- [ ] No summary/rationale field silently contains less information than the
      graph itself would show — the graph fields (nodes/edges/cycle_check/
      critical_path) ARE the meta-points here, per output_schema.json's own
      note on why this agent departs from the usual condensation pattern
- [ ] `dependency-graph.mmd` was rendered from the SAME nodes[]/edges[]/
      cycle_check/critical_path built in processing steps 2–7 — no independent
      recomputation, no cosmetic omissions
- [ ] MMD node count, edge count, and edge directions were explicitly verified
      against `dependency-graph.json` before delivery
- [ ] If `cycle_check.status` is FAIL, cycle annotations (`classDef` +
      `%% CYCLE:` comments) are present in the `.mmd` — the diagram is diagnostic,
      never dressed up as acyclic
- [ ] Both `blob_storage_url` (JSON) and `mmd_blob_storage_url` (MMD) are
      populated in the output artifacts

## Reflection Process
1. Generate → 2. Check all items above → 3. Fix silently → 4. Deliver final only
