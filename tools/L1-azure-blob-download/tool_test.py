"""Tests for L1-azure-blob-download."""
from unittest.mock import patch, MagicMock
from datetime import datetime, timezone
from tool import Tool, ToolResult


def test_download_success():
    tool = Tool(secrets={"connection_string": "DefaultEndpointsProtocol=https;AccountName=test"})
    mock_blob_client = MagicMock()
    mock_blob_client.exists.return_value = True
    mock_download = MagicMock()
    mock_download.readall.return_value = b"hello world"
    mock_blob_client.download_blob.return_value = mock_download
    mock_props = MagicMock()
    mock_props.content_settings.content_type = "text/plain"
    mock_props.last_modified = datetime(2026, 6, 10, 14, 30, tzinfo=timezone.utc)
    mock_blob_client.get_blob_properties.return_value = mock_props

    with patch("tool.BlobServiceClient") as mock_svc:
        mock_svc.from_connection_string.return_value.get_blob_client.return_value = mock_blob_client
        result = tool.execute("docs", "reports", "file.txt")

    assert result.success is True
    assert result.data["size_bytes"] == 11
    assert result.data["content_type"] == "text/plain"


def test_download_not_found():
    tool = Tool(secrets={"connection_string": "test"})
    mock_blob_client = MagicMock()
    mock_blob_client.exists.return_value = False

    with patch("tool.BlobServiceClient") as mock_svc:
        mock_svc.from_connection_string.return_value.get_blob_client.return_value = mock_blob_client
        result = tool.execute("docs", "reports", "missing.txt")

    assert result.success is False
    assert "not found" in result.error


def test_download_path_traversal():
    tool = Tool(secrets={"connection_string": "test"})
    result = tool.execute("docs", "../etc", "passwd")
    assert result.success is False
    assert "traversal" in result.error


def test_download_missing_params():
    tool = Tool(secrets={"connection_string": "test"})
    result = tool.execute("", "reports", "file.txt")
    assert result.success is False
    assert "required" in result.error
