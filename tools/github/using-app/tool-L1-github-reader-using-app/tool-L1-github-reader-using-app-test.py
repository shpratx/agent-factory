"""Unit tests for tool-L1-github-reader-using-app (GithubAppReader).

All GitHub REST API calls (via requests) and JWT signing (via jwt.encode) are
mocked; no real network, App private key, or credentials are required to run
these tests.

Run with:
    pytest tool-L1-github-reader-using-app-test.py -v
"""

import base64
import os
import sys
import types
import importlib.util
from unittest.mock import MagicMock, patch

import pytest

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
    "tool_github_reader_using_app",
    os.path.join(_HERE, "tool-L1-github-reader-using-app.py"),
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)

GithubAppReader = _mod.GithubAppReader


# ── Helpers ───────────────────────────────────────────────────────────────

def _make_tool():
    return GithubAppReader()


def _mock_response(status=200, json_data=None):
    r = MagicMock()
    r.status_code = status
    r.json.return_value = json_data or {}
    r.raise_for_status.return_value = None
    return r


def _b64(text: str) -> str:
    return base64.b64encode(text.encode()).decode()


def _patch_owner_resolution(owner="testowner", repo="testrepo", token="ghs_faketoken"):
    """Bypass JWT signing / installation discovery for tests that only care
    about the file-reading logic, which is identical to the PAT tool once a
    token is in hand."""
    return patch.object(_mod, "_resolve_owner_and_token", return_value=(owner, repo, token))


