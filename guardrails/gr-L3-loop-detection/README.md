# gr-L3-loop-detection

**Layer:** L3 Project (applies to ALL agents)  
**Triggers on:** runtime (continuous monitoring)  
**On fail:** Kill execution  
**Implementation:** Colang + Python actions

## What does it do?

Detects and kills infinite loops, excessive recursion, and runaway agent executions. Monitors action repetition counts, execution duration, and recursion depth. Immediately terminates execution when any threshold is breached to prevent resource exhaustion.

## How It Works

```
Agent action executed
        ↓
┌─────────────────────────────────────┐
│  detect_loops (Python)              │
│                                     │
│  ✓ Same action repeated > max?      │
│  ✓ Execution time > timeout?        │
│  ✓ Recursion depth > max?           │
│                                     │
│  Loop → KILL                         │
│  Timeout → KILL                      │
│  Recursion → KILL                    │
└─────────────────────────────────────┘
        ↓ (normal)
Action proceeds
```

## Rules

| Rule | Description | Action | Severity |
|------|-------------|--------|----------|
| max-iterations | Kill execution after N iterations of same action | block | critical |
| timeout | Kill execution after configured timeout | block | critical |
| recursion-depth | Block recursion deeper than configured max depth | block | high |

## File Structure

```
gr-L3-loop-detection/
├── colang/
│   ├── config.yml
│   ├── prompts.yml
│   ├── actions.py
│   └── rails/
│       └── loop_detection.co
├── spec.yaml
├── guardrail.py
└── README.md
```

## Usage

```yaml
rails:
  input:
    flows:
      - check loop detection
```
