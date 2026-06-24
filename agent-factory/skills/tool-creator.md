---
name: tool-creator
description: Standard structure, patterns, and conventions for creating tools in the Agent Factory. Use this whenever asked to create a new tool — apply this exact structure, naming, spec format, and implementation pattern.
trigger: When the user asks to create a tool, implement a tool integration, or asks about tool structure and standards.
---

# Tool Creator Skill

## Naming Convention

```
tool-L{layer}-{platform}-{action}
```

- `L1` = Enterprise (shared across all agents — Jira, GitHub, Confluence, etc.)
- `L2` = Domain (domain-specific systems — ECDA portal, CRA API, payment gateway)
- `L3` = Project (project-specific integrations)
- `L4` = Squad (team-specific tools)
- `{platform}` = target system (jira, github, confluence, sendgrid, ecda)
- `{action}` = kebab-case operation (create-issue, fetch-user, send-email)

**Reference:** See `01-agent-development-naming-standard.html` for the full naming guide.

Patterns per layer:
- L1: `tool-L1-{platform}-{action}`
- L2: `tool-L2-{domain}-{platform}-{action}`
- L3: `tool-L3-{project}-{platform}-{action}`
- L4: `tool-L4-{squad}-{platform}-{action}`

Examples:
- `tool-L1-jira-create-issue`
- `tool-L1-jira-fetch-issue`
- `tool-L1-github-create-pr`
- `tool-L1-sendgrid-send-email`
- `tool-L2-payments-swift-send-message`
- `tool-L2-ecda-submit-attendance`
- `tool-L3-kyc-lexisnexis-verify-identity`
- `tool-L4-squad-alpha-jenkins-trigger-build`

## Core Principles

| Principle | Standard |
|-----------|----------|
| Single operation | One tool = one API call. Never batch multiple operations. |
| Secrets via SDK | Zero hardcoded credentials. `secrets.get("{platform}")` at runtime. |
| Structured result | Always return `ToolResult(success, data, error)` |
| Timeout | 30s default on all HTTP calls |
| Input validation | Validate all parameters before making the API call |
| Idempotent creates | Check-before-create or use idempotency keys |
| Error handling | Map API errors to structured ToolResult.error (never raw stack traces) |
| Mostly L1 | Shared platform tools (Jira, GitHub, Confluence) are L1. Only domain-specific APIs are L2+. |

## Folder Structure

```
tools/tool-L{n}-{platform}-{action}/
├── spec.yaml              # Tool specification (interface, credentials, resilience)
├── tool.py                # Implementation (Python)
├── tool_test.py           # Unit tests (mocked API calls)
└── README.md              # What it does, parameters, example usage
```

## spec.yaml Template

```yaml
spec_version: "1.0"
artifact_type: tool
metadata:
  name: tool-L{n}-{platform}-{action}
  version: "1.0.0"
  layer: L{n}
  owner: agentic-ai-coe

purpose:
  description: "{What this tool does in one sentence}"
  platform: {platform}
  operation: {action}

interface:
  parameters:
    {param_1}: {type: string, required: true, description: "{what}"}
    {param_2}: {type: string, required: true, pattern: "{regex}"}
    {param_3}: {type: array, items: {type: string}, default: []}

  returns:
    type: ToolResult
    fields:
      success: boolean
      data: {field_1: type, field_2: type}
      error: {type: string, nullable: true}

credentials:
  source: secrets-sdk
  path: "{platform}"
  fields_used: [base_url, api_token]

identity:
  tool_id: "tool-{name}-001"
  role: tool-executor

  invocable_by:
    roles: [content-generator, orchestrator]
    agents: [{allowed-agent-1}]

  permissions:
    operation: read|write|delete
    platform: {platform}
    scope: "org-level|project-level|resource-level"

  credential_scoping:
    method: org-from-context
    vault_path_template: "/secrets/{org_id}/{platform}"

resilience:
  timeout_seconds: 30
  retry: {max: 2, backoff: exponential, retry_on: [timeout, 429, 502, 503]}
  circuit_breaker: {failure_threshold: 5, reset_seconds: 60}

security:
  input_validation: "All parameters validated before API call"
  output_sanitization: "Raw API errors never exposed; mapped to ToolResult.error"
  logging: "Input logged (PII masked); output summary logged; credentials never logged"
```

## Implementation Template (Python)

