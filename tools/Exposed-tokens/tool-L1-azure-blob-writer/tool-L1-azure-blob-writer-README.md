# tool-L1-azure-blob-writer

## What does it do?

Creates a virtual folder and uploads a file with specified text content to Azure Blob Storage. In Azure Blob Storage, folders are virtual and represented by blob name prefixes; the tool creates an empty placeholder blob (`folder_name/`) to simulate the folder, then uploads the actual file at `folder_name/file_name`. If the container does not exist, it is created automatically. File names are sanitised to prevent directory traversal attacks. Content is validated and capped at 10 MB before upload.

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| folder_name | string | ✓ | Name of the folder to create in Azure Blob Storage (used as blob prefix) |
| file_name | string | ✓ | Name of the file to create inside the folder |
| content | string | ✓ | Text content to write to the file; automatically truncated at 10 MB |

## Returns

| Field | Type | Description |
|-------|------|-------------|
| (return value) | string | Multi-line status string on success, e.g. `"Container 'aava-ggm' already exists. blob_storage_url = '...'\nFolder 'docs' created successfully.\nFile 'report.md' created successfully in folder 'docs'."` |
| (return value) | string | `"Error accessing container. Please try again later or contact support."` on container error |
| (return value) | string | `"Error creating folder. Please try again later or contact support."` on folder creation error |
| (return value) | string | `"Error creating file. Please try again later or contact support."` on file upload error |
| (return value) | string | `"An error occurred while processing your request. Please try again later or contact support."` on unhandled error |

## Example

```python
from tool_L1_azure_blob_writer import AzureBlobWriterTool

tool = AzureBlobWriterTool()
result = tool._run(
    folder_name="sprint-42/outputs",
    file_name="summary.md",
    content="# Sprint 42 Summary\n\nAll stories completed."
)
print(result)
# Container 'aava-ggm' already exists. blob_storage_url = 'avaplusstorageprod.blob.core.windows.net/aava-ggm'
# Folder 'sprint-42/outputs' created successfully.
# File 'summary.md' created successfully in folder 'sprint-42/outputs'.
```

## Input Sanitisation

`file_name` is sanitised before use:

| Dangerous pattern | Replacement |
|-------------------|-------------|
| `\`, `/`, `*`, `?`, `"`, `<`, `>`, `\|` | `_` |
| `..` (path traversal) | `_` |
| Leading `.`, `/`, `\` | Stripped |
| Empty result after sanitisation | `"default"` |

`folder_name` is **not** sanitised — it is passed through as-is to support nested prefixes (e.g. `project/subfolder`).

`content` is capped at 10 MB (UTF-8 encoded); if it exceeds this limit the content is truncated silently (a warning is logged).

## Error Handling

| Error | Cause | Behaviour |
|-------|-------|-----------|
| Timeout | SDK network timeout | Returns error string; details logged |
| Container access denied | Invalid credentials or insufficient permissions | Returns `"Error accessing container..."` |
| Folder creation failure | SDK blob upload error | Returns `"Error creating folder..."` |
| File upload failure | SDK blob upload error | Returns `"Error creating file..."` |
| Content too large | Content > 10 MB | Truncated to 10 MB before upload; warning logged |
| Unhandled exception | Unexpected SDK error | Returns `"An error occurred while processing your request..."` |

## Security Notes

- The connection string is currently **hardcoded** at the top of the file — this is a known security issue. Move it to a secrets manager before production use.
- The container name is fixed to `aava-ggm`.
- All operations are logged to `azure_blob_operations.log`. The connection string is **never** written to logs.
- `overwrite=True` is passed to all blob uploads — existing files with the same path are silently overwritten.

## Resilience

| Concern | Configuration |
|---------|--------------|
| Timeout | 30 s default (Azure SDK default) |
| Retry | Max 2 retries with exponential backoff on transient errors (429, 502, 503, timeout) |
| Circuit breaker | 5 consecutive failures → open for 60 s |
| Idempotency | `overwrite=True` — safe to re-run with the same inputs |
