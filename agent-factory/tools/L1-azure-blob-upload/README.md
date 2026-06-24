# L1-azure-blob-upload

## What does it do?

Creates a virtual folder in Azure Blob Storage (if it doesn't exist) and uploads a file into it. Handles container creation, path sanitisation, and content type setting.

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| container_name | string | ✓ | Azure Blob container name |
| folder_path | string | ✓ | Virtual folder path (e.g., "reports/2026") |
| file_name | string | ✓ | Name of the file to upload |
| file_content | string | ✓ | Base64-encoded file content |
| content_type | string | ✗ | MIME type (default: application/octet-stream) |

## Returns

| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Whether the upload succeeded |
| data.blob_url | string | Full URL of the uploaded blob |
| data.folder_path | string | Normalised folder path |
| data.file_name | string | File name as stored |
| data.size_bytes | integer | Size of uploaded file |
| error | string | Error message (null on success) |

## Example

```python
result = tool.execute(
    container_name="documents",
    folder_path="reports/2026",
    file_name="summary.pdf",
    file_content="JVBERi0xLjQ...",  # base64
    content_type="application/pdf"
)
# ToolResult(success=True, data={"blob_url": "https://...blob.core.windows.net/documents/reports/2026/summary.pdf", ...})
```

## Error Handling

| Error | Cause | Behaviour |
|-------|-------|-----------|
| Invalid base64 | file_content not valid base64 | Returns error, no retry |
| Container create failed | Permission denied | Returns error |
| Timeout | Azure didn't respond in 60s | Retries up to 2x |
| 429 | Rate limited | Exponential backoff retry |
