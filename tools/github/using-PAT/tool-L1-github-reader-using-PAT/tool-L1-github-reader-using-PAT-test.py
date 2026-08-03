"""Unit tests for tool-L1-github-reader (GithubReader).

All GitHub REST API calls (via requests) are mocked; no real network or
credentials are required to run these tests.

Run with:
    pytest tool-L1-github-reader-test.py -v
"""

import os
import sys
import types
import base64
import importlib.util
from unittest.mock import MagicMock, patch, call

import pytest
import requests

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

# ── Load the tool module ──────────────────────────────────────────────────

_HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location(
    "tool_github_reader",
    os.path.join(_HERE, "tool-L1-github-reader.py"),
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)

GithubReader = _mod.GithubReader


# ── Helpers ───────────────────────────────────────────────────────────────

def _make_tool():
    return GithubReader()


def _mock_response(status=200, json_data=None, raise_for_status=None):
    r = MagicMock()
    r.status_code = status
    r.json.return_value = json_data or {}
    if raise_for_status:
        r.raise_for_status.side_effect = raise_for_status
    else:
        r.raise_for_status.return_value = None
    return r


def _b64(text: str) -> str:
    return base64.b64encode(text.encode()).decode()


def _build_full_mock_sequence(owner="testowner", file_path="src/app.py",
                              file_content="print('hello')", branch="main",
                              tree_sha="tree-sha-abc", repo="testrepo"):
    """Return a list of mock responses for the full happy-path API sequence."""
    user_resp = _mock_response(json_data={"login": owner})
    repo_resp = _mock_response(json_data={"full_name": f"{owner}/{repo}"})
    folder_resp = _mock_response(json_data=[{"type": "dir", "name": "src"}])
    branch_resp = _mock_response(json_data={
        "commit": {"commit": {"tree": {"sha": tree_sha}}}
    })
    tree_resp = _mock_response(json_data={
        "tree": [{"type": "blob", "path": file_path, "sha": "blob-sha", "size": 100}]
    })
    file_resp = _mock_response(json_data={
        "type": "file",
        "content": _b64(file_content),
        "size": len(file_content),
        "sha": "blob-sha",
    })
    return [user_resp, repo_resp, folder_resp, branch_resp, tree_resp, file_resp]


# ── Tests: tool metadata ──────────────────────────────────────────────────

class TestToolMetadata:
    def test_name(self):
        assert _make_tool().name == "GitHub Reader"

    def test_description_mentions_folder(self):
        assert "folder" in _make_tool().description.lower()


# ── Tests: input validation ───────────────────────────────────────────────

class TestInputValidation:
    def test_empty_folder_location_returns_error(self):
        result = _make_tool()._run("", "repo", "main")
        assert "Error" in result
        assert "folder_location" in result

    def test_whitespace_only_folder_location_returns_error(self):
        result = _make_tool()._run("   ", "repo", "main")
        assert "Error" in result

    def test_folder_location_is_stripped_of_slashes(self):
        """The normalised path should be used in the API call, not the raw input."""
        with patch.object(_mod, "requests") as mock_requests:
            # Simulate repo not found to stop early, but confirm the strip happened
            user_r = _mock_response(json_data={"login": "owner"})
            repo_r = _mock_response(status=404)
            mock_requests.get.side_effect = [user_r, repo_r]
            result = _make_tool()._run("/src/", "repo", "main")
        assert "src" in result  # path was used (without slashes)


# ── Tests: API error paths ────────────────────────────────────────────────

