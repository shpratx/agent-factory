# gr-L3-confidence-gate

**Layer:** L3 Project (applies to ALL agents)  
**Triggers on:** post_execution (output rail)  
**On fail:** Escalate to HITL  
**Implementation:** Colang + Python actions

## What does it do?

Enforces confidence thresholds on agent output items. Items below 0.5 confidence are blocked entirely. Items between 0.5-0.7 are escalated to human-in-the-loop (HITL) review. Ensures low-confidence AI outputs never reach downstream consumers without human oversight.

## How It Works

```
Agent generates output
        ↓
┌─────────────────────────────────────┐
│  check_confidence_scores (Python)   │
│                                     │
│  For each item:                     │
│  ✓ Confidence score present?        │
│  ✓ Confidence ≥ 0.5? (else block)   │
│  ✓ Confidence ≥ 0.7? (else HITL)    │
│                                     │
│  < 0.5 → BLOCK                      │
│  0.5-0.7 → ESCALATE to HITL         │
│  ≥ 0.7 → PASS                       │
└─────────────────────────────────────┘
        ↓ (pass/escalate)
┌─────────────────────────────────────┐
│  self_check_output (LLM)           │
│  Confidence realism check           │
└─────────────────────────────────────┘
        ↓
Output delivered (or escalated)
```

## Rules

| Rule | Description | Action | Severity |
|------|-------------|--------|----------|
| min-confidence | Items with confidence < 0.7 trigger HITL escalation | flag | high |
| low-confidence-block | Items with confidence < 0.5 are blocked entirely | block | critical |
| confidence-present | Every item must have a confidence score | block | high |

## File Structure

```
gr-L3-confidence-gate/
├── colang/
│   ├── config.yml
│   ├── prompts.yml
│   ├── actions.py
│   └── rails/
│       └── confidence_gate.co
├── spec.yaml
├── guardrail.py
└── README.md
```

## Usage

```yaml
rails:
  output:
    flows:
      - check confidence gate
```