```python
"""L{n}-{platform}-{action}: {description}"""
import httpx
from dataclasses import dataclass
from typing import Any, Optional

@dataclass
class ToolResult:
    success: bool
    data: Optional[dict] = None
    error: Optional[str] = None

class Tool:
    name = "L{n}-{platform}-{action}"
    timeout = 30

    def __init__(self, secrets: dict):
        self.base_url = secrets["base_url"]
        self.token = secrets["api_token"]

    def execute(self, **params) -> ToolResult:
        # 1. Validate input
        if not params.get("required_field"):
            return ToolResult(success=False, error="required_field is required")

        # 2. Make API call
        try:
            response = httpx.post(
                f"{self.base_url}/api/endpoint",
                headers={"Authorization": f"Bearer {self.token}"},
                json=params,
                timeout=self.timeout,
            )
            response.raise_for_status()
        except httpx.TimeoutException:
            return ToolResult(success=False, error="API timeout after 30s")
        except httpx.HTTPStatusError as e:
            return ToolResult(success=False, error=f"API error: {e.response.status_code}")

        # 3. Return structured result
        data = response.json()
        return ToolResult(success=True, data={"id": data["id"], "key": data["key"]})
```

## README.md Template

```markdown
# L{n}-{platform}-{action}

## What does it do?

{One paragraph description}

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| {param} | string | ✓ | {description} |

## Returns

| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Whether the operation succeeded |
| data.{field} | string | {description} |
| error | string | Error message (null on success) |

## Example

```python
result = tool.execute(project_key="PROJ", summary="New story", issue_type="Story")
# ToolResult(success=True, data={"key": "PROJ-123", "id": "10001"})
```

## Error Handling

| Error | Cause | Behaviour |
|-------|-------|-----------|
| Timeout | API didn't respond in 30s | Returns error, retries up to 2x |
| 429 | Rate limited | Exponential backoff retry |
| 401 | Invalid credentials | Returns error, no retry |
| 404 | Resource not found | Returns error, no retry |
```

## Permission Model

Tools use least-privilege access:

| Permission | Who Can Invoke | Example |
|------------|---------------|---------|
| `read` | Any agent with tool in `tools_allowed` | fetch-issue, get-user |
| `write` | Orchestrator agents only (by default) | create-issue, send-email |
| `delete` | Explicitly allowlisted agents only | delete-issue (rare) |

Agents reference tools in their spec:
```yaml
# In agent spec
identity:
  permissions:
    tools_allowed: [L1-jira-fetch-issue, L1-jira-create-issue]
    tools_denied: [L1-jira-delete-issue]
```

## Resilience Pattern

Every tool MUST implement:

1. **Timeout** — 30s default, configurable per tool
2. **Retry** — Max 2 retries with exponential backoff for transient errors (timeout, 429, 502, 503)
3. **Circuit breaker** — After 5 consecutive failures, open circuit for 60s (return error immediately)
4. **Idempotency** — For write operations, check-before-create or use platform idempotency keys

## Security Rules

- Credentials loaded from secrets SDK at runtime (never hardcoded, never in env files)
- Credential path scoped per organisation: `/secrets/{org_id}/{platform}`
- Input parameters validated before any API call
- API error responses sanitised — never expose raw stack traces or internal URLs
- All tool executions logged: input (PII masked), output summary, duration, status
- Credentials NEVER appear in logs

## Testing Pattern

```python
# tool_test.py
from unittest.mock import patch, MagicMock

def test_create_issue_success():
    tool = Tool(secrets={"base_url": "https://jira.example.com", "api_token": "test"})
    with patch("httpx.post") as mock_post:
        mock_post.return_value = MagicMock(
            status_code=201,
            json=lambda: {"id": "10001", "key": "PROJ-123"}
        )
        result = tool.execute(project_key="PROJ", summary="Test", issue_type="Story")
        assert result.success is True
        assert result.data["key"] == "PROJ-123"

def test_create_issue_timeout():
    tool = Tool(secrets={"base_url": "https://jira.example.com", "api_token": "test"})
    with patch("httpx.post", side_effect=httpx.TimeoutException("timeout")):
        result = tool.execute(project_key="PROJ", summary="Test", issue_type="Story")
        assert result.success is False
        assert "timeout" in result.error
```

## Checklist Before Publishing

- [ ] Name follows `L{n}-{platform}-{action}` convention
- [ ] spec.yaml has interface (parameters + returns), credentials, resilience
- [ ] Implementation validates input before API call
- [ ] Returns `ToolResult(success, data, error)` — never raises exceptions to caller
- [ ] Timeout configured (30s default)
- [ ] Retry logic for transient errors (429, 502, 503, timeout)
- [ ] Credentials from secrets SDK (not hardcoded)
- [ ] Error messages sanitised (no internal URLs or stack traces)
- [ ] Unit tests with mocked API calls
- [ ] README documents parameters, returns, errors, and example usage

## Guardrails That Apply to Tools

| Guardrail | What It Enforces |
|-----------|-----------------|
| gr-L2-tool-permissions | Agents can only invoke tools in their `tools_allowed` list |
| gr-L3-agent-rate-limit | Max tool calls per execution (prevents runaway loops) |
| gr-L3-cost-control | Token/invocation budgets (tools count toward invocation cap) |
| gr-L1-audit-trail | Every tool execution logged with input/output for traceability |

Tools themselves don't implement guardrails — guardrails run in the agent execution layer and gate tool invocations before they reach the tool.
