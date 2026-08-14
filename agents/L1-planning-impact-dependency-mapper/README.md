# L1-planning-impact-dependency-mapper

## Purpose

Phase 1 of the SDLC pipeline (Requirements → NFR → PRD → **Impact Assessment → Dependency
Graph**) originally split its last two steps across two separate agents that communicated only
through blob storage. This agent merges those two steps into one execution: the Impact Assessment
always runs first, and the Dependency Graph is built directly from that same run's Components
Identified / External Dependencies tables — never re-fetched, never re-derived. This removes the
round-trip and the drift risk of the graph being built against a stale or different version of the
assessment. Evaluation of the two halves stays fully independent: this agent creates no
evaluators, and does not merge their scoring.

## What does it do?

- Reads `prd.md` plus raw `service_catalog` and `cmdb_export` system exports
- **Phase A:** produces `L1-impact-assessment.md` — capability check, technical touch check,
  every FR mapped to a component with a blast-radius rationale, external dependencies, and a
  synthesis-only Impact Summary
- **Phase B:** using Phase A's own Components Identified and External Dependencies rows (plus the
  PRD's FR set) as its ONLY node source, builds `L1-dependency-graph.json` — proven via an actual
  DFS cycle check and an actual longest-path critical-path computation — and a 1:1 Mermaid
  rendering, `L1-dependency-graph.mmd`
- Saves all three artifacts to blob storage and returns one combined `AgentOutput`

## How does it work?

1. Validate `prd_output.status == "success"`; check freshness/contamination of the two exports
2. **Phase A** — run capability + technical touch checks, map every FR to a component, list
   external dependencies, synthesize Impact Summary last, save the `.md`
3. **Phase B** — build one node per Phase A component row and per external dependency, build
   edges from Phase A's own prerequisite language, run DFS for `cycle_check`
4. If `cycle_check.status == FAIL`: stop critical-path computation, still render the `.mmd` with
   cycle annotations, set overall status `failed`
5. If `PASS`: compute longest path over blocking edges only, report every tied chain honestly
6. Render `.mmd` 1:1 from the already-built nodes/edges (no re-derivation), save both graph files
7. Self-check both phases, then emit one combined `AgentOutput`

## Input

- **Source:** direct input, file upload, or blob storage reader tool (see INPUT PROTOCOL in the
  prompt)
- **Required:** `prd` (prd_output, status must be `success`), `folder_name`
- **Optional:** `service_catalog`, `cmdb_export` — empty means "no parent enterprise", stated
  explicitly rather than silently skipped

## Output

- **Type:** `impact_dependency_assessment`
- **Items:** `impact_assessment` (meta-point summaries — full text lives in artifact-001) and
  `dependency_graph` (nodes/edges/cycle_check/critical_path, carried in full — structural data,
  not prose)
- **Artifacts:** `L1-impact-assessment.md`, `L1-dependency-graph.json`, `L1-dependency-graph.mmd`
- **Metadata:** confidence + reasoning per component/node where applicable; `source_requirement`
  citations on every graph node
- **Summary:** `execution_summary` covers both phases — checks run, cycle/critical-path result,
  all three blob storage locations, gaps flagged

## Evaluation (outside this pack)

This agent's own `evaluation.md` is a basic self-check only. Deep, independent re-derivation is
delegated to **two separate evaluator agents, not included in this pack**:
- an impact-assessment evaluator (re-checks catalog/CMDB findings against artifact-001)
- a dependency-graph evaluator (independently re-derives `cycle_check`/`critical_path` from the
  raw nodes/edges in artifact-002)

## Known prompt-budget overage

`instructions.md` is ~273 lines, well past the skill's ~150-line guidance. This is an explicitly
flagged overage, not an oversight: the prompt carries two full Processing Rules pipelines (Phase A
+ Phase B) plus Phase A's literal embedded markdown template (S4 — no template KB is attached), and
duplicate restatement between the template's own inline guidance and the Processing Rules was
already cut wherever the template said the same thing. Splitting Phase A and Phase B into two
prompts would remove the overage but would reintroduce the blob round-trip this agent exists to
eliminate, so the overage was kept rather than the substance cut.

## Composition

```
agents/L1-planning-impact-dependency-mapper/
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
    ├── input-golden-01-parent-enterprise.json
    ├── golden-01-parent-enterprise.json
    ├── input-golden-02-cycle-detected.json
    └── golden-02-cycle-detected.json

prompts/L1-planning-impact-dependency-mapper/
└── instructions.md
```