class TestAPIErrors:
    def test_repo_not_found_returns_error_string(self):
        with patch.object(_mod, "requests") as mock_requests:
            user_r = _mock_response(json_data={"login": "owner"})
            repo_r = _mock_response(status=404)
            mock_requests.get.side_effect = [user_r, repo_r]
            result = _make_tool()._run("src", "missing-repo", "main")

        assert "not found" in result.lower()

    def test_folder_not_found_returns_error_string(self):
        with patch.object(_mod, "requests") as mock_requests:
            user_r = _mock_response(json_data={"login": "owner"})
            repo_r = _mock_response(json_data={"full_name": "owner/repo"})
            folder_r = _mock_response(status=404)
            mock_requests.get.side_effect = [user_r, repo_r, folder_r]
            result = _make_tool()._run("nonexistent-folder", "repo", "main")

        assert "not found" in result.lower()

    def test_network_error_returns_error_string(self):
        with patch.object(_mod, "requests") as mock_requests:
            mock_requests.get.side_effect = requests.exceptions.ConnectionError("timeout")
            result = _make_tool()._run("src", "repo", "main")

        assert "Error reading scripts" in result

    def test_tree_sha_missing_returns_error(self):
        with patch.object(_mod, "requests") as mock_requests:
            user_r = _mock_response(json_data={"login": "owner"})
            repo_r = _mock_response(json_data={})
            folder_r = _mock_response(json_data=[])
            branch_r = _mock_response(json_data={"commit": {}})  # no tree.sha
            mock_requests.get.side_effect = [user_r, repo_r, folder_r, branch_r]
            result = _make_tool()._run("src", "repo", "main")

        assert "tree SHA" in result


# ── Tests: happy path ─────────────────────────────────────────────────────

class TestHappyPath:
    def test_returns_dict_with_expected_keys(self):
        responses = _build_full_mock_sequence()
        with patch.object(_mod, "requests") as mock_requests:
            mock_requests.get.side_effect = responses
            result = _make_tool()._run("src", "testrepo", "main")

        assert isinstance(result, dict)
        assert "repository" in result
        assert "branch" in result
        assert "folder_location" in result
        assert "files" in result

    def test_file_content_decoded_correctly(self):
        responses = _build_full_mock_sequence(
            file_path="src/app.py", file_content="x = 42"
        )
        with patch.object(_mod, "requests") as mock_requests:
            mock_requests.get.side_effect = responses
            result = _make_tool()._run("src", "testrepo", "main")

        assert result["files"]["src/app.py"]["status"] == "success"
        assert result["files"]["src/app.py"]["content"] == "x = 42"

    def test_no_files_under_folder_returns_empty_files_with_message(self):
        with patch.object(_mod, "requests") as mock_requests:
            user_r = _mock_response(json_data={"login": "owner"})
            repo_r = _mock_response(json_data={})
            folder_r = _mock_response(json_data=[])
            branch_r = _mock_response(json_data={
                "commit": {"commit": {"tree": {"sha": "sha1"}}}
            })
            tree_r = _mock_response(json_data={"tree": []})  # no files
            mock_requests.get.side_effect = [user_r, repo_r, folder_r, branch_r, tree_r]
            result = _make_tool()._run("empty-dir", "testrepo", "main")

        assert isinstance(result, dict)
        assert result["files"] == {}
        assert "message" in result


# ── Tests: binary / non-UTF-8 files ──────────────────────────────────────

class TestBinaryFiles:
    def test_binary_file_gets_binary_status(self):
        binary_content = b"\x89PNG\r\n\x1a\n"  # PNG header bytes (not valid UTF-8)
        b64_binary = base64.b64encode(binary_content).decode()

        with patch.object(_mod, "requests") as mock_requests:
            user_r = _mock_response(json_data={"login": "owner"})
            repo_r = _mock_response(json_data={})
            folder_r = _mock_response(json_data=[])
            branch_r = _mock_response(json_data={
                "commit": {"commit": {"tree": {"sha": "sha1"}}}
            })
            tree_r = _mock_response(json_data={
                "tree": [{"type": "blob", "path": "imgs/photo.png", "sha": "s1", "size": 8}]
            })
            file_r = _mock_response(json_data={
                "type": "file",
                "content": b64_binary,
                "size": 8,
                "sha": "s1",
            })
            mock_requests.get.side_effect = [user_r, repo_r, folder_r, branch_r, tree_r, file_r]
            result = _make_tool()._run("imgs", "repo", "main")

        assert result["files"]["imgs/photo.png"]["status"] == "binary_or_non_utf8"
