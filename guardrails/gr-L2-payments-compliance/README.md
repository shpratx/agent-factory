# gr-L2-payments-compliance

**Layer:** L2 Domain (applies to payments domain agents)  
**Triggers on:** post_execution (output rail)  
**On fail:** Block and escalate  
**Implementation:** Colang + Python actions

## What does it do?

Validates that payments domain agent outputs correctly reference PSD2/SCA regulations, use accurate article numbers, include SCA requirements where applicable, and use terminology consistent with the payments knowledge base. Prevents regulatory misinformation in payments-related outputs.

## How It Works

```
Agent generates payments output
        ↓
┌─────────────────────────────────────┐
│  validate_payments_references (Py)  │
│                                     │
│  ✓ PSD2 article numbers valid?      │
│  ✓ CNP transactions include SCA?    │
│  ✓ Regulation names real?           │
│                                     │
│  Invalid → BLOCK + ESCALATE         │
└─────────────────────────────────────┘
        ↓ (pass)
┌─────────────────────────────────────┐
│  self_check_output (LLM)           │
│  Semantic compliance check          │
│  Terminology accuracy               │
└─────────────────────────────────────┘
        ↓ (compliant)
Output delivered
```

## Rules

| Rule | Description | Action | Severity |
|------|-------------|--------|----------|
| regulatory-accuracy | All cited regulations must exist and be correctly referenced | block | critical |
| sca-requirements | Payment stories must include SCA where applicable | flag | high |
| terminology-check | Domain terms must match payments KB definitions | flag | medium |

## File Structure

```
gr-L2-payments-compliance/
├── colang/
│   ├── config.yml
│   ├── prompts.yml
│   ├── actions.py
│   └── rails/
│       └── payments_compliance.co
├── spec.yaml
├── guardrail.py
└── README.md
```

## Usage

```yaml
rails:
  output:
    flows:
      - check payments compliance
```
