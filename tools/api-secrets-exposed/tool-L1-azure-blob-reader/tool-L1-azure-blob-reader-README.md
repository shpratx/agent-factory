# tool-L1-azure-blob-reader

## What does it do?

Reads and returns the decoded text contents of every file inside a specified folder (virtual prefix) in Azure Blob Storage. The tool lists all blobs under the given folder prefix, downloads each one, and returns a formatted string that includes the file name and its content. Binary or non-UTF-8 files are noted with their byte size instead of content. The folder marker blob itself (the empty `folder_name/` placeholder) is skipped automatically.

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| folder_name | string | ✓ | Name of the folder (blob prefix) in Azure Blob Storage to read all files from |

## Returns

| Field | Type | Description |
|-------|------|-------------|
| (return value) | string | `"Read N file(s) from folder '<name>':\n\n===== FILE: <path> =====\n<content>\n..."` on success |
| (return value) | string | `"No files found in folder '<name>'."` when the folder is empty |
| (return value) | string | `"Container '<name>' does not exist."` when the container is missing |
| (return value) | string | `"An error occurred while reading the folder"` on unhandled SDK/network error |

Each `===== FILE: <blob-path> =====` section contains either the decoded UTF-8 text or a note: `[Binary content, N bytes — not displayed as text]`.

## Example

```python
from tool_L1_azure_blob_reader import AzureBlobReaderTool

tool = AzureBlobReaderTool()
result = tool._run(folder_name="my-project/docs")
print(result)
# Read 2 file(s) from folder 'my-project/docs':
#
# ===== FILE: my-project/docs/overview.md =====
# # Overview
# This document describes...
#
# ===== FILE: my-project/docs/config.json =====
# {"key": "value"}
```

## Error Handling

| Error | Cause | Behaviour |
|-------|-------|-----------|
| Container not found | The configured container does not exist | Returns `"Container '<name>' does not exist."` |
| No files in folder | Prefix matches no blobs (or only the folder marker) | Returns `"No files found in folder '<name>'."` or `"Folder '<name>' contains no readable files"` |
| Individual blob download failure | Transient SDK error on a single blob | Logs error at ERROR level; marks file section with `[Error reading this file]` and continues |
| Binary / non-UTF-8 content | File cannot be decoded as UTF-8 | Marks section with `[Binary content, N bytes — not displayed as text]` |
| Unhandled exception | SDK initialisation failure or network error | Logs full traceback; returns `"An error occurred while reading the folder"` |

## Security Notes

- The connection string is currently **hardcoded** at the top of the file — this is a known security issue. It must be moved to a secrets manager (e.g. Azure Key Vault, HashiCorp Vault) before use in production.
- The container name is fixed to `aava-ggm`.
- All operations are logged to `azure_blob_operations.log`. The connection string is **never** written to logs.

## Resilience

| Concern | Configuration |
|---------|--------------|
| Timeout | 30 s default (Azure SDK default) |
| Retry | Max 2 retries with exponential backoff on transient errors (429, 502, 503, timeout) |
| Circuit breaker | 5 consecutive failures → open for 60 s |
| Partial failure | Per-blob errors are isolated; other files in the folder continue to be read |
