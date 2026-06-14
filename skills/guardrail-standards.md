---
name: guardrail-standards
description: Standard structure, patterns, and conventions for creating guardrails in the Agent Factory. Use this whenever asked to create, modify, or review a guardrail — apply this exact structure, naming, and implementation pattern.
trigger: When the user asks to create a guardrail, implement a guardrail, review guardrail code, or asks about guardrail patterns and standards.
---

# Guardrail Standards

## Naming Convention

```
gr-L{layer}-{function}
```

- `gr-` prefix always
- `L1` = Enterprise (all agents, non-overridable)
- `L2` = Domain/LOB (domain-specific agents)
- `L3` = Project/Initiative (project-specific)
- `L4` = Squad/Local (team-specific)
- `{function}` = kebab-case description of what it does

Examples:
- `gr-L1-pii-detection`
- `gr-L2-payments-compliance`
- `gr-L3-hallucination-detector`
- `gr-L4-reasoning-validator`

## Folder Structure

Every guardrail lives in its own folder under `/guardrails/` with this structure:

```
gr-L{n}-{name}/
├── config.yml              # NeMo Guardrails rail configuration
├── prompts.yml             # LLM evaluation prompts (self_check_input/output)
├── gr-L{n}-{name}.co      # LLM-only Colang flow (uses self_check)
├── {name}.co               # Python-hybrid Colang flow (calls actions.py)
├── actions.py              # Deterministic Python implementation
├── spec.yaml               # Guardrail specification
└── README.md               # Documentation with testing instructions
```

Two `.co` files provide two modes:
- **LLM-only** (`gr-L{n}-{name}.co`): Pure Colang, uses `execute self_check_input`/`self_check_output`. No Python dependency.
- **Python-hybrid** (`{name}.co`): Calls Python actions for regex/deterministic checks + LLM for semantic checks.

## spec.yaml Template

```yaml
spec_version: "1.0"
artifact_type: guardrail
metadata:
  name: gr-L{n}-{name}
  version: "1.0.0"
  layer: L{n}
  owner: {owner}
  implementation: colang

purpose:
  description: "{What this guardrail does in one sentence}"

triggers_on:
  - pre_execution    # input rail
  - post_execution   # output rail

on_fail: {block | retry_once | escalate_to_hitl | kill_execution | warn_and_continue}
applies_to: {all_agents | domain_agents | content_generator_agents | configured_agents}

rules:
  - name: {rule-name}
    description: "{What this rule checks}"
    action: {block | flag}
    severity: {critical | high | medium}

evaluation:
  false_positive_threshold: 0.05
```

## config.yml Template

```yaml
models:
  - type: main
    engine: openai
    model: gpt-4.1

rails:
  input:       # for pre_execution guardrails
    flows:
      - {flow name}
  output:      # for post_execution guardrails
    flows:
      - {flow name}
```

## prompts.yml Template

```yaml
prompts:
  - task: self_check_input    # for input rails
    content: |
      User input: {{ user_input }}

      {Numbered list of specific checks}

      Answer "yes" if {pass condition}. Answer "no" if {fail condition}.

  - task: self_check_output   # for output rails
    content: |
      Agent output: {{ bot_response }}

      {Numbered list of specific checks}

      Answer "yes" if {pass condition}. Answer "no" if {fail condition}.
```

### Prompt Rules
- Always use numbered lists for checks (1, 2, 3...)
- Be specific about what constitutes a pass vs fail
- Include edge cases in the prompt ("Note: X is acceptable, Y is not")
- Answer format must be "yes"/"no" (or "block"/"escalate"/"kill" for multi-outcome)
- Use `{{ user_input }}` for input rails, `{{ bot_response }}` for output rails

## LLM-Only .co Template (gr-L{n}-{name}.co)

```colang
# gr-L{n}-{name} — LLM-Driven Colang Implementation
# Layer: L{n} — {title}
# Validation: LLM self_check (pure Colang)
# Python actions preserved in actions.py for reference/hybrid mode

define flow {flow name}
  """LLM validates {description} rules."""
  $result = execute self_check_{input|output}

  if not $result
    bot block {guardrail name}
    stop

define bot block {guardrail name}
  "{Block message explaining what failed and why}"
```

### Flow Rules
- Flow names use spaces (Colang convention): `check output pii`, `check input injection`
- Use `execute self_check_input` for input rails, `execute self_check_output` for output rails
- `if not $result` — NeMo returns boolean
- Always `stop` after blocking
- Bot messages should be clear about what failed

## Python-Hybrid .co Template ({name}.co)

```colang
define flow {flow name}
  """Deterministic check via Python action."""
  $result = execute {action_name}(text=$user_message)  # or output=$bot_message

  if $result
    bot block {guardrail name}
    stop

  # Optional: also run LLM check for semantic analysis
  $llm_result = execute self_check_{input|output}

  if not $llm_result
    bot block {guardrail name}
    stop
```

## actions.py Template

```python
"""{guardrail name}: {description}"""
import re
import json
import logging
from nemoguardrails.actions import action

logger = logging.getLogger("{guardrail-name}")

@action()
async def {action_name}(text: str) -> bool:
    """Return True if violation detected, False if clean."""
    # Deterministic regex/logic checks
    patterns = [...]
    for pattern in patterns:
        if re.search(pattern, text, re.IGNORECASE):
            return True
    return False
```