def _build_full_mock_sequence(file_path="src/app.py", file_content="print('hello')"):
    """Mock responses for the happy-path sequence AFTER owner/token resolution."""
    repo_resp = _mock_response(json_data={"full_name": "testowner/testrepo"})
    folder_resp = _mock_response(json_data=[{"type": "dir", "name": "src"}])
    branch_resp = _mock_response(json_data={
        "commit": {"commit": {"tree": {"sha": "tree-sha-abc"}}}
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
    return [repo_resp, folder_resp, branch_resp, tree_resp, file_resp]


# ── Tests: tool metadata ──────────────────────────────────────────────────

class TestToolMetadata:
    def test_name(self):
        assert _make_tool().name == "GitHub App Reader"

    def test_description_mentions_app(self):
        assert "app" in _make_tool().description.lower()


# ── Tests: input validation (no auth needed) ──────────────────────────────

class TestInputValidation:
    def test_empty_folder_location_returns_error(self):
        result = _make_tool()._run("", "repo", "main")
        assert "Error" in result
        assert "folder_location" in result

    def test_whitespace_only_folder_location_returns_error(self):
        result = _make_tool()._run("   ", "repo", "main")
        assert "Error" in result


# ── Tests: happy path (owner/token resolution mocked away) ───────────────

class TestHappyPath:
    def test_returns_dict_with_expected_keys(self):
        with _patch_owner_resolution():
            with patch.object(_mod, "requests") as mock_requests:
                mock_requests.get.side_effect = _build_full_mock_sequence()
                result = _make_tool()._run("src", "testrepo", "main")

        assert isinstance(result, dict)
        assert result["repository"] == "testowner/testrepo"
        assert "files" in result

    def test_file_content_decoded_correctly(self):
        with _patch_owner_resolution():
            with patch.object(_mod, "requests") as mock_requests:
                mock_requests.get.side_effect = _build_full_mock_sequence(
                    file_path="src/app.py", file_content="x = 42"
                )
                result = _make_tool()._run("src", "testrepo", "main")

        assert result["files"]["src/app.py"]["status"] == "success"
        assert result["files"]["src/app.py"]["content"] == "x = 42"

    def test_no_files_under_folder_returns_empty_files_with_message(self):
        with _patch_owner_resolution():
            with patch.object(_mod, "requests") as mock_requests:
                repo_r = _mock_response(json_data={})
                folder_r = _mock_response(json_data=[])
                branch_r = _mock_response(json_data={
                    "commit": {"commit": {"tree": {"sha": "sha1"}}}
                })
                tree_r = _mock_response(json_data={"tree": []})
                mock_requests.get.side_effect = [repo_r, folder_r, branch_r, tree_r]
                result = _make_tool()._run("empty-dir", "testrepo", "main")

        assert result["files"] == {}
        assert "message" in result

    def test_truncated_tree_surfaces_warning_message(self):
        with _patch_owner_resolution():
            with patch.object(_mod, "requests") as mock_requests:
                repo_r = _mock_response(json_data={})
                folder_r = _mock_response(json_data=[])
                branch_r = _mock_response(json_data={
                    "commit": {"commit": {"tree": {"sha": "sha1"}}}
                })
                tree_r = _mock_response(json_data={
                    "tree": [{"type": "blob", "path": "src/app.py", "sha": "s1", "size": 10}],
                    "truncated": True,
                })
                file_r = _mock_response(json_data={
                    "type": "file", "content": _b64("x=1"), "size": 3, "sha": "s1",
                })
                mock_requests.get.side_effect = [repo_r, folder_r, branch_r, tree_r, file_r]
                result = _make_tool()._run("src", "testrepo", "main")

        assert "truncated" in result.get("message", "").lower()


# ── Tests: binary / non-UTF-8 files ──────────────────────────────────────

class TestBinaryFiles:
    def test_binary_file_gets_binary_status(self):
        binary_content = b"\x89PNG\r\n\x1a\n"
        b64_binary = base64.b64encode(binary_content).decode()

        with _patch_owner_resolution():
            with patch.object(_mod, "requests") as mock_requests:
                repo_r = _mock_response(json_data={})
                folder_r = _mock_response(json_data=[])
                branch_r = _mock_response(json_data={
                    "commit": {"commit": {"tree": {"sha": "sha1"}}}
                })
                tree_r = _mock_response(json_data={
                    "tree": [{"type": "blob", "path": "imgs/photo.png", "sha": "s1", "size": 8}]
                })
                file_r = _mock_response(json_data={
                    "type": "file", "content": b64_binary, "size": 8, "sha": "s1",
                })
                mock_requests.get.side_effect = [repo_r, folder_r, branch_r, tree_r, file_r]
                result = _make_tool()._run("imgs", "testrepo", "main")

        assert result["files"]["imgs/photo.png"]["status"] == "binary_or_non_utf8"


# ── Tests: API error paths ────────────────────────────────────────────────

class TestAPIErrors:
    def test_repo_not_found_returns_error_string(self):
        with _patch_owner_resolution():
            with patch.object(_mod, "requests") as mock_requests:
                mock_requests.get.return_value = _mock_response(status=404)
                result = _make_tool()._run("src", "missing-repo", "main")

        assert "not found" in result.lower()

    def test_owner_resolution_failure_returns_error_string(self):
        """RuntimeError from _resolve_owner_and_token (no installation, etc.)
        must be caught and turned into an error string, not raised."""
        with patch.object(
            _mod, "_resolve_owner_and_token",
            side_effect=RuntimeError("This GitHub App has no installations."),
        ):
            result = _make_tool()._run("src", "repo", "main")

        assert "Error reading scripts" in result
        assert "no installations" in result


# ── Tests: owner/token resolution (the part that differs from the PAT tool) ─

class TestOwnerResolution:
    """CLIENT_ID is patched in every test here: the debug copy under test
    ships with blank APP_ID/CLIENT_ID placeholders, and _generate_app_jwt()
    raises immediately if neither is set — before it ever reaches jwt.encode."""

    def test_explicit_owner_repo_skips_discovery(self):
        """Passing 'owner/repo' should call the /installation endpoint
        directly rather than listing all installations."""
        with patch.object(_mod, "CLIENT_ID", "test-client-id"):
            with patch.object(_mod, "requests") as mock_requests:
                install_check = _mock_response(json_data={"id": 42})
                token_resp = _mock_response(json_data={"token": "ghs_abc"})
                mock_requests.get.return_value = install_check
                mock_requests.post.return_value = token_resp

                owner, repo, token = _mod._resolve_owner_and_token("explicit-owner/my-repo")

        assert owner == "explicit-owner"
        assert repo == "my-repo"
        assert token == "ghs_abc"

    def test_no_installations_raises_runtime_error(self):
        with patch.object(_mod, "CLIENT_ID", "test-client-id"):
            with patch.object(_mod, "requests") as mock_requests:
                mock_requests.get.return_value = _mock_response(json_data=[])
                with pytest.raises(RuntimeError, match="no installations"):
                    _mod._resolve_owner_and_token("bare-repo-name")

    def test_single_installation_resolves_owner_from_account_login(self):
        with patch.object(_mod, "CLIENT_ID", "test-client-id"):
            with patch.object(_mod, "requests") as mock_requests:
                installations_resp = _mock_response(json_data=[
                    {"id": 7, "account": {"login": "solo-org"}}
                ])
                token_resp = _mock_response(json_data={"token": "ghs_solo"})
                mock_requests.get.return_value = installations_resp
                mock_requests.post.return_value = token_resp

                owner, repo, token = _mod._resolve_owner_and_token("some-repo")

        assert owner == "solo-org"
        assert repo == "some-repo"
        assert token == "ghs_solo"
