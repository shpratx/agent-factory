# gr-L4-reasoning-validator

**Layer:** L4 Squad (applies to configured agents)  
**Triggers on:** post_execution (output rail)  
**On fail:** Retry once  
**Implementation:** Colang + Python actions

## What does it do?

Validates that the reasoning field on each output item is present, meets minimum length, and contains substantive decision rationale. Prevents empty, generic, or filler reasoning from passing through. Ensures every output item explains WHY it was produced, referencing input data or KB sources.

## How It Works

```
Agent generates output
        ↓
┌─────────────────────────────────────┐
│  validate_reasoning (Python)        │
│                                     │
│  For each item:                     │
│  ✓ metadata.reasoning present?      │
│  ✓ Length ≥ 20 characters?           │
│  ✓ Not generic filler?              │
│                                     │
│  Missing/short → BLOCK + RETRY      │
└─────────────────────────────────────┘
        ↓ (pass)
┌─────────────────────────────────────┐
│  self_check_output (LLM)           │
│  Reasoning quality assessment       │
│  References input/KB? Has rationale?│
└─────────────────────────────────────┘
        ↓ (quality pass)
Output delivered
```

## Rules

| Rule | Description | Action | Severity |
|------|-------------|--------|----------|
| reasoning-present | metadata.reasoning must not be null or empty | block | high |
| min-length | Reasoning must be at least 20 characters | flag | medium |
| contains-rationale | Reasoning should reference input data or KB sources | flag | medium |

## File Structure

```
gr-L4-reasoning-validator/
├── colang/
│   ├── config.yml
│   ├── prompts.yml
│   ├── actions.py
│   └── rails/
│       └── reasoning_validator.co
├── spec.yaml
├── guardrail.py
└── README.md
```

## Usage

```yaml
rails:
  output:
    flows:
      - check reasoning quality
```
