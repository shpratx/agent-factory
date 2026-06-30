"""Unit tests for tool-L1-github-writer-generic (GithubCommitterTool).

All GitHub REST API calls (via requests) are mocked; no real network or
credentials are required to run these tests.

Run with:
    pytest tool-L1-github-writer-generic-test.py -v
"""

import os
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

# ── Load the tool module ──────────────────────────────────────────────────

_HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location(
    "tool_github_writer",
    os.path.join(_HERE, "tool-L1-github-writer-generic.py"),
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)

GithubCommitterTool = _mod.GithubCommitterTool


# ── Helpers ───────────────────────────────────────────────────────────────

def _make_tool():
    return GithubCommitterTool()


def _mock_response(status=200, json_data=None):
    r = MagicMock()
    r.status_code = status
    r.json.return_value = json_data or {}
    r.raise_for_status.return_value = None
    return r


def _happy_path_responses(source_sha="src-sha", new_tree_sha="tree-sha", commit_sha="commit-sha"):
    """Return side_effect list covering the full happy-path for a new branch."""
    get_source = _mock_response(json_data={"object": {"sha": source_sha}})
    create_ref = _mock_response(status=201, json_data={"ref": "refs/heads/feature/x"})
    create_tree = _mock_response(json_data={"sha": new_tree_sha})
    create_commit = _mock_response(json_data={"sha": commit_sha})
    update_ref = _mock_response(json_data={"ref": "refs/heads/feature/x"})
    return get_source, create_ref, create_tree, create_commit, update_ref


# ── Tests: tool metadata ──────────────────────────────────────────────────

class TestToolMetadata:
    def test_name(self):
        assert _make_tool().name == "Github Branch Committer"

    def test_description_mentions_branch(self):
        assert "branch" in _make_tool().description.lower()


# ── Tests: successful commit (flat file format) ───────────────────────────

class TestSuccessfulCommit:
    def test_flat_file_format_returns_success(self):
        get_src, create_ref, create_tree, create_commit, update_ref = _happy_path_responses()

        with patch.object(_mod, "requests") as mock_requests:
            mock_requests.get.return_value = get_src
            mock_requests.post.side_effect = [create_ref, create_tree, create_commit]
            mock_requests.patch.return_value = update_ref

            result = _make_tool()._run(
                files=[{"filename": "docs/readme.md", "code": "# Hello"}],
                repo_name="my-repo",
                new_branch="feature/auto-update",
                source_branch="main",
            )

        assert result["status"] == "success"
        assert result["branch"] == "feature/auto-update"
        assert "docs/readme.md" in result["updated_files"]
        assert "my-repo" in result["url"]

    def test_nested_file_format_resolves_path(self):
        get_src, create_ref, create_tree, create_commit, update_ref = _happy_path_responses()

        with patch.object(_mod, "requests") as mock_requests:
            mock_requests.get.return_value = get_src
            mock_requests.post.side_effect = [create_ref, create_tree, create_commit]
            mock_requests.patch.return_value = update_ref

            result = _make_tool()._run(
                files=[{"src/utils": {"filename": "helpers.py", "code": "def add(a,b): return a+b"}}],
                repo_name="my-repo",
                new_branch="feature/helpers",
                source_branch="main",
            )

        assert result["status"] == "success"
        assert "src/utils/helpers.py" in result["updated_files"]

    def test_multiple_files_committed_together(self):
        get_src, create_ref, create_tree, create_commit, update_ref = _happy_path_responses()

        with patch.object(_mod, "requests") as mock_requests:
            mock_requests.get.return_value = get_src
            mock_requests.post.side_effect = [create_ref, create_tree, create_commit]
            mock_requests.patch.return_value = update_ref

            result = _make_tool()._run(
                files=[
                    {"filename": "a.py", "code": "a=1"},
                    {"filename": "b.py", "code": "b=2"},
                ],
                repo_name="repo",
                new_branch="feature/multi",
            )

        assert result["status"] == "success"
        assert len(result["updated_files"]) == 2

    def test_result_contains_github_url(self):
        get_src, create_ref, create_tree, create_commit, update_ref = _happy_path_responses()

        with patch.object(_mod, "requests") as mock_requests:
            mock_requests.get.return_value = get_src
            mock_requests.post.side_effect = [create_ref, create_tree, create_commit]
            mock_requests.patch.return_value = update_ref

            result = _make_tool()._run(
                files=[{"filename": "f.py", "code": "x=1"}],
                repo_name="target-repo",
                new_branch="feature/xyz",
            )

        assert result["url"].startswith("https://github.com/")
        assert "feature/xyz" in result["url"]


# ── Tests: existing branch handling (422) ────────────────────────────────

class TestExistingBranch:
    def test_422_on_create_ref_commits_on_existing_branch(self):
        get_src = _mock_response(json_data={"object": {"sha": "src-sha"}})
        create_ref_422 = _mock_response(status=422)
        create_ref_422.raise_for_status.return_value = None  # 422 is handled, not raised

        existing_ref = _mock_response(json_data={"object": {"sha": "existing-sha"}})
        create_tree = _mock_response(json_data={"sha": "new-tree"})
        create_commit = _mock_response(json_data={"sha": "new-commit"})
        update_ref = _mock_response(json_data={})

        with patch.object(_mod, "requests") as mock_requests:
            mock_requests.get.side_effect = [get_src, existing_ref]
            mock_requests.post.side_effect = [create_ref_422, create_tree, create_commit]
            mock_requests.patch.return_value = update_ref

            result = _make_tool()._run(
                files=[{"filename": "update.py", "code": "v=2"}],
                repo_name="repo",
                new_branch="existing-branch",
            )

        assert result["status"] == "success"


# ── Tests: error handling ─────────────────────────────────────────────────

class TestErrorHandling:
    def test_api_error_returns_failure_dict(self):
        import requests as req_lib

        with patch.object(_mod, "requests") as mock_requests:
            mock_requests.get.side_effect = req_lib.exceptions.HTTPError("401 Unauthorized")
            result = _make_tool()._run(
                files=[{"filename": "f.py", "code": "x"}],
                repo_name="repo",
                new_branch="branch",
            )

        assert result["status"] == "failure"
        assert "message" in result

    def test_general_exception_returns_failure_dict(self):
        with patch.object(_mod, "requests") as mock_requests:
            mock_requests.get.side_effect = Exception("unexpected SDK error")
            result = _make_tool()._run(
                files=[{"filename": "f.py", "code": "x"}],
                repo_name="repo",
                new_branch="branch",
            )

        assert result["status"] == "failure"
        assert "message" in result

    def test_missing_filename_defaults_gracefully(self):
        """A file descriptor missing 'filename' must fall back to 'script.py'."""
        get_src, create_ref, create_tree, create_commit, update_ref = _happy_path_responses()

        with patch.object(_mod, "requests") as mock_requests:
            mock_requests.get.return_value = get_src
            mock_requests.post.side_effect = [create_ref, create_tree, create_commit]
            mock_requests.patch.return_value = update_ref

            result = _make_tool()._run(
                files=[{"code": "print('hi')"}],  # no 'filename'
                repo_name="repo",
                new_branch="branch",
            )

        assert result["status"] == "success"
        assert any("script.py" in p for p in result["updated_files"])
