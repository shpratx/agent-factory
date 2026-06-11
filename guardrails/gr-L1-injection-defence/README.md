# gr-L1-injection-defence

**Layer:** L1 Enterprise (applies to ALL agents)  
**Triggers on:** pre_execution (input rail)  
**On fail:** Block and log  
**Implementation:** Colang + Python actions

## What does it do?

Detects and blocks prompt injection attempts before they reach agent processing. Uses a two-layer defence: deterministic regex matching for known injection patterns (fast, zero false negatives on known vectors), followed by LLM semantic analysis for novel/obfuscated attempts. Enforces the principle that the system prompt is the sole instruction source — all user content is treated as data.

## How It Works

```
User sends input
        ↓
┌─────────────────────────────────────┐
│  detect_injection_patterns (Python) │
│                                     │
│  ✓ Known override phrases?          │
│  ✓ Role redefinition attempts?      │
│  ✓ Boundary marker injection?       │
│  ✓ System prompt extraction?        │
│                                     │
│  ANY match → BLOCK immediately      │
└─────────────────────────────────────┘
        ↓ (no pattern match)
┌─────────────────────────────────────┐
│  self_check_input (LLM)            │
│  Semantic injection detection       │
│  Catches obfuscated/novel attempts  │
└─────────────────────────────────────┘
        ↓ (safe)
Agent processes request
```

## Rules

| Rule | Description | Action | Severity |
|------|-------------|--------|----------|
| pattern-match | Block known injection patterns (ignore previous, system:, you are now) | block | critical |
| instruction-boundary | Enforce system prompt as sole instruction source | block | critical |
| external-content | Treat all external content as untrusted data | flag | high |

## File Structure

```
gr-L1-injection-defence/
├── colang/
│   ├── config.yml
│   ├── prompts.yml
│   ├── actions.py
│   └── rails/
│       └── injection_defence.co
├── spec.yaml
├── guardrail.py
└── README.md
```

## Usage

```yaml
rails:
  input:
    flows:
      - check injection defence
```
