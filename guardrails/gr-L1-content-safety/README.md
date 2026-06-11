# gr-L1-content-safety

**Layer:** L1 Enterprise (applies to ALL agents)  
**Triggers on:** pre_execution + post_execution (input + output rails)  
**On fail:** Block immediately  
**Implementation:** Colang + Python actions

## What does it do?

Blocks toxic, harmful, offensive, or unsafe content in both input and output streams. Combines deterministic keyword/pattern matching for known harmful content with LLM semantic analysis for nuanced toxicity detection. Ensures all agent interactions remain professional and safe.

## How It Works

```
Input/Output text
        ↓
┌─────────────────────────────────────┐
│  check_content_safety (Python)      │
│                                     │
│  ✓ Harmful instructions?            │
│  ✓ Hate speech / slurs?             │
│  ✓ Excessive profanity (≥3)?        │
│                                     │
│  ANY match → BLOCK                  │
└─────────────────────────────────────┘
        ↓ (clean)
┌─────────────────────────────────────┐
│  self_check (LLM)                  │
│  Semantic safety analysis           │
│  Violence, self-harm, illegal acts  │
└─────────────────────────────────────┘
        ↓ (safe)
Content passes through
```

## Rules

| Rule | Description | Action | Severity |
|------|-------------|--------|----------|
| toxicity-check | Block content scoring above toxicity threshold | block | critical |
| harmful-content | Block content promoting violence, self-harm, or illegal activity | block | critical |
| profanity-filter | Flag excessive profanity in professional context | flag | medium |

## File Structure

```
gr-L1-content-safety/
├── colang/
│   ├── config.yml
│   ├── prompts.yml
│   ├── actions.py
│   └── rails/
│       └── content_safety.co
├── spec.yaml
├── guardrail.py
└── README.md
```

## Usage

```yaml
rails:
  input:
    flows:
      - check input content safety
  output:
    flows:
      - check output content safety
```
