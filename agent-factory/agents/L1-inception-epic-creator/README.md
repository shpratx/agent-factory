# L1-inception-epic-creator

## Purpose

Converts the approved Phase 1 outputs — PRD, Impact Assessment, and Dependency Graph — into a verifiable, dependency-ordered set of business-capability epics. Every field in every epic is grounded in explicit citation to source content; nothing is asserted without a traceable PRD requirement ID, impact-assessment finding ID, or dependency-graph node ID behind it.

## What does it do?

Takes an approved PRD (prd.md), an impact assessment (impact-assessment.md), and a dependency graph (dependency_graph.json), and produces:
- **Epics** — business-capability groupings of PRD requirements, one epic per logical capability, never a technical layer
- **Full PRD coverage** — every FR-NNN/NFR in the PRD is assigned to at least one epic's `requirements_used`, or explicitly recorded in `open_questions`
- **Dependency-ordered sequencing** — epics are ordered using `dependency_graph.json` edges, foundational (upstream) capabilities before dependent (downstream) ones
- **Impact-assessment grounding** — findings that materially change an epic's scope or risk (e.g. high blast-radius flags) are folded into that epic's `business_value`/`description`, citing the finding ID
- **Traceability matrix** — generated directly from `requirements_used` on every epic, never maintained separately, so it can never diverge
- **Open questions** — anything that can't be grounded in the input (an unmappable requirement, a dependency node with no epic, a cross-phase scope) is surfaced explicitly, never guessed at

## How does it work?

1. Ingests `prd.md`, `impact-assessment.md`, and `dependency_graph.json` — via direct input, file upload, or an attached blob storage reader tool (`folder_name` supplied at runtime)
2. Validates upstream status, and that all three inputs are present and parseable; returns `INSUFFICIENT_CONTEXT` / `PRECONDITION_FAILED` if any are missing or malformed
3. Grounds every PRD requirement to the epic(s) it belongs in, citing the source requirement, finding, or node for every field written
4. Drafts epic objects: title, description, business_value, priority, requirements_used, acceptance_criteria, confidence, reasoning
5. Assigns priority from the PRD's own requirement ordering — never invented
6. Orders epics by dependency using `dependency_graph.json` edges
7. Flags any requirement whose scope spans more than one delivery phase as a split candidate, rather than silently splitting or merging it
8. Builds `traceability_matrix` directly from `requirements_used`, and `open_questions` for anything ungroundable
9. Saves the completed epic set to blob storage (`L1-epics.json`) via the attached blob storage writer tool, and captures the returned `blob_storage_url`
10. Self-checks against the full reflection checklist (coverage, sequencing, citation validity, no PII, traceability-matrix consistency) and fixes issues silently before delivering
11. Delivers the final output with a plain-text execution summary

## Input

- **Source:** `agent_output` (from `L1-requirements-prd-composer`, `L1-planning-impact-assessor`, `L1-planning-dependency-mapper`), `direct_input`, or `file_upload` (`prd.md`, `impact-assessment.md`, `dependency_graph.json`) — checked in that order, used verbatim, never merged across sources
- **Required:** `prd` (PRD content with FR-NNN/NFR set), `impact_assessment` (affected systems, blast-radius ratings, risk flags), `dependency_graph` (nodes and edges for sequencing)
- **Optional:** `folder_name` (string, used by the attached blob storage reader/writer tool if attached)

## Output

- **Type:** `epics`
- **Items:** Array of epics, each with: `epic_id`, `title`, `description`, `business_value`, `priority` (P0/P1/P2), `requirements_used[]`, `acceptance_criteria[]` (each citing its source), `confidence`, `reasoning`
- **Also includes:** `traceability_matrix[]` (fr_id → covered_by epic_id list), `open_questions[]`
- **Storage:** `blob_storage_url` where `L1-epics.json` was saved
- **Summary:** Plain-text — workflow_execution_id, total epics, PRD requirement coverage, key sequencing/priority decisions, self-check findings, open_questions, tools invoked, blob storage location

## Composition

```
L1-inception-epic-creator/
├── spec.yaml                 # Agent specification
├── output_schema.json        # JSON Schema for output validation
├── examples/                 # Input/output pairs
│   ├── input-01-{name}.json
│   └── output-01-{name}.json
└── golden/v1.0.0/            # Benchmark responses
    ├── golden-01-{name}.json
    └── golden-02-empty-input.json

prompts/L1-inception-epic-creator/
└── instructions.md           # Agent prompt
```

## Downstream Verification

`L1-inception-epic-creator-evaluator` independently re-derives PRD coverage and dependency-graph ordering against this agent's output before `L1-inception-feature-decomposer` is authorized to run against the epic set — see that agent's own instructions for the verification contract.
