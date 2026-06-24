"""Tests for L1-azure-blob-upload."""
import base64
from unittest.mock import patch, MagicMock
from tool import Tool, ToolResult


def test_upload_success():
    tool = Tool(secrets={"connection_string": "DefaultEndpointsProtocol=https;AccountName=test"})
    mock_blob_client = MagicMock()
    mock_blob_client.url = "https://test.blob.core.windows.net/docs/reports/file.pdf"
    mock_container = MagicMock()
    mock_container.exists.return_value = True
    mock_container.get_blob_client.return_value = mock_blob_client

    with patch("tool.BlobServiceClient") as mock_svc:
        mock_svc.from_connection_string.return_value.get_container_client.return_value = mock_container
        content = base64.b64encode(b"hello world").decode()
        result = tool.execute("docs", "reports", "file.pdf", content, "application/pdf")

    assert result.success is True
    assert result.data["file_name"] == "file.pdf"
    assert result.data["size_bytes"] == 11


def test_upload_invalid_base64():
    tool = Tool(secrets={"connection_string": "test"})
    result = tool.execute("docs", "reports", "file.pdf", "not-valid-base64!!!", "text/plain")
    assert result.success is False
    assert "base64" in result.error


def test_upload_missing_params():
    tool = Tool(secrets={"connection_string": "test"})
    result = tool.execute("", "reports", "file.pdf", "abc", "text/plain")
    assert result.success is False
    assert "required" in result.error
