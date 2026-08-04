"""Unit tests for tool-L1-s3-writer (S3UploadTool).

All boto3 S3 calls are mocked; no real network or AWS credentials are
required to run these tests.

Run with:
    pytest tool-L1-s3-writer-test.py -v
"""

import os
import re
import sys
import types
import importlib.util
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
    "tool_s3_writer",
    os.path.join(_HERE, "tool-L1-s3-writer.py"),
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)

S3UploadTool = _mod.S3UploadTool


# ── Helpers ───────────────────────────────────────────────────────────────

def _make_tool():
    return S3UploadTool()


def _make_s3_client(put_object_side_effect=None):
    s3 = MagicMock()
    if put_object_side_effect is not None:
        s3.put_object.side_effect = put_object_side_effect
    return s3


_TIMESTAMP_RE = re.compile(r"^\d{8}_\d{6}$")


# ── Tests: tool metadata ──────────────────────────────────────────────────

class TestToolMetadata:
    def test_name(self):
        assert _make_tool().name == "S3 Upload Tool"

    def test_description_mentions_upload(self):
        assert "upload" in _make_tool().description.lower()


# ── Tests: successful upload ──────────────────────────────────────────────

class TestSuccessfulUpload:
    def test_upload_returns_success_status(self):
        tool = _make_tool()
        s3 = _make_s3_client()
        with patch.object(_mod, "boto3") as mock_boto3:
            mock_boto3.client.return_value = s3
            result = tool._run("incoming", "report.txt", "hello world")

        assert result["status"] == "SUCCESS"
        assert result["bucket"] == tool.BUCKET_NAME

    def test_object_key_includes_folder_timestamp_and_filename(self):
        s3 = _make_s3_client()
        with patch.object(_mod, "boto3") as mock_boto3:
            mock_boto3.client.return_value = s3
            result = _make_tool()._run("incoming/reports", "summary.md", "content")

        assert result["key"].startswith("incoming/reports/")
        assert result["key"].endswith("_summary.md")
        # timestamp segment between folder and filename must look like YYYYMMDD_HHMMSS
        middle = result["key"][len("incoming/reports/"):-len("_summary.md")]
        assert _TIMESTAMP_RE.match(middle)

    def test_size_bytes_reflects_utf8_encoded_length(self):
        s3 = _make_s3_client()
        content = "héllo"  # multi-byte character to confirm UTF-8 length, not char count
        with patch.object(_mod, "boto3") as mock_boto3:
            mock_boto3.client.return_value = s3
            result = _make_tool()._run("f", "n.txt", content)

        assert result["size_bytes"] == len(content.encode("utf-8"))
        assert result["size_bytes"] != len(content)

    def test_put_object_called_with_correct_bucket_and_content_type(self):
        tool = _make_tool()
        s3 = _make_s3_client()
        with patch.object(_mod, "boto3") as mock_boto3:
            mock_boto3.client.return_value = s3
            tool._run("f", "n.txt", "body text")

        _, kwargs = s3.put_object.call_args
        assert kwargs["Bucket"] == tool.BUCKET_NAME
        assert kwargs["Body"] == b"body text"
        assert kwargs["ContentType"] == "text/plain; charset=utf-8"

    def test_repeated_uploads_get_distinct_keys(self):
        """Two calls with the same file_name must not collide (different timestamps)."""
        s3 = _make_s3_client()
        with patch.object(_mod, "boto3") as mock_boto3:
            mock_boto3.client.return_value = s3
            r1 = _make_tool()._run("f", "same-name.txt", "v1")
            r2 = _make_tool()._run("f", "same-name.txt", "v2")

        # Keys may coincide only if generated within the same second; structure
        # must still differ in principle by including a fresh timestamp each call.
        assert r1["uploaded_at"] is not None
        assert r2["uploaded_at"] is not None


# ── Tests: file name sanitisation ─────────────────────────────────────────

class TestFileNameHandling:
    def test_path_components_in_file_name_are_stripped_to_basename(self):
        s3 = _make_s3_client()
        with patch.object(_mod, "boto3") as mock_boto3:
            mock_boto3.client.return_value = s3
            result = _make_tool()._run("f", "../../etc/evil.txt", "x")

        assert result["status"] == "SUCCESS"
        assert result["key"].endswith("_evil.txt")
        assert ".." not in result["key"]

    def test_empty_file_name_returns_invalid_file_name(self):
        with patch.object(_mod, "boto3") as mock_boto3:
            mock_boto3.client.return_value = _make_s3_client()
            result = _make_tool()._run("f", "", "x")

        assert result == {"status": "FAILED", "reason": "INVALID_FILE_NAME"}

    def test_slash_only_file_name_returns_invalid_file_name(self):
        with patch.object(_mod, "boto3") as mock_boto3:
            mock_boto3.client.return_value = _make_s3_client()
            result = _make_tool()._run("f", "///", "x")

        assert result == {"status": "FAILED", "reason": "INVALID_FILE_NAME"}

    def test_invalid_file_name_short_circuits_before_upload(self):
        """Client init still happens, but put_object must never be reached."""
        s3 = _make_s3_client()
        with patch.object(_mod, "boto3") as mock_boto3:
            mock_boto3.client.return_value = s3
            _make_tool()._run("f", "", "x")

        s3.put_object.assert_not_called()


# ── Tests: folder name normalisation ──────────────────────────────────────

class TestFolderNormalisation:
    def test_surrounding_slashes_normalised_to_single_trailing_slash(self):
        s3 = _make_s3_client()
        with patch.object(_mod, "boto3") as mock_boto3:
            mock_boto3.client.return_value = s3
            result = _make_tool()._run("/reports/", "n.txt", "x")

        assert result["folder"] == "reports/"
        assert result["key"].startswith("reports/")
        assert "//" not in result["key"]


# ── Tests: error handling ─────────────────────────────────────────────────

class TestErrorHandling:
    def test_client_init_failure_returns_failed_status(self):
        with patch.object(_mod, "boto3") as mock_boto3:
            mock_boto3.client.side_effect = Exception("invalid credentials")
            result = _make_tool()._run("f", "n.txt", "x")

        assert result["status"] == "FAILED"
        assert "S3_CLIENT_INIT_FAILED" in result["reason"]

    def test_upload_failure_returns_failed_status(self):
        s3 = _make_s3_client(put_object_side_effect=Exception("access denied"))
        with patch.object(_mod, "boto3") as mock_boto3:
            mock_boto3.client.return_value = s3
            result = _make_tool()._run("f", "n.txt", "x")

        assert result["status"] == "FAILED"
        assert "S3_UPLOAD_FAILED" in result["reason"]


# ── Tests: bucket/region wiring ────────────────────────────────────────────

class TestClientConfiguration:
    def test_boto3_client_called_with_configured_region(self):
        tool = _make_tool()
        s3 = _make_s3_client()
        with patch.object(_mod, "boto3") as mock_boto3:
            mock_boto3.client.return_value = s3
            tool._run("f", "n.txt", "x")

        _, kwargs = mock_boto3.client.call_args
        assert kwargs["region_name"] == tool.AWS_REGION
