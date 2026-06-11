# gr-L1-output-schema-validator

**Layer:** L1 Enterprise (applies to ALL agents)  
**Triggers on:** post_execution (output rail)  
**On fail:** Retry once then escalate  
**Implementation:** Colang + Python actions

## What does it do?

Ensures every agent output conforms to the AgentOutput v1.0 contract. Validates structure (all required fields present), format (IDs match patterns), and completeness (items contain reasoning and citations). Non-compliant output is blocked from delivery.

## How It Works

```
Agent generates output
        ↓
┌─────────────────────────────────────┐
│  validate_output_schema (Python)    │
│                                     │
│  ✓ agent_id, execution_id format?   │
│  ✓ agent_version semver?            │
│  ✓ input_summary complete?          │
│  ✓ output.type valid enum?          │
│  ✓ items non-empty?                 │
│  ✓ Each item has reasoning+citation?│
│                                     │
│  ANY fail → BLOCK output            │
└─────────────────────────────────────┘
        ↓ (pass)
┌─────────────────────────────────────┐
│  self_check_output (LLM)           │
│  Semantic schema validation         │
└─────────────────────────────────────┘
        ↓ (pass)
Output delivered
```

## Rules

| Rule | Description | Action | Severity |
|------|-------------|--------|----------|
| schema-compliance | Output must match AgentOutput v1.0 schema | block | critical |
| required-fields | agent_id, agent_version, execution_id, input_summary, output must be present | block | critical |
| items-not-empty | output.items must not be empty unless handling failure | flag | high |
| field-presence | metadata.reasoning and metadata.citation must exist on each item | block | high |

## File Structure

```
gr-L1-output-schema-validator/
├── colang/
│   ├── config.yml
│   ├── prompts.yml
│   ├── actions.py
│   └── rails/
│       └── output_schema_validator.co
├── spec.yaml
├── guardrail.py
└── README.md
```

## Usage

```yaml
rails:
  output:
    flows:
      - check output schema compliance
```
