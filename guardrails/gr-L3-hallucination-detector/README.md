# gr-L3-hallucination-detector

**Layer:** L3 Project (applies to content generator agents)  
**Triggers on:** post_execution (output rail)  
**On fail:** Retry with stricter grounding  
**Implementation:** Colang + Python actions

## What does it do?

Checks that agent outputs are grounded in input data and attached knowledge bases. Detects fabricated claims, invented statistics, fake references, and ungrounded entities. Combines pattern-based detection (numeric claims without citations) with LLM semantic grounding verification.

## How It Works

```
Agent generates output
        ↓
┌─────────────────────────────────────┐
│  detect_fabrication_patterns (Py)   │
│                                     │
│  ✓ Numeric claims have citations?   │
│  ✓ No vague "study shows" claims?   │
│  ✓ URLs from known KB sources?      │
│                                     │
│  Fabrication → BLOCK + RETRY        │
└─────────────────────────────────────┘
        ↓ (pass)
┌─────────────────────────────────────┐
│  self_check_output (LLM)           │
│  Full groundedness evaluation       │
│  Every claim traced to source       │
└─────────────────────────────────────┘
        ↓ (grounded)
Output delivered
```

## Rules

| Rule | Description | Action | Severity |
|------|-------------|--------|----------|
| groundedness | Every claim must trace to input data or attached KB | block | critical |
| fabrication-patterns | Detect invented entities, statistics, or references | block | critical |
| confidence-correlation | Low-confidence items must have explicit uncertainty markers | flag | medium |

## File Structure

```
gr-L3-hallucination-detector/
├── colang/
│   ├── config.yml
│   ├── prompts.yml
│   ├── actions.py
│   └── rails/
│       └── hallucination_detector.co
├── spec.yaml
├── guardrail.py
└── README.md
```

## Usage

```yaml
rails:
  output:
    flows:
      - check hallucination
```
