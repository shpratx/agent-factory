# L1-azure-blob-download

## What does it do?

Downloads a document from a specific folder in Azure Blob Storage. Returns file content as base64 with metadata (content type, size, last modified).

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| container_name | string | ✓ | Azure Blob container name |
| folder_path | string | ✓ | Virtual folder path (e.g., "reports/2026") |
| file_name | string | ✓ | Name of the file to download |

## Returns

| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Whether the download succeeded |
| data.file_content | string | Base64-encoded file content |
| data.content_type | string | MIME type of the file |
| data.size_bytes | integer | File size in bytes |
| data.last_modified | string | ISO 8601 timestamp of last modification |
| error | string | Error message (null on success) |

## Example

```python
result = tool.execute(
    container_name="documents",
    folder_path="reports/2026",
    file_name="summary.pdf"
)
# ToolResult(success=True, data={"file_content": "JVBERi0x...", "content_type": "application/pdf", "size_bytes": 45200, "last_modified": "2026-06-10T14:30:00+00:00"})
```

## Error Handling

| Error | Cause | Behaviour |
|-------|-------|-----------|
| Blob not found | File doesn't exist at path | Returns error, no retry |
| Path traversal | ".." in folder_path or file_name | Returns error immediately |
| Timeout | Azure didn't respond in 60s | Retries up to 2x |
| 429 | Rate limited | Exponential backoff retry |
