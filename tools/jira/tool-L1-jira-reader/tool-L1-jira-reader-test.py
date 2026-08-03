"""Unit tests for tool-L1-jira-fetch-issue (JiraIssueTreeFetcher).

All Jira REST API calls (via requests) are mocked; no real network or
credentials are required to run these tests.

Run with:
    pytest tool-L1-jira-fetch-issue-test.py -v
"""

import json
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
    "tool_jira_fetch_issue",
    os.path.join(_HERE, "tool-L1-jira-fetch-issue.py"),
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)

JiraIssueTreeFetcher = _mod.JiraIssueTreeFetcher


# ── Helpers ───────────────────────────────────────────────────────────────

def _make_tool():
    return JiraIssueTreeFetcher()


def _raw_issue(key="DEMO-1", summary="Test Issue", status="To Do",
               description=None, labels=None, assignee=None):
    return {
        "key": key,
        "fields": {
            "summary": summary,
            "status": {"name": status},
            "description": description,
            "labels": labels or [],
            "assignee": {"displayName": assignee} if assignee else None,
            "duedate": None,
            "reporter": None,
        },
    }


def _mock_get_response(status=200, json_data=None, ok=True):
    r = MagicMock()
    r.status_code = status
    r.ok = ok
    r.json.return_value = json_data or {}
    r.text = json.dumps(json_data or {})
    r.raise_for_status.return_value = None
    return r


def _mock_post_response(issues=None, is_last=True):
    r = MagicMock()
    r.ok = True
    r.json.return_value = {"issues": issues or [], "isLast": is_last}
    return r


# ── Tests: tool metadata ──────────────────────────────────────────────────

class TestToolMetadata:
    def test_name(self):
        assert _make_tool().name == "Jira Issue Tree Fetcher"

    def test_description_mentions_jira(self):
        assert "jira" in _make_tool().description.lower()


# ── Tests: input coercion ─────────────────────────────────────────────────

class TestInputCoercion:
    def test_bare_string_coerced_to_single_key(self):
        schema = _mod.JiraIssueTreeFetcherSchema
        result = schema.model_validate({"inputJSON": "DEMO-1"})
        assert result.inputJSON == {"key": "DEMO-1"}

    def test_comma_separated_string_coerced_to_keys_list(self):
        schema = _mod.JiraIssueTreeFetcherSchema
        result = schema.model_validate({"inputJSON": "DEMO-1, DEMO-2"})
        assert result.inputJSON == {"keys": ["DEMO-1", "DEMO-2"]}

    def test_list_coerced_to_keys_dict(self):
        schema = _mod.JiraIssueTreeFetcherSchema
        result = schema.model_validate({"inputJSON": ["DEMO-1", "DEMO-2"]})
        assert result.inputJSON == {"keys": ["DEMO-1", "DEMO-2"]}

    def test_json_string_array_coerced(self):
        schema = _mod.JiraIssueTreeFetcherSchema
        result = schema.model_validate({"inputJSON": '["DEMO-1"]'})
        assert result.inputJSON == {"keys": ["DEMO-1"]}


# ── Tests: missing key/keys ───────────────────────────────────────────────

class TestMissingKeys:
    def test_missing_key_and_keys_returns_fatal_error(self):
        result = _make_tool()._run({})
        assert "Fatal error" in result
        assert "key" in result.lower()


# ── Tests: single key success ─────────────────────────────────────────────

class TestSingleKeySuccess:
    def test_returns_json_with_fixed_schema(self):
        raw = _raw_issue("DEMO-1", "Platform Foundation", "To Do")

        with patch.object(_mod, "requests") as mock_requests:
            mock_requests.get.return_value = _mock_get_response(json_data=raw)
            mock_requests.post.return_value = _mock_post_response(issues=[], is_last=True)

            result = _make_tool()._run({"key": "DEMO-1"})

        data = json.loads(result)
        assert data["issue_id"] == "DEMO-1"
        assert data["title"] == "Platform Foundation"
        assert data["status"] == "To Do"
        assert "children" in data
        assert "child_work_item_ids" in data

    def test_returns_single_object_not_array_for_single_key(self):
        raw = _raw_issue("DEMO-5")

        with patch.object(_mod, "requests") as mock_requests:
            mock_requests.get.return_value = _mock_get_response(json_data=raw)
            mock_requests.post.return_value = _mock_post_response(is_last=True)

            result = _make_tool()._run({"key": "DEMO-5"})

        data = json.loads(result)
        assert isinstance(data, dict)
        assert data["issue_id"] == "DEMO-5"


