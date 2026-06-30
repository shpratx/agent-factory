"""Unit tests for tool-L1-azure-blob-writer (AzureBlobWriterTool).

All Azure SDK and crewai calls are mocked; no real network or storage
credentials are required to run these tests.

Run with:
    pytest tool-L1-azure-blob-writer-test.py -v
"""

import os
import sys
import types
import importlib.util
from unittest.mock import MagicMock, patch

import pytest

# ── Stub unavailable packages before the tool module is loaded ────────────

class _StubBaseTool:
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

# ── Load the tool module ──────────────────────────────────────────────────

_HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location(
    "tool_azure_blob_writer",
    os.path.join(_HERE, "tool-L1-azure-blob-writer.py"),
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)

AzureBlobWriterTool = _mod.AzureBlobWriterTool


# ── Helpers ───────────────────────────────────────────────────────────────

def _make_tool():
    return AzureBlobWriterTool()


def _make_container_client(exists: bool = True):
    cc = MagicMock()
    cc.exists.return_value = exists
    cc.get_blob_client.return_value = MagicMock()
    return cc


def _make_bsc(cc):
    bsc = MagicMock()
    bsc.get_container_client.return_value = cc
    bsc.create_container.return_value = cc
    return bsc


# ── Tests: tool metadata ──────────────────────────────────────────────────

class TestToolMetadata:
    def test_name(self):
        assert _make_tool().name == "Azure Blob Storage Tool"

    def test_description_mentions_blob(self):
        assert "blob" in _make_tool().description.lower()


# ── Tests: successful writes ──────────────────────────────────────────────

class TestSuccessfulWrites:
    def test_creates_file_in_existing_container(self):
        cc = _make_container_client(exists=True)
        bsc = _make_bsc(cc)

        with patch.object(_mod, "BlobServiceClient") as MockBSC:
            MockBSC.from_connection_string.return_value = bsc
            result = _make_tool().create_folder_and_file_in_blob_storage(
                "sprint-1", "notes.md", "Sprint notes here"
            )

        assert "already exists" in result
        assert "created successfully" in result

    def test_creates_container_when_missing(self):
        cc = _make_container_client(exists=False)
        bsc = _make_bsc(cc)

        with patch.object(_mod, "BlobServiceClient") as MockBSC:
            MockBSC.from_connection_string.return_value = bsc
            result = _make_tool().create_folder_and_file_in_blob_storage(
                "new-folder", "file.txt", "content"
            )

        bsc.create_container.assert_called_once()
        assert "created successfully" in result

    def test_run_delegates_to_create_method(self):
        tool = _make_tool()
        with patch.object(
            tool, "create_folder_and_file_in_blob_storage", return_value="ok"
        ) as m:
            result = tool._run("f", "n.txt", "body")
        m.assert_called_once_with("f", "n.txt", "body")
        assert result == "ok"


# ── Tests: input sanitisation ─────────────────────────────────────────────

class TestInputSanitisation:
    def test_sanitize_filename_removes_path_traversal(self):
        tool = _make_tool()
        result = tool._sanitize_path_component("../../../etc/passwd")
        assert ".." not in result
        assert "/" not in result

    def test_sanitize_filename_removes_special_chars(self):
        tool = _make_tool()
        result = tool._sanitize_path_component('file<name>:bad|chars"here')
        for ch in '<>:"|':
            assert ch not in result

    def test_sanitize_empty_returns_default(self):
        tool = _make_tool()
        assert tool._sanitize_path_component("") == "default"
        assert tool._sanitize_path_component("   ") == "default"

    def test_content_over_10mb_is_truncated(self):
        tool = _make_tool()
        big = "x" * (11 * 1024 * 1024)
        result = tool._validate_content(big)
        assert len(result.encode("utf-8")) <= 10 * 1024 * 1024

    def test_non_string_content_is_converted(self):
        tool = _make_tool()
        result = tool._validate_content(12345)
        assert isinstance(result, str)
        assert result == "12345"


# ── Tests: error cases ────────────────────────────────────────────────────

class TestErrorCases:
    def test_container_access_error_returns_safe_message(self):
        bsc = MagicMock()
        bsc.get_container_client.side_effect = Exception("auth failure")

        with patch.object(_mod, "BlobServiceClient") as MockBSC:
            MockBSC.from_connection_string.return_value = bsc
            result = _make_tool().create_folder_and_file_in_blob_storage(
                "f", "n.txt", "c"
            )

        assert "error" in result.lower()
        assert "auth failure" not in result

    def test_folder_creation_error_returns_safe_message(self):
        cc = _make_container_client(exists=True)
        blob_client = MagicMock()
        blob_client.upload_blob.side_effect = Exception("quota exceeded")
        cc.get_blob_client.return_value = blob_client
        bsc = _make_bsc(cc)

        with patch.object(_mod, "BlobServiceClient") as MockBSC:
            MockBSC.from_connection_string.return_value = bsc
            result = _make_tool().create_folder_and_file_in_blob_storage(
                "folder", "file.txt", "data"
            )

        assert "error" in result.lower()
        assert "quota exceeded" not in result

    def test_general_exception_returns_safe_message(self):
        with patch.object(_mod, "BlobServiceClient") as MockBSC:
            MockBSC.from_connection_string.side_effect = RuntimeError("unexpected")
            result = _make_tool().create_folder_and_file_in_blob_storage(
                "f", "n.txt", "c"
            )

        assert "An error occurred" in result
        assert "unexpected" not in result
