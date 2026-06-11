# gr-L1-pii-detection

**Layer:** L1 Enterprise (applies to ALL agents)  
**Triggers on:** pre_execution + post_execution (input + output rails)  
**On fail:** Mask and continue  
**Implementation:** Colang + Python actions

## What does it do?

Detects personally identifiable information in both input and output streams. Uses regex patterns for deterministic detection of emails, phone numbers, SSNs, credit cards, passport numbers, and addresses. Falls back to LLM analysis for name detection and context-dependent PII. Blocks content containing unmasked PII.

## How It Works

```
Input/Output text
        ↓
┌─────────────────────────────────────┐
│  detect_pii (Python)                │
│                                     │
│  ✓ Email patterns?                  │
│  ✓ Phone number patterns?           │
│  ✓ SSN patterns?                    │
│  ✓ Credit card patterns?            │
│  ✓ Passport patterns?               │
│  ✓ Address patterns?                │
│                                     │
│  ANY match → BLOCK                  │
└─────────────────────────────────────┘
        ↓ (clean)
┌─────────────────────────────────────┐
│  self_check (LLM)                  │
│  Name detection, contextual PII     │
└─────────────────────────────────────┘
        ↓ (clean)
Content passes through
```

## Rules

| Rule | Description | Action | Severity |
|------|-------------|--------|----------|
| pii-patterns | Detect email, phone, SSN, credit card, passport numbers | block | critical |
| name-detection | Flag real person names outside of role descriptions | flag | high |
| address-detection | Block real physical addresses in output | block | high |

## File Structure

```
gr-L1-pii-detection/
├── colang/
│   ├── config.yml
│   ├── prompts.yml
│   ├── actions.py
│   └── rails/
│       └── pii_detection.co
├── spec.yaml
├── guardrail.py
└── README.md
```

## Usage

```yaml
rails:
  input:
    flows:
      - check input pii
  output:
    flows:
      - check output pii
```
