# tool-L1-confluence-reader

## What does it do?

Reads the title and full body of a Confluence page via the Confluence REST API v1. Authentication uses HTTP Basic Auth (email + API token). The body is returned in **Confluence storage format**, which is a proprietary XHTML dialect — not plain text, not Markdown. Agents consuming this output must be prepared to handle or strip XHTML tags.

---

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `page_id` | string | ✓ | Numeric ID of the Confluence page (e.g. `"425985"`). Find it in the page URL: `.../pages/425985/Page+Title` |
| `base_url` | string | ✓ | Base URL of the Confluence instance **including `/wiki`** (e.g. `"https://your-domain.atlassian.net/wiki"`) |

---

## Returns

On success, a single formatted string:

```
Title: <page title>
Content: <body in Confluence storage format (XHTML)>
```

On error:

```
Error reading Confluence page: <requests exception message>
```

### ⚠️ Output Format — Confluence Storage Format (XHTML)

The `Content` field is **raw Confluence storage format**, not plain text or Markdown. This is a proprietary XHTML dialect used internally by Confluence. Examples of what you will see:

```xml
<p>This is a paragraph.</p>
<h2>Section Heading</h2>
<ul><li>Bullet point</li></ul>
<ac:structured-macro ac:name="info">
  <ac:rich-text-body><p>This is an info panel.</p></ac:rich-text-body>
</ac:structured-macro>
<ri:page ri:content-title="Another Page" />
```

**Agents and downstream consumers must either:**
- Parse/strip XHTML tags if they need plain text, or
- Treat the string as markup to be passed directly to another Confluence write call

---

## Example

```python
from tool_L1_confluence_reader import ConfluencePageReader

tool = ConfluencePageReader()
result = tool._run(
    page_id="425985",
    base_url="https://mycompany.atlassian.net/wiki"
)
print(result)
# Title: Sprint 42 Notes
# Content: <p>Velocity: 34 points.</p><h2>Completed</h2><ul><li>Task A</li></ul>
```

---

## Error Handling

| Error | Cause | Behaviour |
|-------|-------|-----------|
| `401 Unauthorized` | Invalid or expired API token | `RequestException` caught; returns `"Error reading Confluence page: 401 Client Error..."` |
| `403 Forbidden` | Authenticated user lacks page-read permission | Same as above |
| `404 Not Found` | `page_id` does not exist | Returns `"Error reading Confluence page: 404 Client Error..."` |
| `429 Rate Limited` | Too many API requests | Returns error string; no automatic retry in current implementation |
| Network timeout | Confluence instance unreachable | Caught by `RequestException`; returns error string |
| Connection error | DNS failure, firewall | Caught by `RequestException`; returns error string |

---

## API Endpoint Used

```
GET {base_url}/rest/api/content/{page_id}?expand=body.storage
```

Authentication: HTTP Basic Auth (`user_email:api_key`)

---

## Known Issues & Nuances

### 1. Argument Swap Guard (silent behaviour)
The tool contains this guard:
```python
if base_url.isdigit() or page_id.startswith("http"):
    page_id, base_url = base_url, page_id
```
If the calling agent passes the arguments in the wrong order — `page_id="https://..."` or `base_url="425985"` — the tool **silently swaps them and continues** rather than failing fast. While this improves robustness against agent confusion, it can **mask incorrect invocations** and make bugs harder to diagnose.

### 2. Output is XHTML, not plain text
The `Content` field contains raw Confluence storage format. Agents expecting natural-language text will receive XML markup. An HTML/XML parser or stripping step is needed if plain text is required.

### 3. No HTTP timeout configured
There is no `timeout=` argument on the `requests.get()` call. On a slow or unresponsive Confluence instance the request can **hang indefinitely**, blocking the agent's execution thread. A 30 s timeout should be added.

### 4. Only `body.storage` is fetched
The `expand=body.storage` query parameter means only the page body is returned. **Not included**: labels, attachments, comments, page version, space info, child pages, or ancestors. A separate API call is required for any of these.

### 5. Hardcoded credentials
`api_key` and `user_email` are hardcoded at the top of the file. This is a security vulnerability. They must be moved to a secrets manager before production use.

### 6. No input validation
`page_id` is not validated to be numeric before the API call. A non-numeric `page_id` will cause a `404` or malformed URL.

---

## Security Notes

- `api_key` and `user_email` are currently **hardcoded** — revoke and move to a secrets manager (e.g. Azure Key Vault, HashiCorp Vault) before production use.
- Credentials are passed via HTTP Basic Auth over HTTPS — never logged by the tool.

## Resilience

| Concern | Current state | Recommendation |
|---------|--------------|----------------|
| Timeout | ❌ None configured | Add `timeout=30` to `requests.get()` |
| Retry | ❌ No retry logic | Add retry with exponential backoff for 429/5xx |
| Input validation | ❌ No `page_id` format check | Validate `page_id` is numeric before calling |
| Error detail | ⚠️ Exception message only | Consider including HTTP status code in error string |
