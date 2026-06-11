# gr-L3-consistency-checker

**Layer:** L3 Project (applies to multi-item output agents)  
**Triggers on:** post_execution (output rail)  
**On fail:** Warn and escalate to HITL  
**Implementation:** Colang + Python actions

## What does it do?

Detects contradictions, conflicting enum values, and duplicate IDs in multi-item agent output. Ensures all items are internally consistent — same entities referenced the same way, no duplicate identifiers, and no contradictory claims across items.

## How It Works

```
Agent generates multi-item output
        ↓
┌─────────────────────────────────────┐
│  check_internal_consistency (Py)    │
│                                     │
│  ✓ All item IDs unique?             │
│  ✓ No conflicting enum values?      │
│                                     │
│  Duplicates → BLOCK                 │
└─────────────────────────────────────┘
        ↓ (pass)
┌─────────────────────────────────────┐
│  self_check_output (LLM)           │
│  Semantic consistency check         │
│  Entity consistency, contradictions │
└─────────────────────────────────────┘
        ↓ (consistent)
Output delivered
```

## Rules

| Rule | Description | Action | Severity |
|------|-------------|--------|----------|
| no-duplicate-ids | All item IDs must be unique within the output | block | critical |
| no-conflicting-enums | Same field cannot have conflicting enum values across items | flag | high |
| entity-consistency | Same entity must be referenced consistently across items | flag | high |

## File Structure

```
gr-L3-consistency-checker/
├── colang/
│   ├── config.yml
│   ├── prompts.yml
│   ├── actions.py
│   └── rails/
│       └── consistency_checker.co
├── spec.yaml
├── guardrail.py
└── README.md
```

## Usage

```yaml
rails:
  output:
    flows:
      - check output consistency
```
