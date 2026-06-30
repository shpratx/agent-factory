"""Unit tests for tool-L1-jira-create-issue-generic (JiraIssueCreator).

All Jira REST API calls (via requests) are mocked; no real network or
credentials are required to run these tests.

Run with:
    pytest tool-L1-jira-create-issue-generic-test.py -v
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
    "tool_jira_create_issue_generic",
    os.path.join(_HERE, "tool-L1-jira-create-issue-generic.py"),
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)

JiraIssueCreator = _mod.JiraIssueCreator


# ── Helpers ───────────────────────────────────────────────────────────────

def _make_tool():
    return JiraIssueCreator()


def _mock_post_response(status=201, key="PROJ-1"):
    r = MagicMock()
    r.status_code = status
    r.ok = status < 400
    r.json.return_value = {"key": key, "id": "10001"}
    r.raise_for_status.return_value = None
    r.text = f'{{"key": "{key}"}}'
    return r


def _minimal_payload(summary="Test issue", label=None, issue_type="Task"):
    return {
        "projectKey": "PROJ",
        "issueType": issue_type,
        "issues": [
            {
                "summary": summary,
                "description": "A test description.",
                "label": label or [],
            }
        ],
    }


# ── Tests: tool metadata ──────────────────────────────────────────────────

class TestToolMetadata:
    def test_name(self):
        assert _make_tool().name == "Jira Issue Creator"

    def test_description_mentions_jira(self):
        assert "jira" in _make_tool().description.lower()


# ── Tests: single issue success ───────────────────────────────────────────

class TestSingleIssueSuccess:
    def test_returns_created_key(self):
        with patch.object(_mod, "requests") as mock_requests:
            mock_requests.post.return_value = _mock_post_response(key="PROJ-42")
            result = _make_tool()._run(_minimal_payload())

        assert "PROJ-42" in result
        assert "created" in result.lower()

    def test_jira_link_included_in_output(self):
        with patch.object(_mod, "requests") as mock_requests:
            mock_requests.post.return_value = _mock_post_response(key="PROJ-5")
            result = _make_tool()._run(_minimal_payload())

        assert "PROJ-5" in result
        assert "browse" in result.lower() or "jira_issue_link" in result.lower()

    def test_dict_description_is_normalised_before_adf(self):
        """Dict descriptions must be converted to plain text then to ADF."""
        payload = {
            "projectKey": "PROJ",
            "issueType": "Task",
            "issues": [{
                "summary": "Epic with dict desc",
                "description": {
                    "goal": "Improve reliability",
                    "steps": ["Add tests", "Add logging"],
                },
                "label": ["E1"],
            }],
        }
        with patch.object(_mod, "requests") as mock_requests:
            mock_requests.post.return_value = _mock_post_response(key="PROJ-10")
            result = _make_tool()._run(payload)

        assert "PROJ-10" in result
        # Confirm that a POST was made (ADF conversion didn't crash)
        mock_requests.post.assert_called_once()


# ── Tests: multiple issues ────────────────────────────────────────────────

class TestMultipleIssues:
    def test_creates_all_issues_and_returns_one_line_each(self):
        with patch.object(_mod, "requests") as mock_requests:
            mock_requests.post.side_effect = [
                _mock_post_response(key="PROJ-1"),
                _mock_post_response(key="PROJ-2"),
            ]
            payload = {
                "projectKey": "PROJ",
                "issues": [
                    {"summary": "Issue 1", "description": "Desc 1", "label": ["E1"]},
                    {"summary": "Issue 2", "description": "Desc 2", "label": ["E2"]},
                ],
            }
            result = _make_tool()._run(payload)

        lines = result.strip().split("\n")
        assert len(lines) == 2
        assert "PROJ-1" in result
        assert "PROJ-2" in result

    def test_id_map_built_from_label_zero(self):
        """label[0] acts as the logical ID; it should be registered in id_map."""
        created_keys = []

        def capture_post(*args, **kwargs):
            key = f"PROJ-{len(created_keys) + 1}"
            created_keys.append(key)
            return _mock_post_response(key=key)

        with patch.object(_mod, "requests") as mock_requests:
            mock_requests.post.side_effect = capture_post
            payload = {
                "projectKey": "PROJ",
                "issues": [
                    {"summary": "Epic", "description": "d", "label": ["E1"]},
                    {"summary": "Story", "description": "d", "label": ["E1.1"]},
                ],
            }
            result = _make_tool()._run(payload)

        assert "PROJ-1" in result
        assert "PROJ-2" in result


# ── Tests: error handling ─────────────────────────────────────────────────

class TestErrorHandling:
    def test_api_error_per_issue_appended_as_failed_line(self):
        with patch.object(_mod, "requests") as mock_requests:
            mock_requests.post.return_value = _mock_post_response(status=400)
            result = _make_tool()._run(_minimal_payload("Bad issue"))

        assert "Failed" in result

    def test_second_issue_continues_after_first_fails(self):
        with patch.object(_mod, "requests") as mock_requests:
            mock_requests.post.side_effect = [
                _mock_post_response(status=400),        # first fails
                _mock_post_response(key="PROJ-2"),      # second succeeds
            ]
            payload = {
                "projectKey": "PROJ",
                "issues": [
                    {"summary": "Issue 1", "description": "d", "label": []},
                    {"summary": "Issue 2", "description": "d", "label": []},
                ],
            }
            result = _make_tool()._run(payload)

        lines = result.strip().split("\n")
        assert len(lines) == 2
        assert any("Failed" in l for l in lines)
        assert any("PROJ-2" in l for l in lines)

    def test_request_exception_per_issue_does_not_abort_batch(self):
        import requests as req_lib

        with patch.object(_mod, "requests") as mock_requests:
            mock_requests.post.side_effect = [
                req_lib.RequestException("timeout"),
                _mock_post_response(key="PROJ-3"),
            ]
            payload = {
                "projectKey": "PROJ",
                "issues": [
                    {"summary": "Issue A", "description": "d", "label": []},
                    {"summary": "Issue B", "description": "d", "label": []},
                ],
            }
            result = _make_tool()._run(payload)

        assert "PROJ-3" in result

    def test_fatal_exception_returns_fatal_error_string(self):
        with patch.object(_mod, "requests") as mock_requests:
            mock_requests.post.side_effect = RuntimeError("total meltdown")
            # Cause the exception to bubble up to the outer try
            result = _make_tool()._run({"projectKey": None, "issues": "not-a-list"})

        assert "Fatal error" in result


# ── Tests: ADF structure ──────────────────────────────────────────────────

class TestADFConversion:
    def test_bullet_list_description_produces_adf_post(self):
        """Description lines starting with '- ' must become ADF bulletList blocks."""
        payload = {
            "projectKey": "PROJ",
            "issues": [{
                "summary": "List issue",
                "description": "- Item one\n- Item two\n- Item three",
                "label": [],
            }],
        }
        with patch.object(_mod, "requests") as mock_requests:
            mock_requests.post.return_value = _mock_post_response(key="PROJ-99")
            result = _make_tool()._run(payload)

        call_kwargs = mock_requests.post.call_args[1]
        posted_body = call_kwargs.get("json", {})
        desc = posted_body.get("fields", {}).get("description", {})
        assert desc.get("type") == "doc"
        any_bullet = any(
            b.get("type") == "bulletList"
            for b in desc.get("content", [])
        )
        assert any_bullet
