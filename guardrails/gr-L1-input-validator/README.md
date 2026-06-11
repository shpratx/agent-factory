# gr-L1-input-validator

**Layer:** L1 Enterprise (applies to ALL agents)  
**Triggers on:** pre_execution (input rail)  
**On fail:** Reject with error  
**Implementation:** Colang + Python actions

## What does it do?

Validates incoming requests match the expected structure before any agent processing begins. Checks three dimensions: field presence (are all required fields there?), type correctness (do values match declared types?), and length limits (are strings within bounds?). Any violation immediately rejects the request with a descriptive error.

## How It Works

```
User sends request
        ↓
┌─────────────────────────────────────┐
│  validate_input_structure (Python)  │
│                                     │
│  ✓ Required fields present?         │
│  ✓ Types match declarations?        │
│  ✓ String lengths within limits?    │
│                                     │
│  ANY fail → REJECT input            │
└─────────────────────────────────────┘
        ↓ (pass)
┌─────────────────────────────────────┐
│  self_check_input (LLM)            │
│  Semantic validation of structure   │
└─────────────────────────────────────┘
        ↓ (pass)
Agent processes request
```

## Rules

| Rule | Description | Action | Severity |
|------|-------------|--------|----------|
| required-fields | All required parameters must be present | block | critical |
| type-validation | All parameters must match declared types | block | high |
| length-limits | String fields must not exceed max_length | block | medium |

## File Structure

```
gr-L1-input-validator/
├── colang/
│   ├── config.yml
│   ├── prompts.yml
│   ├── actions.py
│   └── rails/
│       └── input_validator.co
├── spec.yaml
├── guardrail.py
└── README.md
```

## Usage

```yaml
rails:
  input:
    flows:
      - check input validation
```

```python
from nemoguardrails import LLMRails, RailsConfig

config = RailsConfig.from_path("./gr-L1-input-validator/colang")
rails = LLMRails(config)
```
