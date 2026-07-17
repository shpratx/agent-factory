# Evaluation Framework — Architecture Overview

## Core Principle: Fewer Agents, Shared Context

The biggest token waste is passing the full source document + output + ground truth
to every agent separately. Store it once and pass only what each agent needs.

---

## Agent Design — Minimum 2 Agents

Instead of 3 separate agents, collapse to 2:

| Agent | Role | Description |
|---|---|---|
| **Agent 1** | Generator | Your existing agent — unchanged |
| **Agent 2** | Evaluator + Improver (combined) | Evaluates first, then improves on failure |

> The Evaluator and Improver can be one agent because they never run at the same time —
> evaluation happens first, then improvement. Combining them halves your agent count
> and eliminates one full context handoff.

---

## Flow

```
Input
  └─► Agent 1 (Generator)
        └─► Agent 2 (Evaluator)
              ├─► PASS ──► Final Output + Report
              └─► FAIL ──► Agent 2 (Improver mode)
                              └─► Back to Agent 2 (Evaluator) ──► Loop (max 3x)
```

### Happy Path
- Overall Score ≥ 70 **AND** zero hallucinated claims
- Return final output + full metric report
- Show `improvementInstructions` as "Suggestions for future runs"

### Non-Happy Path
- Overall Score < 70 **OR** hallucinated claims > 0
- Collect all failure signals and pass to Improver
- Improver fixes only what failed — never starts from scratch
- Re-evaluate using only the tools that previously failed
- Return best scoring version after max 3 iterations

---

## App Components

```
Tools:      3   similarity_checker, faithfulness_checker, llm_judge
Agents:     2   Generator (existing) + Evaluator/Improver (new)
Workflows:  1   evaluation_pipeline with branching gates
KB docs:    1   rubrics + scoring weights + improvement rules
Guardrails: 5   JSON, token cap, loop breaker, regression, truncation
```

---

## Token Budget Per Run

| Scenario | Tokens |
|---|---|
| Happy path — easy case (similarity only + judge) | ~1,000 |
| Happy path — normal case (all 3 tools) | ~1,400 |
| Non-happy path — 1 improvement iteration | ~2,800 |
| Non-happy path — 3 iterations (worst case) | ~5,200 |

---

## Short-Circuit Logic

```
IF similarity score > 0.85
  → skip faithfulness_checker
  → call llm_judge with confidence mode (shorter prompt)
  → saves 1 full LLM call on easy cases

IF hallucination rate > 0.5
  → skip llm_judge entirely
  → go straight to Improver
  → saves 1 full LLM call on bad cases
```
