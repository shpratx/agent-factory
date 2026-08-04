"""Unit tests for tool-L1-s3-reader (S3DocumentRetriever).

All boto3 S3 calls are mocked; no real network or AWS credentials are
required to run these tests.

Run with:
    pytest tool-L1-s3-reader-test.py -v
"""

import os
import sys
import types
import importlib.util
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import pytest

# ── Stub crewai before the tool module is loaded ──────────────────────────

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

# boto3 isn't a test dependency — every real call is mocked per-test via
# patch.object(_mod, "boto3"), so a bare stub is enough to satisfy the import.
sys.modules.setdefault("boto3", types.ModuleType("boto3"))

# ── Load the tool module (the debug copy — no AWS calls at import time) ────

_HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location(
    "tool_s3_reader",
    os.path.join(_HERE, "tool-L1-s3-reader.py"),
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)

S3DocumentRetriever = _mod.S3DocumentRetriever


# ── Helpers ───────────────────────────────────────────────────────────────

def _make_tool():
    return S3DocumentRetriever()


def _obj(key, size=10, last_modified=None):
    return {
        "Key": key,
        "Size": size,
        "LastModified": last_modified or datetime(2026, 1, 1, tzinfo=timezone.utc),
    }


def _make_s3_client(objects_by_page, get_object_side_effect=None):
    """Return a MagicMock boto3 S3 client with a working paginator."""
    s3 = MagicMock()
    paginator = MagicMock()
    paginator.paginate.return_value = [{"Contents": page} for page in objects_by_page]
    s3.get_paginator.return_value = paginator
    if get_object_side_effect is not None:
        s3.get_object.side_effect = get_object_side_effect
    return s3


def _body(text: str):
    """Build a mock S3 get_object response body."""
    b = MagicMock()
    b.read.return_value = text.encode("utf-8") if isinstance(text, str) else text
    return {"Body": b}


# ── Tests: tool metadata ──────────────────────────────────────────────────

class TestToolMetadata:
    def test_name(self):
        assert _make_tool().name == "S3 Document Retriever"

    def test_description_mentions_folder(self):
        assert "folder" in _make_tool().description.lower()


# ── Tests: successful reads ───────────────────────────────────────────────

class TestSuccessfulReads:
    def test_reads_single_file(self):
        s3 = _make_s3_client(
            [[_obj("reports/summary.md", size=20)]],
            get_object_side_effect=[_body("# Summary\nAll good.")],
        )
        with patch.object(_mod, "boto3") as mock_boto3:
            mock_boto3.client.return_value = s3
            result = _make_tool()._run("reports")

        assert "FILE_COUNT: 1" in result
        assert "reports/summary.md" in result
        assert "# Summary" in result

    def test_reads_multiple_files_sorted_by_key(self):
        s3 = _make_s3_client(
            [[_obj("data/b.txt", size=4), _obj("data/a.txt", size=5)]],
            get_object_side_effect=[_body("Beta"), _body("Alpha")],
        )
        with patch.object(_mod, "boto3") as mock_boto3:
            mock_boto3.client.return_value = s3
            result = _make_tool()._run("data")

        assert "FILE_COUNT: 2" in result
        # Sorted by key: a.txt before b.txt regardless of listing order
        assert result.index("data/a.txt") < result.index("data/b.txt")

    def test_folder_marker_object_is_skipped(self):
        """The zero-byte 'folder/' marker object must not be counted or read."""
        s3 = _make_s3_client(
            [[_obj("docs/", size=0), _obj("docs/file.txt", size=12)]],
            get_object_side_effect=[_body("real content")],
        )
        with patch.object(_mod, "boto3") as mock_boto3:
            mock_boto3.client.return_value = s3
            result = _make_tool()._run("docs")

        assert "FILE_COUNT: 1" in result
        assert "docs/file.txt" in result

    def test_pagination_across_multiple_pages(self):
        s3 = _make_s3_client(
            [[_obj("p/1.txt", size=1)], [_obj("p/2.txt", size=1)]],
            get_object_side_effect=[_body("1"), _body("2")],
        )
        with patch.object(_mod, "boto3") as mock_boto3:
            mock_boto3.client.return_value = s3
            result = _make_tool()._run("p")

        assert "FILE_COUNT: 2" in result
        assert "p/1.txt" in result
        assert "p/2.txt" in result