# ── Tests: multiple keys ──────────────────────────────────────────────────

class TestMultipleKeys:
    def test_returns_json_array_for_multiple_keys(self):
        raw1 = _raw_issue("DEMO-1", "Epic One")
        raw2 = _raw_issue("DEMO-2", "Epic Two")

        with patch.object(_mod, "requests") as mock_requests:
            mock_requests.get.side_effect = [
                _mock_get_response(json_data=raw1),
                _mock_get_response(json_data=raw2),
            ]
            mock_requests.post.return_value = _mock_post_response(is_last=True)

            result = _make_tool()._run({"keys": ["DEMO-1", "DEMO-2"]})

        data = json.loads(result)
        assert isinstance(data, list)
        assert len(data) == 2


# ── Tests: include_children=False ────────────────────────────────────────

class TestIncludeChildrenFalse:
    def test_no_children_fetched_when_disabled(self):
        raw = _raw_issue("DEMO-1")

        with patch.object(_mod, "requests") as mock_requests:
            mock_requests.get.return_value = _mock_get_response(json_data=raw)

            result = _make_tool()._run({"key": "DEMO-1", "includeChildren": False})

        mock_requests.post.assert_not_called()
        data = json.loads(result)
        assert data["children"] == []


# ── Tests: nested children ────────────────────────────────────────────────

class TestNestedChildren:
    def test_child_issues_returned_in_children_list(self):
        parent = _raw_issue("DEMO-1", "Epic")
        child = _raw_issue("DEMO-2", "Story")

        with patch.object(_mod, "requests") as mock_requests:
            mock_requests.get.side_effect = [
                _mock_get_response(json_data=parent),   # get parent
                _mock_get_response(json_data=child),    # get child
            ]
            mock_requests.post.side_effect = [
                _mock_post_response(issues=[child], is_last=True),  # children of parent
                _mock_post_response(issues=[], is_last=True),       # children of child (leaf)
            ]

            result = _make_tool()._run({"key": "DEMO-1", "maxDepth": 2})

        data = json.loads(result)
        assert len(data["children"]) == 1
        assert data["children"][0]["issue_id"] == "DEMO-2"
        assert data["child_work_item_ids"] == ["DEMO-2"]


# ── Tests: API error per key ──────────────────────────────────────────────

class TestAPIError:
    def test_http_error_for_key_returns_error_node(self):
        error_resp = _mock_get_response(status=404, ok=False)
        error_resp.text = "Not Found"

        with patch.object(_mod, "requests") as mock_requests:
            mock_requests.get.return_value = error_resp

            result = _make_tool()._run({"key": "DEMO-404"})

        data = json.loads(result)
        assert "error" in data
        assert "404" in data["error"]

    def test_network_error_returns_fatal_error_string(self):
        import requests as req_lib

        with patch.object(_mod, "requests") as mock_requests:
            mock_requests.get.side_effect = req_lib.RequestException("network down")

            result = _make_tool()._run({"key": "DEMO-1"})

        assert "Fatal error" in result


# ── Tests: ADF to plain text ──────────────────────────────────────────────

class TestADFToText:
    def setup_method(self):
        self.tool = _make_tool()

    def test_plain_string_returned_as_is(self):
        assert self.tool._adf_to_text("plain text") == "plain text"

    def test_none_returns_empty_string(self):
        assert self.tool._adf_to_text(None) == ""

    def test_adf_doc_with_paragraph(self):
        adf = {
            "type": "doc",
            "version": 1,
            "content": [{
                "type": "paragraph",
                "content": [{"type": "text", "text": "Hello world"}]
            }]
        }
        assert self.tool._adf_to_text(adf) == "Hello world"

    def test_adf_bullet_list(self):
        adf = {
            "type": "doc",
            "version": 1,
            "content": [{
                "type": "bulletList",
                "content": [
                    {"type": "listItem", "content": [
                        {"type": "paragraph", "content": [{"type": "text", "text": "Item A"}]}
                    ]},
                    {"type": "listItem", "content": [
                        {"type": "paragraph", "content": [{"type": "text", "text": "Item B"}]}
                    ]},
                ]
            }]
        }
        text = self.tool._adf_to_text(adf)
        assert "Item A" in text
        assert "Item B" in text
