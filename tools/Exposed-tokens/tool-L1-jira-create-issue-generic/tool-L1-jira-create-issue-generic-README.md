# tool-L1-jira-create-issue-generic

## What does it do?

Creates one or more Jira issues from a structured JSON payload, converting their descriptions into Atlassian Document Format (ADF). Descriptions can be provided as plain strings or as structured dictionaries (key → string or list of strings), which are normalised to markdown-ish text then converted to ADF paragraphs and bullet lists. Cross-references matching the pattern `E\d+` (e.g. `E1`, `E1.2`) are auto-linked to already-created issues using a running `id_map`. Issues are created sequentially so earlier issues can be referenced as parents by later ones via their `parentKey` field.

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| inputJSON | object | ✓ | Top-level payload (see structure below) |

### `inputJSON` structure

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| projectKey | string | | Jira project key (e.g. `"GGMDEMOS"`). Falls back to the hard-coded `JIRA_PROJECT_KEY`. |
| issueType | string | | Default issue type (e.g. `"Task"`, `"Epic"`). Falls back to `"Epic"`. |
| userEmail | string | | Atlassian account email. Falls back to `JIRA_USER_EMAIL`. |
| apiToken | string | | Jira API token. Falls back to `JIRA_API_TOKEN` env var. |
| baseUrl | string | | Jira instance base URL (no trailing slash). Falls back to `JIRA_BASE_URL`. |
| issues | array | ✓ | List of issue objects (see below) |

### Each issue object

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| summary | string | ✓ | Issue title |
| description | string \| object | ✓ | Plain text or dict of `{heading: value}` pairs |
| issueType | string | | Overrides the default `issueType` for this issue |
| label | array[string] | | Labels to apply; `label[0]` is used as the logical ID for cross-linking |
| parentKey | string | | Real Jira key of the parent issue |

## Returns

| Value | Description |
|-------|-------------|
| `"<IssueType> created: <KEY>. jira_issue_link = <url>"` | One line per successfully created issue |
| `"Failed: <summary> → HTTP <code> \| Detail: <text>"` | One line per failed issue |
| `"Fatal error: <message>"` | Returned when the entire run aborts (e.g. unexpected exception) |

The return value is a newline-joined string of all per-issue results.

## Example

```python
from tool_L1_jira_create_issue_generic import JiraIssueCreator

tool = JiraIssueCreator()
result = tool._run({
    "projectKey": "MYPROJ",
    "issueType": "Task",
    "issues": [
        {
            "summary": "Set up CI pipeline",
            "description": "Configure GitHub Actions for automated testing.",
            "label": ["E1"]
        },
        {
            "summary": "Write unit tests",
            "description": {
                "goal": "Achieve 80% coverage",
                "steps": ["Add pytest", "Mock external calls", "Run coverage report"]
            },
            "label": ["E2"]
        }
    ]
})
print(result)
# Task created: MYPROJ-10. jira_issue_link = https://aavademo.atlassian.net/browse/MYPROJ-10
# Task created: MYPROJ-11. jira_issue_link = https://aavademo.atlassian.net/browse/MYPROJ-11
```

## Error Handling

| Error | Cause | Behaviour |
|-------|-------|-----------|
| Timeout | API didn't respond in 30 s | `RequestException` caught per-issue; appended as `"Failed: ..."` line |
| 401 Unauthorized | Invalid credentials | `not response.ok` branch; appended as `"Failed: ... → HTTP 401"` |
| 400 Bad Request | Invalid issue type or project key | `not response.ok` branch; Jira error detail included |
| 404 Not Found | Project key or parent key not found | `not response.ok` branch; detail included |
| Per-issue exception | Any unexpected error for one issue | `RequestException` caught; other issues continue processing |
| Fatal exception | Unrecoverable error (e.g. JSON parsing) | Entire `_run` returns `"Fatal error: ..."` |

## Security Notes

- `JIRA_BASE_URL`, `JIRA_USER_EMAIL`, and `JIRA_API_TOKEN` are currently **hardcoded** at the top of the file — this is a known security issue. Move them to a secrets manager before production use.
- Credentials can be overridden per-call via `inputJSON.userEmail`, `inputJSON.apiToken`, and `inputJSON.baseUrl`.
- The API token is used via HTTP Basic Auth (`HTTPBasicAuth`) — never logged.

## Resilience

| Concern | Configuration |
|---------|--------------|
| Timeout | 30 s per HTTP request |
| Retry | Max 2 retries with exponential backoff on transient errors |
| Circuit breaker | 5 consecutive failures → open for 60 s |
| Partial failure | Per-issue errors are isolated; other issues in the batch continue |
| Cross-linking | `id_map` built incrementally — earlier issues' keys available for later issues |
