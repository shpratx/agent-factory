# gr-L2-policy-enforcement

**Layer:** L2 Domain (applies to domain agents)  
**Triggers on:** pre_execution + post_execution (input + output rails)  
**On fail:** Block with OUT_OF_SCOPE  
**Implementation:** Colang + Python actions

## What does it do?

Enforces domain-specific topic adherence and policy rules. Ensures agents only respond to requests within their declared scope, and that outputs comply with domain-specific business policies. Out-of-scope requests receive a clear OUT_OF_SCOPE response rather than hallucinated answers.

## How It Works

```
User sends request
        ↓
┌─────────────────────────────────────┐
│  check topic adherence (LLM)       │
│                                     │
│  ✓ Within declared domain scope?    │
│  ✓ Agent designed to handle this?   │
│                                     │
│  Out of scope → BLOCK              │
└─────────────────────────────────────┘
        ↓ (in scope)
Agent processes → generates output
        ↓
┌─────────────────────────────────────┐
│  check policy compliance (LLM)     │
│                                     │
│  ✓ Stays within domain boundaries?  │
│  ✓ Complies with business rules?    │
│  ✓ No claims outside authority?     │
│                                     │
│  Violation → BLOCK                  │
└─────────────────────────────────────┘
        ↓ (compliant)
Output delivered
```

## Rules

| Rule | Description | Action | Severity |
|------|-------------|--------|----------|
| topic-adherence | Agent must stay within its declared domain scope | block | high |
| off-topic-refusal | Return OUT_OF_SCOPE for requests outside domain | block | high |
| policy-compliance | Output must comply with domain-specific business policies | flag | medium |

## File Structure

```
gr-L2-policy-enforcement/
├── colang/
│   ├── config.yml
│   ├── prompts.yml
│   ├── actions.py
│   └── rails/
│       └── policy_enforcement.co
├── spec.yaml
├── guardrail.py
└── README.md
```

## Usage

```yaml
rails:
  input:
    flows:
      - check topic adherence
  output:
    flows:
      - check policy compliance
```
