# L1-inception-epic-creator-agent

## Purpose

Converts an approved roadmap and vision into a delivery-ready epic backlog. Groups roadmap items into business-capability epics, grounds every field in traceable source content, checks for duplicates against the existing issue tracker, and produces plannable units that the Feature Decomposer can break down further.

## What does it do?

Takes an approved roadmap (from the sprint planner) and an approved vision (from the vision-statement generator), and produces:
- **Epics** — business capability groupings of roadmap items, one epic per logical capability
- **Traceability** — every epic links back to the roadmap item(s) and vision theme(s) it derives from
- **Deduplication** — every run checks existing tracker epics before proposing new ones
- **Open questions** — anything that can't be grounded in the input is surfaced explicitly, never guessed at

The agent groups roadmap items by business capability cohesion, ensuring each epic represents a logical planning unit a team can decompose and schedule.

## How does it work?

1. Ingests roadmap.md and vision.md (from upstream agents or direct input)
2. Validates roadmap carries Product-Lead approval and vision clears its viability threshold
3. Grounds each roadmap item to a supporting vision theme before drafting
4. Calls the issue tracker to fetch existing epics and checks for duplicates
5. Drafts epic objects: title, description, business value, priority, target phase, source refs
6. Reflects against evaluation.md — verifies full roadmap coverage, no duplication, no cross-phase scope, no sensitive content
7. Delivers final output with plain-text execution summary

## Input

- **Source:** agent_output (from `L1-planning-sprint-planner-agent` and `L1-vision-statement-generator-agent`) or direct_input
- **Required:** `roadmap` (object, Product-Lead approved), `vision` (object, viability_score >= 7)
- **Optional:** `max_epics` (integer, default 10), `dedupe_scope` (string: project|program|portfolio)

## Output

- **Type:** `epics`
- **Items:** Array of epics, each with: epic_id, title, description, business_value, priority, target_phase, source_refs[], dedupe_check, metadata
- **Also includes:** open_questions[], delivery_summary
- **Summary:** Plain-text with epic count, roadmap coverage, dedupe results, grouping decisions, reflection changes

## Composition

```
L1-inception-epic-creator/
├── spec.yaml                 # Agent specification
├── evaluation.md             # Quality rubric and reflection checklist
├── output_schema.json        # JSON Schema for output validation
├── examples/                 # Input/output pairs
│   ├── input-01-checkout-platform.json
│   └── output-01-checkout-platform.json
└── golden/v1.0.0/            # Benchmark responses
    ├── golden-01-checkout-platform.json
    └── golden-02-empty-input.json

prompts/L1-inception-epic-creator-agent/
└── instructions.md           # Agent prompt
```

## Human Gate

The Product Lead reviews `open_questions` and any quality-gate failure history before the Feature Decomposer (A2) is authorized to run against this epic set.
