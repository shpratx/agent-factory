# gr-L3-agent-rate-limit

**Layer:** L3 Project (applies to ALL agents)  
**Triggers on:** runtime (before tool/agent calls)  
**On fail:** Throttle then block  
**Implementation:** Colang + Python actions

## What does it do?

Limits the number of tool calls and downstream agent invocations per execution. Prevents agents from making excessive calls that could overload systems, generate unexpected costs, or indicate runaway behavior. Enforces cooldown intervals between repeated identical tool calls.

## How It Works

```
Agent requests tool/agent call
        ↓
┌─────────────────────────────────────┐
│  check_rate_limits (Python)         │
│                                     │
│  ✓ Total tool calls within max?     │
│  ✓ Agent invocations within max?    │
│  ✓ Cooldown respected?              │
│                                     │
│  Exceeded → BLOCK                   │
│  Cooldown active → THROTTLE         │
└─────────────────────────────────────┘
        ↓ (within limits)
Tool/agent call proceeds
```

## Rules

| Rule | Description | Action | Severity |
|------|-------------|--------|----------|
| max-tool-calls | Agent cannot exceed configured max tool calls per execution | block | high |
| max-agent-calls | Orchestrator cannot invoke more than configured downstream agents | block | high |
| cooldown | Enforce minimum interval between repeated tool calls | flag | medium |

## File Structure

```
gr-L3-agent-rate-limit/
├── colang/
│   ├── config.yml
│   ├── prompts.yml
│   ├── actions.py
│   └── rails/
│       └── agent_rate_limit.co
├── spec.yaml
├── guardrail.py
└── README.md
```

## Usage

```yaml
rails:
  input:
    flows:
      - check agent rate limit
```
