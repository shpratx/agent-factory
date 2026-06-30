"""Unit tests for tool-L1-azure-blob-reader (AzureBlobReaderTool).

All Azure SDK and crewai calls are mocked; no real network or storage
credentials are required to run these tests.

Run with:
    pytest tool-L1-azure-blob-reader-test.py -v
"""

import os
import sys
import types
import importlib.util
from unittest.mock import MagicMock, patch

import pytest

# ── Stub unavailable packages before the tool module is loaded ────────────

class _StubBaseTool:
    """Minimal BaseTool stub so the tool class can be defined without crewai."""
    name: str = ""
    description: str = ""
    args_schema = None

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)


_mock_crewai = types.ModuleType("crewai")
_mock_crewai_tools = types.ModuleType("crewai.tools")
_mock_crewai_tools.BaseTool = _StubBaseTool
sys.modules.setdefault("crewai", _mock_crewai)
sys.modules.setdefault("crewai.tools", _mock_crewai_tools)

_mock_azure = types.ModuleType("azure")
_mock_azure_storage = types.ModuleType("azure.storage")
_mock_azure_blob = types.ModuleType("azure.storage.blob")
_mock_azure_blob.BlobServiceClient = MagicMock()
_mock_azure_blob.BlobClient = MagicMock()
_mock_azure_blob.ContainerClient = MagicMock()
sys.modules.setdefault("azure", _mock_azure)
sys.modules.setdefault("azure.storage", _mock_azure_storage)
sys.modules.setdefault("azure.storage.blob", _mock_azure_blob)

# ── Load the tool module (hyphenated filename requires importlib) ──────────

_HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location(
    "tool_azure_blob_reader",
    os.path.join(_HERE, "tool-L1-azure-blob-reader.py"),
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)

AzureBlobReaderTool = _mod.AzureBlobReaderTool


# ── Helpers ───────────────────────────────────────────────────────────────

def _make_tool():
    return AzureBlobReaderTool()


def _make_blob_obj(name: str, content: bytes = b"text content"):
    blob = MagicMock()
    blob.name = name
    blob.download_blob.return_value.readall.return_value = content
    return blob


def _make_service_client(container_mock):
    bsc = MagicMock()
    bsc.get_container_client.return_value = container_mock
    return bsc


def _make_container(exists: bool = True, blobs=None):
    cc = MagicMock()
    cc.exists.return_value = exists
    cc.list_blobs.return_value = blobs or []
    return cc


# ── Tests: tool metadata ──────────────────────────────────────────────────

class TestToolMetadata:
    def test_name(self):
        assert _make_tool().name == "Azure Blob Reader Tool"

    def test_description_mentions_folder(self):
        assert "folder" in _make_tool().description.lower()


# ── Tests: successful reads ───────────────────────────────────────────────

class TestSuccessfulReads:
    def test_reads_single_utf8_file(self):
        blob = _make_blob_obj("reports/summary.md", b"# Summary\nAll good.")
        cc = _make_container(blobs=[blob])
        cc.get_blob_client.return_value = blob
        bsc = _make_service_client(cc)

        with patch.object(_mod, "BlobServiceClient") as MockBSC:
            MockBSC.from_connection_string.return_value = bsc
            result = _make_tool().read_all_files_in_folder("reports")

        assert "Read 1 file(s)" in result
        assert "reports/summary.md" in result
        assert "# Summary" in result

    def test_reads_multiple_files(self):
        blob_a = _make_blob_obj("data/a.txt", b"Alpha")
        blob_b = _make_blob_obj("data/b.txt", b"Beta")
        cc = _make_container(blobs=[blob_a, blob_b])
        cc.get_blob_client.side_effect = lambda n: blob_a if n == "data/a.txt" else blob_b
        bsc = _make_service_client(cc)

        with patch.object(_mod, "BlobServiceClient") as MockBSC:
            MockBSC.from_connection_string.return_value = bsc
            result = _make_tool().read_all_files_in_folder("data")

        assert "Read 2 file(s)" in result
        assert "data/a.txt" in result
        assert "data/b.txt" in result

    def test_folder_marker_blob_is_skipped(self):
        """The empty 'folder_name/' placeholder blob must not be counted."""
        marker = MagicMock()
        marker.name = "docs/"
        real_blob = _make_blob_obj("docs/file.txt", b"real content")
        cc = _make_container(blobs=[marker, real_blob])
        cc.get_blob_client.return_value = real_blob
        bsc = _make_service_client(cc)

        with patch.object(_mod, "BlobServiceClient") as MockBSC:
            MockBSC.from_connection_string.return_value = bsc
            result = _make_tool().read_all_files_in_folder("docs")

        assert "Read 1 file(s)" in result


