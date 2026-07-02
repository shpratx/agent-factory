# tool-L1-confluence-page-writer-and-updater

## What does it do?

Creates a new Confluence page, or **appends content to an existing page** if a page with the same title already exists in the target space. The tool first searches the space for a page matching the title exactly. If found, it fetches the existing body, concatenates the new content onto it, and PUTs the full updated body back. If not found, it POSTs a new page. Content must be provided in **Confluence storage format (XHTML)** — the same format returned by the reader tool.

---

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `title` | string | ✓ | Title of the page to create or append to. **Exact-match, case-sensitive** against existing pages in the space. |
| `content` | string | ✓ | Body content in **Confluence storage format (XHTML)**. See below for format details and examples. Plain text or Markdown will be stored literally and render incorrectly. |
| `space_key` | string | ✓ | Key of the target Confluence space. For team spaces: alphanumeric (e.g. `"ENG"`). For personal spaces: a hashed key (e.g. `"~7120208dde8969e5854fbfbe0185df21567c33"`). |
| `base_url` | string | ✓ | Base URL of the Confluence instance **including `/wiki`** (e.g. `"https://your-domain.atlassian.net/wiki"`). |

---

## ⚠️ Input Format — Confluence Storage Format (XHTML)

The `content` parameter **must** be valid Confluence storage format. This is a proprietary XHTML dialect. Passing plain text or Markdown will cause it to be stored literally — it will appear as raw markup in the Confluence page.

### Supported tags

| Purpose | Tags |
|---------|------|
| Paragraphs | `<p>text</p>` |
| Headings | `<h1>` through `<h6>` |
| Bullet list | `<ul><li>item</li></ul>` |
| Numbered list | `<ol><li>item</li></ol>` |
| Table | `<table><tr><th>Head</th></tr><tr><td>Cell</td></tr></table>` |
| Bold / italic | `<strong>bold</strong>`, `<em>italic</em>` |
| Code block | `<ac:structured-macro ac:name="code"><ac:plain-text-body><![CDATA[code here]]></ac:plain-text-body></ac:structured-macro>` |
| Info panel | `<ac:structured-macro ac:name="info"><ac:rich-text-body><p>text</p></ac:rich-text-body></ac:structured-macro>` |
| Cross-page link | `<ac:link><ri:page ri:content-title="Page Name"/></ac:link>` |

### Example valid content string

```xml
<h2>Sprint 42 Summary</h2>
<p>Velocity: <strong>34 points</strong>.</p>
<ul>
  <li>Feature A shipped</li>
  <li>Bug B resolved</li>
</ul>
<ac:structured-macro ac:name="info">
  <ac:rich-text-body><p>Retrospective scheduled for Friday.</p></ac:rich-text-body>
</ac:structured-macro>
```

---

## Returns

### On successful append (page already existed)

```
Content appended to existing page.
confluence_page_id: 425985
base_url: https://mycompany.atlassian.net/wiki
space_key: ENG

Page Title: Sprint 42 Notes
Version: 4
URL: https://mycompany.atlassian.net/wiki/spaces/ENG/pages/425985/Sprint+42+Notes
```

### On successful create (new page)

```
Page created successfully.
confluence_page_id: 425986
base_url: https://mycompany.atlassian.net/wiki
space_key: ENG

Page Title: Sprint 42 Notes
Version: 1
URL: https://mycompany.atlassian.net/wiki/spaces/ENG/pages/425986/Sprint+42+Notes
```

### On error

```
Error writing to Confluence page: <exception message>
Details: <HTTP response body from Confluence>
```

---

## Example

```python
from tool_L1_confluence_page_writer_and_updater import ConfluencePageCreator

tool = ConfluencePageCreator()

# Create a new page
result = tool._run(
    title="Sprint 42 Notes",
    content="<h2>Goals</h2><p>Complete auth module.</p>",
    space_key="ENG",
    base_url="https://mycompany.atlassian.net/wiki"
)
print(result)
# Page created successfully.
# confluence_page_id: 425986 ...

# Run again with same title -> appends to the existing page
result = tool._run(
    title="Sprint 42 Notes",
    content="<h2>Outcomes</h2><p>Auth module shipped.</p>",
    space_key="ENG",
    base_url="https://mycompany.atlassian.net/wiki"
)
print(result)
# Content appended to existing page.
# confluence_page_id: 425986 ...
# Version: 2
```