# ── Tests: edge cases ─────────────────────────────────────────────────────

class TestEdgeCases:
    def test_empty_folder_returns_retrieve_failed(self):
        s3 = _make_s3_client([[]])
        with patch.object(_mod, "boto3") as mock_boto3:
            mock_boto3.client.return_value = s3
            result = _make_tool()._run("empty-dir")

        assert "S3_RETRIEVE_FAILED" in result
        assert "empty-dir" in result

    def test_oversized_file_is_skipped_not_downloaded(self):
        tool = _make_tool()
        s3 = _make_s3_client([[_obj("big/file.bin", size=tool.MAX_FILE_BYTES + 1)]])
        with patch.object(_mod, "boto3") as mock_boto3:
            mock_boto3.client.return_value = s3
            result = tool._run("big")

        assert "[SKIPPED: file exceeds size limit]" in result
        s3.get_object.assert_not_called()

    def test_binary_content_flagged_without_crashing(self):
        s3 = _make_s3_client(
            [[_obj("imgs/photo.png", size=8)]],
            get_object_side_effect=[_body(b"\x89PNG\r\n\x1a\n")],
        )
        with patch.object(_mod, "boto3") as mock_boto3:
            mock_boto3.client.return_value = s3
            result = _make_tool()._run("imgs")

        assert "BINARY OR NON-UTF8 CONTENT" in result

    def test_per_file_read_failure_does_not_abort_other_files(self):
        s3 = _make_s3_client(
            [[_obj("data/bad.txt", size=3), _obj("data/good.txt", size=4)]],
            get_object_side_effect=[Exception("transient S3 error"), _body("good")],
        )
        with patch.object(_mod, "boto3") as mock_boto3:
            mock_boto3.client.return_value = s3
            result = _make_tool()._run("data")

        assert "[READ_FAILED:" in result
        assert "good" in result

    def test_list_failure_returns_labelled_error(self):
        s3 = MagicMock()
        s3.get_paginator.side_effect = Exception("bucket does not exist")
        with patch.object(_mod, "boto3") as mock_boto3:
            mock_boto3.client.return_value = s3
            result = _make_tool()._run("anything")

        assert "S3_LIST_FAILED" in result

    def test_client_init_failure_returns_labelled_error(self):
        with patch.object(_mod, "boto3") as mock_boto3:
            mock_boto3.client.side_effect = Exception("invalid credentials")
            result = _make_tool()._run("anything")

        assert "S3_CLIENT_INIT_FAILED" in result

    def test_folder_name_is_normalised_to_prefix(self):
        """A folder name with surrounding slashes must be normalised to '<name>/'."""
        s3 = _make_s3_client([[]])
        with patch.object(_mod, "boto3") as mock_boto3:
            mock_boto3.client.return_value = s3
            _make_tool()._run("/reports/")

        call_kwargs = s3.get_paginator.return_value.paginate.call_args[1]
        assert call_kwargs["Prefix"] == "reports/"


# ── Tests: bucket/region wiring ────────────────────────────────────────────

class TestClientConfiguration:
    def test_boto3_client_called_with_configured_bucket_and_region(self):
        tool = _make_tool()
        s3 = _make_s3_client([[]])
        with patch.object(_mod, "boto3") as mock_boto3:
            mock_boto3.client.return_value = s3
            tool._run("anything")

        _, kwargs = mock_boto3.client.call_args
        assert kwargs["region_name"] == tool.AWS_REGION