### Action Rules
- Always async (`async def`)
- Always decorated with `@action()`
- Return `bool` — True for detection (violation found), False for clean
- Use logging for observability (`logger.warning(...)`)
- Keep production integrations (DynamoDB, S3) commented

## README.md Template

```markdown
# gr-L{n}-{name}

**Layer:** L{n}
**Triggers on:** {pre_execution | post_execution | both}
**On fail:** {Block | Escalate | Kill | Warn}
**Implementation:** LLM-driven (Colang) — Python actions preserved for hybrid mode

## What does it do?

{Detailed explanation:}
- Why it exists
- What it catches (bullet list)
- When it fires (input/output/both) with clear explanation
- Why it matters (consequences of not having it)
- Scope notes if applicable

## How It Works

{ASCII flow diagram showing:}
- Entry point
- What's checked (numbered)
- Pass/fail outcomes
- What happens on each outcome

## File Structure

{Actual files with descriptions, noting the two .co modes}

## Testing

### Option 1: Prompt-Based Testing (LLM Judgement Only)
- Valid example (expected: "yes")
- Invalid example (expected: "no")

### Test Cases Matrix
| Test | Mutation | Expected |
|------|----------|----------|
| ... | ... | ... |

### Option 2: End-to-End Flow Testing (NeMo Guardrails SDK)
- Python code loading config and running pass/block scenarios

### Option 3: Python Unit Testing (standalone actions.py)
- Direct function calls
```

## Layering Rules

| Layer | Applies To | Overridable? | Examples |
|-------|-----------|--------------|----------|
| L1 Enterprise | ALL agents | ❌ Never | PII, injection, schema, secrets, content safety, audit |
| L2 Domain | Domain agents | ❌ Never (extends L1) | Compliance, policy, tool permissions, memory |
| L3 Project | Project agents | Can extend, not weaken | Hallucination, citations, confidence, consistency, cost, rate, loops |
| L4 Squad | Configured agents | Can extend, not weaken | Reasoning validator, custom format checks |

## Rail Types

| Type | When | Use For |
|------|------|---------|
| Input rail (`pre_execution`) | Before agent processes input | Injection, PII in input, validation, topic adherence, tool permissions |
| Output rail (`post_execution`) | After agent generates, before delivery | Schema, PII in output, secrets, hallucination, citations, confidence |
| Runtime rail | During execution | Loops, rate limits, cost control, memory safety |

## On-Fail Actions

| Action | Behaviour |
|--------|-----------|
| `block` | Stop delivery, return error message |
| `retry_once_then_escalate` | Retry generation once, escalate if still fails |
| `escalate_to_hitl` | Deliver to human review queue |
| `warn_and_continue` | Deliver output but log warning + alert ops |
| `kill_execution` | Terminate agent immediately |
| `throttle_then_block` | Slow down, block if persists |

## Cascade & Inheritance

Guardrails cascade downward — an L4 agent inherits ALL guardrails from L1 + L2 + L3 + L4:

```
L4 agent sees:
  └── L1 guardrails (enterprise — always applied, non-overridable)
  └── L2 guardrails (domain — if agent is in a domain)
  └── L3 guardrails (project — if agent is in a project)
  └── L4 guardrails (squad — agent's own squad rules)
```

Lower layers can ADD stricter guardrails but can NEVER weaken or remove inherited ones.

## Attaching Guardrails to an Agent

In the agent spec, guardrails are listed under `context.guardrails`:

```yaml
context:
  guardrails:
    - gr-L1-output-schema-validator   # L1 — auto-attached to all
    - gr-L1-pii-detection             # L1 — auto-attached to all
    - gr-L2-payments-compliance       # L2 — domain-specific
    - gr-L3-citation-validator        # L3 — project-specific
```

L1 guardrails are auto-attached by the platform even if omitted from the spec.

## Execution Order

When multiple guardrails fire on the same rail (input or output), they execute in this order:

1. **L1 guardrails** (enterprise) — first, most critical
2. **L2 guardrails** (domain) — second
3. **L3 guardrails** (project) — third
4. **L4 guardrails** (squad) — last

Within the same layer, order follows the sequence in `config.yml` flows list. If any guardrail blocks, subsequent guardrails do NOT execute — fail fast.

## Logic Inversion (Important)

The two .co modes use **opposite boolean logic**:

| Mode | Function returns | Meaning | Block condition |
|------|-----------------|---------|-----------------|
| **LLM-only** | `self_check_input`/`output` returns `True` | Input/output is SAFE | `if not $result` → block |
| **Python-hybrid** | `detect_pii()`, `detect_injection()` returns `True` | Violation FOUND | `if $result` → block |

Always check which mode you're in before writing the `if` condition.

## Guardrails vs Evaluations

Guardrails and evaluations are different mechanisms:

| | Guardrails | Evaluations |
|---|---|---|
| When | Inline, real-time | Post-hoc, async |
| Action | Block/pass (binary) | Score (0.0–1.0) |
| Purpose | Prevent bad output delivery | Measure quality over time |
| Reference | `context.guardrails[]` in agent spec | `quality.evaluation_rubric` in agent spec |

See `quality-gates-vs-evaluation.md` for full comparison.