# ── Tests: edge cases ─────────────────────────────────────────────────────

class TestEdgeCases:
    def test_container_not_found_returns_error_string(self):
        cc = _make_container(exists=False)
        bsc = _make_service_client(cc)

        with patch.object(_mod, "BlobServiceClient") as MockBSC:
            MockBSC.from_connection_string.return_value = bsc
            result = _make_tool().read_all_files_in_folder("anything")

        assert "does not exist" in result.lower()

    def test_empty_folder_returns_info_message(self):
        cc = _make_container(exists=True, blobs=[])
        bsc = _make_service_client(cc)

        with patch.object(_mod, "BlobServiceClient") as MockBSC:
            MockBSC.from_connection_string.return_value = bsc
            result = _make_tool().read_all_files_in_folder("empty-dir")

        assert "No files found" in result

    def test_binary_file_noted_without_crashing(self):
        """Non-UTF-8 bytes must be noted gracefully, not raise an exception."""
        blob = _make_blob_obj("imgs/photo.png", b"\x89PNG\r\n\x1a\n\x00")
        cc = _make_container(blobs=[blob])
        cc.get_blob_client.return_value = blob
        bsc = _make_service_client(cc)

        with patch.object(_mod, "BlobServiceClient") as MockBSC:
            MockBSC.from_connection_string.return_value = bsc
            result = _make_tool().read_all_files_in_folder("imgs")

        assert "Binary content" in result or "not displayed as text" in result

    def test_individual_blob_error_does_not_abort_other_files(self):
        bad = MagicMock()
        bad.name = "data/bad.txt"
        bad.download_blob.side_effect = Exception("transient error")

        good = _make_blob_obj("data/good.txt", b"OK content")
        cc = _make_container(blobs=[bad, good])
        cc.get_blob_client.side_effect = lambda n: bad if n == "data/bad.txt" else good
        bsc = _make_service_client(cc)

        with patch.object(_mod, "BlobServiceClient") as MockBSC:
            MockBSC.from_connection_string.return_value = bsc
            result = _make_tool().read_all_files_in_folder("data")

        assert "Error reading this file" in result
        assert "OK content" in result

    def test_sdk_exception_returns_safe_message(self):
        """Internal error detail must not be exposed to the caller."""
        with patch.object(_mod, "BlobServiceClient") as MockBSC:
            MockBSC.from_connection_string.side_effect = Exception("secret-credential-xyz")
            result = _make_tool().read_all_files_in_folder("docs")

        assert "An error occurred" in result
        assert "secret-credential-xyz" not in result

    def test_only_marker_blobs_returns_no_readable_files_message(self):
        """Folder that contains only the marker blob (ends with /) counts as empty."""
        marker = MagicMock()
        marker.name = "logs/"
        cc = _make_container(blobs=[marker])
        cc.get_blob_client.return_value = MagicMock()
        bsc = _make_service_client(cc)

        with patch.object(_mod, "BlobServiceClient") as MockBSC:
            MockBSC.from_connection_string.return_value = bsc
            result = _make_tool().read_all_files_in_folder("logs")

        assert "no readable files" in result.lower() or "no files found" in result.lower()


# ── Tests: _run delegation ────────────────────────────────────────────────

class TestRunDelegation:
    def test_run_delegates_to_read_all_files_in_folder(self):
        tool = _make_tool()
        with patch.object(tool, "read_all_files_in_folder", return_value="sentinel") as m:
            result = tool._run("my-folder")
        m.assert_called_once_with("my-folder")
        assert result == "sentinel"
