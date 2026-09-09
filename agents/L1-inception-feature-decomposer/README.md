# L1-inception-feature-decomposer

## Purpose

Bridges the gap between coarse-grained business epics and buildable units of work. Delivery teams need
a consistent, traceable feature backlog to plan sprints and estimate work; this agent produces that
backlog automatically from the epics generated earlier in the Inception phase.

## What does it do?

- Accepts `epics.json` (produced by `epic-creator`) as input.
- For each epic, identifies the distinct functional slices needed to deliver its capability.
- Produces a set of features per epic, each:
  - Sized to fit within a single sprint
  - Traceable back to its parent epic
  - Mapped to relevant non-functional requirements (NFRs)
  - Backed by acceptance criteria consistent with the parent epic

## How does it work?

1. Ingests and validates `epics.json` (rejects empty/invalid input as `INSUFFICIENT_CONTEXT`).
2. Identifies functional slices within each epic's capability.
3. Converts each slice into a feature with an ID in `F-{epic}.{seq}` format.
4. Sizes and caps features per epic (`max_features_per_epic`).
5. Maps NFRs and builds a `traceability_matrix` linking every feature back to its epic.
6. Reflects on the output against `evaluation.md`, silently fixing issues.
7. Emits the final `features.json` plus a plain-text `execution_summary`.

## Input

- **Source:** Agent output (`epics.json` from `epic-creator`) or direct JSON input
- **Required:** `epics` — array of epic objects (id, title, description, capability, acceptance_criteria)
- **Optional:**
  - `max_features_per_epic` (default 6) — cap on features generated per epic
  - `target_sprint_length_weeks` (default 2) — sprint length used to guide feature sizing

## Output

- **Type:** `features`
- **Items:** `features` array — each with id, epic_id, title, description, acceptance_criteria, nfr_mapping, sprint_hint, and a `metadata` block (confidence, reasoning, citation, trajectory)
- **Metadata:** `traceability_matrix` linking epic_id to its feature_ids; optional `gaps` array for flagged issues
- **Summary:** `execution_summary` — plain text bullets covering counts produced, key decisions, reflection findings, and any gaps

## Composition

```
agents/L1-inception-feature-decomposer/
├── spec.yaml
├── evaluation.md
├── output_schema.json
├── README.md
├── examples/
│   ├── input-01-onboarding.json
│   ├── output-01-onboarding.json
│   ├── input-02-empty.json
│   └── output-02-empty.json
└── golden/v1.0.0/
    ├── input-golden-01-onboarding.json
    ├── golden-01-onboarding.json
    ├── input-golden-02-insufficient-context.json
    └── golden-02-insufficient-context.json

prompts/L1-inception-feature-decomposer/
└── instructions.md
```
