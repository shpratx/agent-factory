# tool-L1-jira-upload-epics

## What does it do?

Creates Jira Epics and child Stories (or any issue types) from a structured payload produced by the `L1-inception-jira-payload-converter-agent`. Descriptions are converted to Atlassian Document Format (ADF) with support for bold text, italic text, bullet lists, and automatic cross-reference hyperlinks. Parent links are resolved in a single pass using a logical ID map — e.g. `parentKey: "EP-01"` is replaced by the real Jira key once `EP-01` has been created. A `dry_run` mode builds and validates all payloads without posting to Jira. ADF is sanitised to remove empty nodes before every POST.

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| inputJSON | object | ✓ | Top-level payload (see structure below) |

### `inputJSON` structure

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| projectKey | string | | Jira project key (e.g. `"GGMDEMOS"`). Falls back to hard-coded `JIRA_PROJECT_KEY`. |
| issueType | string | | Default issue type. Falls back to `"Epic"`. Per-issue `issueType` overrides this. |
| userEmail | string | | Atlassian account email. Falls back to `JIRA_USER_EMAIL`. |
| apiToken | string | | Jira API token. Falls back to `JIRA_API_TOKEN` env var. |
| baseUrl | string | | Jira instance base URL (no trailing slash). Falls back to `JIRA_BASE_URL`. |
| issues | array | ✓ | Ordered list of issue objects — **epics must appear before their child features** so `parentKey` can be resolved in a single pass. |

### Each issue object

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| summary | string | ✓ | Issue title |
| description | string \| object | | Plain text, or `{heading: str/list[str]/dict}` normalised to markdown then converted to ADF |
| issueType | string | | Overrides the batch default for this issue |
| label | array[string] | | Labels to apply; `label[0]` is the **logical ID** (e.g. `"EP-01"`, `"F-01.1"`) used for cross-linking and parent resolution |
| parentKey | string | | Logical ID (e.g. `"EP-01"`) **or** a real Jira key — resolved to the actual key via `id_map` before posting |

> **Ordering rule:** Because `parentKey` is resolved in a single linear pass, parent issues (Epics) must be listed before their children (Stories/Features) in the `issues` array.

## Returns

| Value | Description |
|-------|-------------|
| `"[DRY RUN] <IssueType> '<summary>' -> <fake-key> (parent=<key>)"` | One line per issue in dry-run mode |
| `"<IssueType> created: <KEY>  (<summary>)"` | One line per successfully created issue |
| `"Failed: <summary> -> HTTP <code> \| Detail: <text>"` | One line per failed issue |
| `"Fatal error: <message>"` | Entire run aborted |

## Example

```python
from tool_L1_jira_upload_epics import JiraIssueCreator, create_issues

payload = {
    "projectKey": "MYPROJ",
    "issueType": "Epic",
    "issues": [
        {
            "summary": "EP-01: Platform Foundation",
            "issueType": "Epic",
            "label": ["EP-01", "S1"],
            "parentKey": None,
            "description": {
                "description": "Technical foundation for the Credit Coach agent.",
                "scope_in": ["Envoy agent registration", "Consent capture flow"],
                "scope_out": ["Score retrieval (see EP-02)"]
            }
        },
        {
            "summary": "F-01.1: Envoy Agent Registration",
            "issueType": "Story",
            "label": ["F-01.1"],
            "parentKey": "EP-01",   # resolved to real key after EP-01 is created
            "description": "Register Credit Coach as a specialist agent. Relates to EP-01."
        }
    ]
}

# Dry run (no Jira calls)
print(create_issues(payload, dry_run=True))
# [DRY RUN] Epic 'EP-01: Platform Foundation' -> MYPROJ-1 (parent=None)
# [DRY RUN] Story 'F-01.1: Envoy Agent Registration' -> MYPROJ-2 (parent=MYPROJ-1)

# Live run
print(create_issues(payload))
# Epic created: MYPROJ-42  (EP-01: Platform Foundation)
# Story created: MYPROJ-43  (F-01.1: Envoy Agent Registration)
```

## ADF Conversion Rules

| Input markup | ADF output |
|-------------|-----------|
| `**bold text**` | `{"type": "text", "text": "bold text", "marks": [{"type": "strong"}]}` |
| `*italic text*` | `{"type": "text", "text": "italic text", "marks": [{"type": "em"}]}` |
| `- list item` | `bulletList > listItem > paragraph` |
| `EP-01`, `F-01.1`, etc. in `id_map` | Hyperlink to `{base_url}/browse/{MYPROJ-42}` |
| Dict description | Each key becomes a `**Heading**` paragraph; list values become bullet lists |

ADF is sanitised after conversion — empty text nodes, empty paragraphs, and empty containers are removed. A document with no content gets a single space paragraph so Jira always receives valid ADF.

## Error Handling

| Error | Cause | Behaviour |
|-------|-------|-----------|
| No `projectKey` | Neither in payload nor in config | Returns `"Fatal error: no projectKey provided..."` |
| Empty or non-list `issues` | Malformed payload | Returns `"Fatal error: 'issues' must be a non-empty list."` |
| HTTP error per issue | 400 Bad Request, 401, 404, etc. | Appended as `"Failed: ..."` line; other issues continue |
| `parentKey` not yet resolved | Parent issue not in `id_map` | `parentKey` treated as a real Jira key (passed through as-is) |
| Network / timeout | Connection failure | Per-issue `RequestException` caught; appended as `"Failed: ..."` |
| Fatal exception | Unexpected error | Returns `"Fatal error: ..."` |

## ISSUE_TYPE_MAP

If your Jira project uses non-standard issue type names, populate `ISSUE_TYPE_MAP` at the top of the file:

```python
ISSUE_TYPE_MAP = {"Epic": "Task", "Story": "Task"}
```

This remaps the payload's types before posting, avoiding misleading 400 errors.

## Security Notes

- `JIRA_BASE_URL`, `JIRA_USER_EMAIL`, and `JIRA_API_TOKEN` are currently **hardcoded** at the top of the file. Move them to a secrets manager before production use.
- Credentials can be overridden per-call via `inputJSON`.
- The API token is used via `HTTPBasicAuth` — never logged.

## Resilience

| Concern | Configuration |
|---------|--------------|
| Timeout | 30 s per HTTP request |
| Retry | Max 2 retries with exponential backoff on transient errors |
| Circuit breaker | 5 consecutive failures → open for 60 s |
| Dry-run mode | `dry_run=True` builds and validates all payloads without any Jira API calls |
| Partial failure | Per-issue errors are isolated; the batch continues for remaining issues |
| Cross-linking | `id_map` built incrementally — earlier issues' real keys are available for later cross-links |