---

## API Workflow

| Step | API Call | Purpose |
|------|----------|---------|
| 1 | `GET {base}/rest/api/content?spaceKey=...&title=...&expand=body.storage,version` | Search for existing page by exact title |
| 2a | `PUT {base}/rest/api/content/{page_id}` | Update (append) if page found — must include `version.number = current + 1` |
| 2b | `POST {base}/rest/api/content` | Create new page if not found |

---

## Error Handling

| Error | Cause | Behaviour |
|-------|-------|-----------|
| `401 Unauthorized` | Invalid or expired API token | `RequestException` caught; returns error string with HTTP detail |
| `403 Forbidden` | User lacks write permission to the space | Same as above |
| `404 Not Found` | `space_key` or `page_id` invalid | Returns error string with HTTP detail |
| `400 Bad Request` | Malformed XHTML content or invalid JSON payload | Returns error string with Confluence's error body in `Details:` |
| `409 Conflict` | Version mismatch (optimistic lock failure) | Returns error string — see concurrency caveat below |
| `429 Rate Limited` | Too many API requests | Returns error string; no automatic retry |
| Network / timeout | Confluence instance unreachable | Caught by `RequestException`; returns error string |

---

## Known Issues & Nuances

### 1. Append is a full read-modify-write (not an atomic append)
Confluence has no "append" endpoint. The tool:
1. Reads the existing page body (XHTML)
2. Concatenates `<p></p>` + new content onto the end
3. PUTs the entire combined body back

This means the **whole page is rewritten on every append**. If the existing page has complex macros or structured content, there is a small risk of subtle rendering changes.

### 2. Version bumping is mandatory — 409 Conflict on stale version
Confluence uses **optimistic locking**. Every PUT must supply `version.number` as exactly `current_version + 1`. The tool reads the current version from the search response and increments it. If the version has changed between the search and the PUT (e.g. a manual edit in the browser), the PUT will **fail with HTTP 409 Conflict**.

### 3. Concurrency hazard — parallel runs will conflict
Because the flow is read → increment version → write, **two agents running against the same page title simultaneously** will both read the same current version. One PUT will succeed; the other will fail with 409. Never run two instances of this tool targeting the same page in parallel.

### 4. Title matching is exact and case-sensitive
The search uses `title=<exact string>`. `"Sprint Notes"` and `"sprint notes"` are treated as **different pages**. Confluence itself is not case-sensitive for page titles, but the REST API search parameter is used with `=` exact match here — ensure the calling agent always passes the canonical casing.

### 5. Content is not validated before submission
The tool sends whatever string is in `content` directly to the Confluence API. **Malformed XHTML** (unclosed tags, invalid attribute values, illegal characters) may:
- Cause a `400 Bad Request` from Confluence
- Be silently accepted but render incorrectly in the page editor
- Strip certain unsupported tags without warning

### 6. Append separator is a single empty paragraph
The separator between the existing body and the new content is `<p></p>` (an empty paragraph). This produces a small visual gap. If you need a horizontal rule or a labelled section, include it explicitly in the `content` parameter.

### 7. No HTTP timeout on any request
None of the three `requests` calls (`GET`, `PUT`, `POST`) have a `timeout=` argument. All three can hang indefinitely.

### 8. Hardcoded credentials
`api_key` and `user_email` are hardcoded at the top of the file. This is a security vulnerability. Move them to a secrets manager before production use.

---

## Security Notes

- `api_key` and `user_email` are currently **hardcoded** — revoke and move to a secrets manager before production use.
- Credentials are passed via HTTP Basic Auth over HTTPS — never logged by the tool.
- The HTTP response body from Confluence (which may contain internal error detail) is included in the error return string on failure.

## Resilience

| Concern | Current state | Recommendation |
|---------|--------------|----------------|
| Timeout | ❌ None on GET / PUT / POST | Add `timeout=30` to all three calls |
| Retry | ❌ No retry logic | Add retry with backoff for 429/5xx; **do NOT retry 409** (version conflict needs re-read) |
| Concurrency | ❌ Race condition on same-title pages | Serialize writes to the same page; or re-read version before PUT |
| Content validation | ❌ No XHTML validation | Validate content is well-formed XML before submitting |
| 409 handling | ❌ Returned as error string | Consider re-reading the page and retrying once on 409 |
