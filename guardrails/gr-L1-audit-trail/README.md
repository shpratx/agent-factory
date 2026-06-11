# gr-L1-audit-trail

**Layer:** L1 Enterprise (applies to ALL agents, cannot be overridden)  
**Triggers on:** post_execution (output rail)  
**On fail:** Block output (missing fields) or Warn (persistence failure)  
**Implementation:** Pure Colang — no Python actions required

## What does it do?

This guardrail ensures every agent execution leaves a traceable, compliant audit record. It operates in two phases:

1. **Validates completeness** — Before output is delivered, the LLM checks that all traceability fields exist in the agent's response: who ran (agent_id, version), what happened (execution_id, output type), where input came from (source, parameters), and which schema version was used. If any field is missing, output is **blocked** — it never reaches the user or downstream agent.

2. **Persists a structured audit record** — After validation passes, a Python action extracts the traceability fields, masks any PII in input parameters (emails → [EMAIL], phones → [PHONE], etc.), and writes a structured JSON record to the configured audit store. If persistence fails, output is still delivered but an operational alert is raised.

The result: every agent execution can be traced end-to-end — from who triggered it, through what was produced, to where the output went. This is essential for regulatory compliance, incident investigation, and operational monitoring.

## How It Works

Uses NeMo Guardrails' built-in `self_check_output` mechanism. The LLM evaluates the output against the `prompts.yml` criteria — no custom Python code needed.

```
Agent generates output
        ↓
┌─────────────────────────────────────────┐
│  check audit trail completeness         │
│                                         │
│  LLM evaluates (via prompts.yml):       │
│  ✓ agent_id present (L[0-4]-*-agent)?   │
│  ✓ execution_id present (exec-*)?       │
│  ✓ agent_version present (x.y.z)?       │
│  ✓ input_summary.source valid enum?     │
│  ✓ input_summary.parameters non-empty?  │
│  ✓ output.type valid enum?              │
│  ✓ output.schema_version present?       │
│                                         │
│  ANY missing → BLOCK output             │
└─────────────────────────────────────────┘
        ↓ (all present)
┌─────────────────────────────────────────┐
│  log audit record                       │
│                                         │
│  LLM extracts and formats:              │
│  AUDIT | agent_id=X | exec_id=Y | ...   │
│  PII in parameters is masked            │
│                                         │
│  Captured in NeMo conversation log      │
└─────────────────────────────────────────┘
        ↓
Output delivered
```

## Fields Validated

| Field | Format | Fail Action |
|-------|--------|-------------|
| `agent_id` | `L[0-4]-*-agent` | Block |
| `execution_id` | `exec-*` | Block |
| `agent_version` | `x.y.z` (semver) | Block |
| `input_summary.source` | `agent_output` / `direct_input` / `file_upload` | Block |
| `input_summary.parameters` | Non-empty object | Block |
| `output.type` | Valid enum (story, epic, test_case, code, etc.) | Block |
| `output.schema_version` | Non-empty string | Block |

## File Structure

```
gr-L1-audit-trail/
├── colang/
│   ├── config.yml          # Rail configuration (2 output flows)
│   ├── prompts.yml         # LLM prompts for validation + audit summary
│   └── rails/
│       └── audit_trail.co  # Colang flow definitions
├── spec.yaml               # Guardrail specification
├── guardrail.py            # Standalone Python impl (for non-NeMo runtimes)
└── README.md               # This file
```

## Usage

### 1. Include in your agent's guardrails config

```yaml
rails:
  output:
    flows:
      - check audit trail completeness
      - log audit record
```

### 2. Load the configuration

```python
from nemoguardrails import LLMRails, RailsConfig

config = RailsConfig.from_path("./gr-L1-audit-trail/colang")
rails = LLMRails(config)
```

### 3. Place last in the output rail chain

The audit trail should run **after** all other output validations:

```yaml
rails:
  output:
    flows:
      - check output schema           # First: structure valid?
      - check output pii              # Second: safe?
      - check output hallucination    # Third: grounded?
      - check audit trail completeness # Last: log it
      - log audit record
```

This ensures only valid, safe output gets an audit record.

## Audit Summary Format

The LLM produces a one-line audit summary captured in NeMo's conversation log:

```
AUDIT | agent_id=L1-inception-template-agent | exec_id=exec-abc123 | version=1.0.0 | source=direct_input | type=fact | items=1 | status=success
```

PII in parameters is masked:
```
AUDIT | ... | params={email: [EMAIL], topic: "honeybees"} | ...
```

## Production Persistence

For production audit stores beyond NeMo's conversation log, add a Python action file (`actions.py`) that persists to:
- **AWS:** DynamoDB, S3, CloudWatch Logs
- **Azure:** Cosmos DB, Blob Storage  
- **GCP:** BigQuery, Cloud Logging

See `guardrail.py` for a standalone Python implementation that can be used with non-NeMo runtimes.
