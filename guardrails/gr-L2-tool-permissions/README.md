# gr-L2-tool-permissions

**Layer:** L2 Domain (applies to ALL agents)  
**Triggers on:** runtime (before tool execution)  
**On fail:** Block and log  
**Implementation:** Colang + Python actions

## What does it do?

Enforces least-privilege tool access. Before any tool invocation, checks that the calling agent has explicit permission to use that tool, the tool is not on the deny list, and the call is within the agent's organizational scope. Prevents privilege escalation and unauthorized system access.

## How It Works

```
Agent requests tool call
        ↓
┌─────────────────────────────────────┐
│  check_tool_allowed (Python)        │
│                                     │
│  ✓ Tool in agent's allowed list?    │
│  ✓ Tool NOT in denied list?         │
│  ✓ Within agent's org_scope?        │
│                                     │
│  Not permitted → BLOCK + LOG        │
└─────────────────────────────────────┘
        ↓ (permitted)
Tool executes
```

## Rules

| Rule | Description | Action | Severity |
|------|-------------|--------|----------|
| allowed-tools | Agent can only call tools in its tools_allowed list | block | critical |
| denied-tools | Agent must never call tools in its tools_denied list | block | critical |
| scope-check | Tool calls must be within agent's org_scope | block | high |

## File Structure

```
gr-L2-tool-permissions/
├── colang/
│   ├── config.yml
│   ├── prompts.yml
│   ├── actions.py
│   └── rails/
│       └── tool_permissions.co
├── spec.yaml
├── guardrail.py
└── README.md
```

## Usage

```yaml
rails:
  input:
    flows:
      - check tool permissions
```
