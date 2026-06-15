# L1-inception-stories-generator-agent

## Purpose

Decomposes epics and features into implementable user stories ordered for incremental delivery. Stories are sequenced from foundational setup through simple features to complex enhancements, enabling teams to deliver sprint after sprint.

## What does it do?

Takes epics with features (from the epics generator) and produces:
- **User stories** in "As a / I want / So that" format
- **Acceptance criteria** in Given/When/Then (3-5 per story, testable)
- **4-tier sequencing:** Foundation → Core → Enhancement → Polish
- **Story points** (1, 2, 3, 5 — capped at 5, each story fits one 5-day cycle)
- **Dependencies** between stories (acyclic, minimal, enable parallel work)
- **Data sensitivity** tagged on every story

The incremental ordering ensures teams can start immediately with foundation stories (no dependencies), then build up through increasingly complex capabilities.

## How does it work?

1. Ingests epics with features (from epics generator or direct input)
2. Validates at least one epic with one feature exists
3. For each feature, decomposes into stories across 4 tiers:
   - Tier 1 (Foundation): data models, API setup, SDK integration, config
   - Tier 2 (Core): happy path, primary UI, main user flows
   - Tier 3 (Enhancement): validations, error handling, edge cases, offline
   - Tier 4 (Polish): performance, UX refinement, advanced features
4. Orders stories within each feature by tier (1 → 2 → 3 → 4)
5. Orders features by dependency (independent first)
6. Assigns story points based on complexity (max 5 — split if larger)
7. Tags data sensitivity on every story
8. Maps dependencies (no intra-feature deps for Tier 1; cross-feature allowed)
9. Reflects against evaluation.md — verifies sequencing, coverage, dependencies
10. Delivers final output with recommended cycle-by-cycle implementation sequence

## Input

- **Source:** agent_output (from L1-inception-epics-generator-agent) or direct_input
- **Required:** `epics` (array) — epics with features including implements[], acceptance_summary
- **Optional:** `target_feature` (string — generate for one feature only), `cycle_duration_days` (integer, default 5)

## Output

- **Type:** `stories`
- **Items:** Array of stories, each with: id, epic_id, feature_id, tier, tier_label, title (As a.../I want.../So that...), acceptance_criteria[], story_points, data_sensitivity, depends_on[], implements[], metadata
- **Summary:** Plain-text with story count per tier, recommended cycle sequence, effort estimate, reflection findings

## Composition

```
L1-inception-stories-generator/
├── spec.yaml                 # Agent specification
├── evaluation.md             # Quality rubric and reflection checklist
├── output_schema.json        # JSON Schema for output validation
├── examples/                 # Input/output pairs
│   ├── input-01-expense-capture.json
│   └── output-01-expense-capture.json
└── golden/v1.0.0/            # Benchmark responses
    └── golden-01-expense-capture.json

prompts/L1-inception-stories-generator-agent/
└── instructions.md           # Agent prompt
```
