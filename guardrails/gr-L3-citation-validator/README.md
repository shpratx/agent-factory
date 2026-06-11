# gr-L3-citation-validator

**Layer:** L3 Project (applies to content generator agents)  
**Triggers on:** post_execution (output rail)  
**On fail:** Block and retry  
**Implementation:** Colang + Python actions

## What does it do?

Ensures every output item has at least one resolvable citation pointing to an attached knowledge base or valid source document. Prevents uncited claims from reaching downstream consumers. Works alongside the hallucination detector to enforce evidence-based output.

## How It Works

```
Agent generates output
        ↓
┌─────────────────────────────────────┐
│  validate_citations (Python)        │
│                                     │
│  For each item:                     │
│  ✓ citation array non-empty?        │
│  ✓ source_reference present?        │
│  ✓ At least 1 citation per item?    │
│                                     │
│  Missing citation → BLOCK + RETRY   │
└─────────────────────────────────────┘
        ↓ (pass)
┌─────────────────────────────────────┐
│  self_check_output (LLM)           │
│  Citation relevance check           │
└─────────────────────────────────────┘
        ↓ (valid)
Output delivered
```

## Rules

| Rule | Description | Action | Severity |
|------|-------------|--------|----------|
| citation-present | Every item in output.items must have non-empty citation array | block | high |
| source-resolvable | citation.source_reference must resolve to an attached KB or valid source | block | high |
| min-citations | At least 1 citation per item | block | high |

## File Structure

```
gr-L3-citation-validator/
├── colang/
│   ├── config.yml
│   ├── prompts.yml
│   ├── actions.py
│   └── rails/
│       └── citation_validator.co
├── spec.yaml
├── guardrail.py
└── README.md
```

## Usage

```yaml
rails:
  output:
    flows:
      - check citation validity
```
