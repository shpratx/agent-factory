# tool-L1-github-reader

## What does it do?

Recursively reads and returns the decoded text contents of all files under a specified folder in a GitHub repository branch. The tool authenticates with GitHub using a Personal Access Token, resolves the repository owner from the token, verifies both the repository and the target folder exist, then uses the Git Tree API to retrieve the full recursive file list in a single call. Each file is downloaded via the Contents API and decoded from base64 UTF-8. Binary files are flagged with a special status instead of failing.

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| folder_location | string | ✓ | Repository folder path to read recursively (e.g. `"src"` or `"project_k/lld"`). Leading/trailing whitespace and slashes are stripped automatically. |
| repo | string | ✓ | Repository name **without** the owner prefix (e.g. `"scib_demo"`) |
| branch | string | ✓ | Exact branch name to read from (e.g. `"main"`, `"feature/SCRUM-11691"`) |

## Returns

On success, a dictionary with the following structure:

| Field | Type | Description |
|-------|------|-------------|
| repository | string | Full repository identifier in `owner/repo` format |
| branch | string | Branch that was read |
| folder_location | string | Normalised folder path (leading/trailing slashes removed) |
| files | object | Per-file results keyed by file path (see below) |
| message | string (optional) | Present when the folder exists but contains no files |

Each entry in `files` has one of these shapes:

**Success:**
```json
{
  "status": "success",
  "content": "<decoded UTF-8 text>",
  "size": 1234,
  "sha": "abc123..."
}
```

**Binary / non-UTF-8:**
```json
{
  "status": "binary_or_non_utf8",
  "message": "File is not UTF-8 text; content not decoded.",
  "size": 5678,
  "sha": "def456..."
}
```

**Not found** (race condition — file deleted between tree and content fetch):
```json
{"status": "not_found", "message": "File '<path>' not found in branch '<branch>'."}
```

**Error:**
```json
{"status": "error", "message": "<description>"}
```

On any unhandled error, returns a plain **error string** (not a dict).

## Example

```python
from tool_L1_github_reader import GithubReader

tool = GithubReader()
result = tool._run(
    folder_location="src/components",
    repo="my-repo",
    branch="main"
)
print(result["repository"])   # "varun-ascendion/my-repo"
print(result["files"]["src/components/app.py"]["content"])  # decoded file text
```

## Error Handling

| Error | Cause | Behaviour |
|-------|-------|-----------|
| Empty `folder_location` | Blank or whitespace-only string | Returns error string: `'folder_location' must be a non-empty string` |
| Repository not found | 404 from GitHub | Returns `"Error: Repository '<owner>/<repo>' not found."` |
| Folder not found | Folder path absent in branch | Returns `"Error reading scripts: Folder '<path>' not found in branch '<branch>'."` |
| Tree SHA missing | Unexpected branch API response shape | Returns `"Error reading scripts: Unable to resolve tree SHA for branch."` |
| No files under folder | Folder exists but has no blobs | Returns dict with empty `files` dict and `message` field |
| File download 404 | Race condition — file deleted mid-run | Entry set to `{"status": "not_found", ...}` |
| Binary / decode error | Non-UTF-8 file content | Entry set to `{"status": "binary_or_non_utf8", ...}` |
| Network / HTTP error | Timeout, 429, 5xx | Returns `"Error reading scripts: <exception> | GitHub response: <status> <text>"` |
| Timeout (30 s) | API didn't respond in time | Returns `"Error reading scripts: <timeout message>"` |

## GitHub API Endpoints Used

| Order | Endpoint | Purpose |
|-------|----------|---------|
| 1 | `GET /user` | Resolve repo owner from token |
| 2 | `GET /repos/{owner}/{repo}` | Verify repository exists |
| 3 | `GET /repos/{owner}/{repo}/contents/{folder}?ref={branch}` | Verify folder exists in branch |
| 4 | `GET /repos/{owner}/{repo}/branches/{branch}` | Fetch root tree SHA |
| 5 | `GET /repos/{owner}/{repo}/git/trees/{sha}?recursive=1` | Retrieve full recursive file list |
| 6 | `GET /repos/{owner}/{repo}/contents/{file}?ref={branch}` | Download each file's content (one call per file) |

## Security Notes

- The GitHub Personal Access Token is currently **hardcoded** at the top of the file — this is a known security vulnerability. Revoke and move it to a secrets manager before production use.
- The token must have at minimum `repo` scope (or `public_repo` for public-only repos).
- GitHub rate limit: **5 000 requests/hour** when authenticated. Large folders with many files may approach this limit.

## Resilience

| Concern | Configuration |
|---------|--------------|
| Timeout | 30 s per HTTP request |
| Retry | Max 2 retries with exponential backoff on transient errors (429, 502, 503, timeout) |
| Circuit breaker | 5 consecutive failures → open for 60 s |
| Binary files | Gracefully flagged, never cause failure |
| Race conditions | Mid-run file deletions handled with `not_found` status |
