# tool-L1-github-writer-generic

## What does it do?

Creates a new branch from a source branch in a GitHub repository and commits one or more files to it in a single operation. The tool handles both flat and nested file descriptor formats, builds a Git tree object containing all the files, creates a commit, and updates the branch reference atomically. If the target branch already exists, the commit is stacked on top of its current HEAD — the tool is idempotent on the branch name.

## Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| files | array of objects | ✓ | — | List of file descriptors (see formats below) |
| repo_name | string | ✓ | — | Repository name without owner prefix (e.g. `"SCIB-Inception"`) |
| new_branch | string | ✓ | — | Name of the branch to create and commit to (e.g. `"feature/auto-update"`) |
| source_branch | string | | `"main"` | Branch to use as the base when creating `new_branch` |

### File Descriptor Formats

**Flat format:**
```json
{"filename": "docs/api.txt", "code": "API documentation content"}
```

**Nested format** (folder + filename):
```json
{"src/utils": {"filename": "helpers.py", "code": "def add(a, b):\n    return a + b\n"}}
```

Both formats can be mixed in the same `files` list.

## Returns

| Field | Type | Description |
|-------|------|-------------|
| status | string | `"success"` or `"failure"` |
| branch | string | Name of the newly created or updated branch |
| source_branch | string | Branch used as the base |
| updated_files | array[string] | Resolved file paths that were committed |
| message | string | Human-readable summary (e.g. `"Created 'feature/x' from 'main' and committed 3 file(s)."`) |
| url | string | GitHub URL to browse the new branch |

On failure:
```json
{"status": "failure", "message": "<exception message>"}
```

## Example

```python
from tool_L1_github_writer_generic import GithubCommitterTool

tool = GithubCommitterTool()
result = tool._run(
    files=[
        {"filename": "docs/summary.md", "code": "# Summary\nSprint complete."},
        {"src": {"filename": "main.py", "code": "print('hello')\n"}}
    ],
    repo_name="my-repo",
    new_branch="feature/sprint-42-output",
    source_branch="main"
)
print(result["status"])   # "success"
print(result["url"])      # "https://github.com/varun-ascendion/my-repo/tree/feature/sprint-42-output"
```

## GitHub API Workflow

| Step | API Call | Purpose |
|------|----------|---------|
| 1 | `GET /repos/{owner}/{repo}/git/ref/heads/{source_branch}` | Get HEAD SHA of source branch |
| 2 | `POST /repos/{owner}/{repo}/git/refs` | Create new branch (HTTP 422 = already exists → skip to step 2b) |
| 2b | `GET /repos/{owner}/{repo}/git/ref/heads/{new_branch}` | Get current HEAD SHA of existing branch |
| 3 | `POST /repos/{owner}/{repo}/git/trees` | Create tree object with all file contents |
| 4 | `POST /repos/{owner}/{repo}/git/commits` | Create commit pointing to new tree |
| 5 | `PATCH /repos/{owner}/{repo}/git/refs/heads/{new_branch}` | Update branch reference to new commit |

## Error Handling

| Error | Cause | Behaviour |
|-------|-------|-----------|
| HTTP 4xx/5xx | API error on any step | `raise_for_status()` raises; caught by outer `except`; returned as `{"status": "failure", "message": "..."}` |
| Branch already exists | HTTP 422 on step 2 | Detected gracefully; commit stacked on existing branch HEAD |
| Invalid token | 401 Unauthorized | Caught; returned as failure dict |
| Network timeout | No response within 30 s | Caught; returned as failure dict |
| Malformed file descriptor | Missing `filename` key | Defaults to `"script.py"` for filename; empty string for code |

## Security Notes

- The GitHub token and repo owner are currently **hardcoded** at the top of the file — this is a known security vulnerability. Move them to a secrets manager before production use.
- The commit message includes a UTC timestamp; no PII is included.
- All file content is passed directly as strings to the GitHub API — ensure content does not contain secrets before committing.

## Resilience

| Concern | Configuration |
|---------|--------------|
| Timeout | 30 s per HTTP request (requests library default) |
| Retry | Max 2 retries with exponential backoff on transient errors (429, 502, 503, timeout) |
| Circuit breaker | 5 consecutive failures → open for 60 s |
| Idempotency | Existing branch detected via HTTP 422; commit safely stacked on top |
