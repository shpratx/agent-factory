# gr-L3-cost-control

**Layer:** L3 Project (applies to ALL agents)  
**Triggers on:** runtime (before execution)  
**On fail:** Kill execution  
**Implementation:** Colang + Python actions

## What does it do?

Enforces token and invocation budget caps per agent execution. Prevents runaway costs by tracking cumulative token usage and invocation counts within time windows. Issues warnings at 80% usage and blocks execution when budgets are exceeded.

## How It Works

```
Agent execution requested
        ↓
┌─────────────────────────────────────┐
│  check_budget_limits (Python)       │
│                                     │
│  ✓ Invocation count within cap?     │
│  ✓ Token usage within budget?       │
│  ✓ At 80%+ → warning               │
│  ✓ At 100% → kill                   │
│                                     │
│  Exceeded → KILL execution          │
│  80%+ → WARN and continue           │
└─────────────────────────────────────┘
        ↓ (within budget)
Agent executes
```

## Rules

| Rule | Description | Action | Severity |
|------|-------------|--------|----------|
| token-budget | Total tokens (input+output) must not exceed max_token_budget | block | high |
| invocation-cap | Agent cannot exceed max invocations per time window | block | high |
| cost-alert | Flag executions exceeding 80% of budget | flag | medium |

## File Structure

```
gr-L3-cost-control/
├── colang/
│   ├── config.yml
│   ├── prompts.yml
│   ├── actions.py
│   └── rails/
│       └── cost_control.co
├── spec.yaml
├── guardrail.py
└── README.md
```

## Usage

```yaml
rails:
  input:
    flows:
      - check cost budget
```
