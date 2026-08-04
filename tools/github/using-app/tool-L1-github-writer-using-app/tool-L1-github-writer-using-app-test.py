"""Unit tests for tool-L1-github-writer-using-app (GithubCommitterTool).

All GitHub REST API calls (via requests) and JWT signing (via jwt.encode) are
mocked; no real network, App private key, or credentials are required to run
these tests.

Run with:
    pytest tool-L1-github-writer-using-app-test.py -v
"""

import os
import sys
import types
import importlib.util
from unittest.mock import MagicMock, patch

import pytest
import requests

# ── Stub crewai and jwt before the tool module is loaded ──────────────────

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

_mock_jwt = types.ModuleType("jwt")
_mock_jwt.encode = MagicMock(return_value="fake.jwt.token")
sys.modules.setdefault("jwt", _mock_jwt)

# ── Load the tool module (the debug copy — no AWS calls at import time) ────

_HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location(
    "tool_github_writer_using_app",
    os.path.join(_HERE, "tool-L1-github-writer-using-app.py"),
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


def _patch_owner_resolution(owner="testowner", repo="testrepo", token="ghs_faketoken"):
    return patch.object(_mod, "_resolve_owner_and_token", return_value=(owner, repo, token))


def _happy_path_responses(source_sha="src-sha", new_tree_sha="tree-sha", commit_sha="commit-sha"):
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


# ── Tests: successful commit (owner/token resolution mocked away) ─────────

class TestSuccessfulCommit:
    def test_flat_file_format_returns_success(self):
        get_src, create_ref, create_tree, create_commit, update_ref = _happy_path_responses()

        with _patch_owner_resolution(repo="my-repo"):
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

        with _patch_owner_resolution():
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

    def test_result_contains_github_url(self):
        get_src, create_ref, create_tree, create_commit, update_ref = _happy_path_responses()

        with _patch_owner_resolution(owner="target-org", repo="target-repo"):
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
        existing_ref = _mock_response(json_data={"object": {"sha": "existing-sha"}})
        create_tree = _mock_response(json_data={"sha": "new-tree"})
        create_commit = _mock_response(json_data={"sha": "new-commit"})
        update_ref = _mock_response(json_data={})

        with _patch_owner_resolution():
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


# ── Tests: owner resolution failure (before any write is attempted) ──────

class TestOwnerResolutionFailure:
    def test_no_installations_returns_failure_without_writing(self):
        with patch.object(
            _mod, "_resolve_owner_and_token",
            side_effect=RuntimeError("This GitHub App has no installations."),
        ):
            with patch.object(_mod, "requests") as mock_requests:
                result = _make_tool()._run(
                    files=[{"filename": "f.py", "code": "x"}],
                    repo_name="repo",
                    new_branch="branch",
                )

        assert result["status"] == "failure"
        assert "no installations" in result["message"]
        mock_requests.get.assert_not_called()
        mock_requests.post.assert_not_called()


# ── Tests: error handling ─────────────────────────────────────────────────

class TestErrorHandling:
    def test_403_forbidden_includes_contents_permission_hint(self):
        """The App-specific diagnostic must surface the Contents-permission hint."""
        forbidden = MagicMock()
        forbidden.status_code = 403
        forbidden.text = "Forbidden"
        http_error = requests.exceptions.HTTPError("403 Client Error: Forbidden")
        http_error.response = forbidden
        get_src = _mock_response(json_data={"object": {"sha": "src-sha"}})
        create_ref_resp = MagicMock()
        create_ref_resp.status_code = 403
        create_ref_resp.raise_for_status.side_effect = http_error

        with _patch_owner_resolution():
            with patch.object(_mod, "requests") as mock_requests:
                mock_requests.exceptions = requests.exceptions
                mock_requests.get.return_value = get_src
                mock_requests.post.return_value = create_ref_resp

                result = _make_tool()._run(
                    files=[{"filename": "f.py", "code": "x"}],
                    repo_name="repo",
                    new_branch="branch",
                )

        assert result["status"] == "failure"
        assert "Contents" in result["message"]
        assert "Read and write" in result["message"]

    def test_general_exception_returns_failure_dict(self):
        with _patch_owner_resolution():
            with patch.object(_mod, "requests") as mock_requests:
                mock_requests.exceptions = requests.exceptions
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

        with _patch_owner_resolution():
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
