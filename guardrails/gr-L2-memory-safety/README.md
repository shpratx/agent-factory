# gr-L2-memory-safety

**Layer:** L2 Domain (applies to agents with memory access)  
**Triggers on:** runtime (before memory operations)  
**On fail:** Block and alert  
**Implementation:** Colang + Python actions

## What does it do?

Prevents memory poisoning, cross-agent memory leakage, and unauthorized writes. Ensures agents can only access their own episodic memory, enforces write permissions, and scans content being written for adversarial injection patterns that could corrupt the memory store.

## How It Works

```
Agent requests memory operation
        ↓
┌─────────────────────────────────────┐
│  validate_memory_operation (Python) │
│                                     │
│  ✓ Write permission granted?        │
│  ✓ Accessing own memory only?       │
│  ✓ No cross-agent access?           │
│  ✓ Content free of injection?       │
│                                     │
│  Violation → BLOCK + ALERT          │
└─────────────────────────────────────┘
        ↓ (safe)
┌─────────────────────────────────────┐
│  self_check_input (LLM)            │
│  Semantic poisoning detection       │
└─────────────────────────────────────┘
        ↓ (safe)
Memory operation proceeds
```

## Rules

| Rule | Description | Action | Severity |
|------|-------------|--------|----------|
| write-permission | Only agents with memory_write permission can store to long-term memory | block | critical |
| cross-agent-isolation | Agent cannot read another agent's episodic memory without explicit share | block | high |
| poisoning-detection | Detect and block adversarial content injection into memory stores | flag | high |

## File Structure

```
gr-L2-memory-safety/
├── colang/
│   ├── config.yml
│   ├── prompts.yml
│   ├── actions.py
│   └── rails/
│       └── memory_safety.co
├── spec.yaml
├── guardrail.py
└── README.md
```

## Usage

```yaml
rails:
  input:
    flows:
      - check memory safety
```
