# gr-L1-secrets-protection

**Layer:** L1 Enterprise (applies to ALL agents)  
**Triggers on:** post_execution (output rail)  
**On fail:** Block and alert  
**Implementation:** Colang + Python actions

## What does it do?

Prevents credentials, API keys, tokens, and internal system details from appearing in agent output. Scans for known secret formats (AWS keys, OpenAI keys, JWTs, private keys) plus internal URLs that could expose infrastructure. Any match immediately blocks output delivery and raises an alert.

## How It Works

```
Agent generates output
        ↓
┌─────────────────────────────────────┐
│  detect_secrets (Python)            │
│                                     │
│  ✓ AWS/OpenAI/Stripe/GH keys?      │
│  ✓ Password/token assignments?      │
│  ✓ Private key blocks?              │
│  ✓ JWT tokens?                      │
│  ✓ Internal/localhost URLs?         │
│  ✓ Private IP addresses?            │
│                                     │
│  ANY match → BLOCK + ALERT          │
└─────────────────────────────────────┘
        ↓ (clean)
┌─────────────────────────────────────┐
│  self_check_output (LLM)           │
│  Semantic secret detection          │
└─────────────────────────────────────┘
        ↓ (clean)
Output delivered
```

## Rules

| Rule | Description | Action | Severity |
|------|-------------|--------|----------|
| api-key-patterns | Block strings matching API key formats | block | critical |
| credential-patterns | Block password, token, secret patterns | block | critical |
| internal-urls | Block internal system URLs and endpoints | block | high |

## File Structure

```
gr-L1-secrets-protection/
├── colang/
│   ├── config.yml
│   ├── prompts.yml
│   ├── actions.py
│   └── rails/
│       └── secrets_protection.co
├── spec.yaml
├── guardrail.py
└── README.md
```

## Usage

```yaml
rails:
  output:
    flows:
      - check secrets protection
```
