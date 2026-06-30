"""Unit tests for tool-L1-jira-upload-epics (JiraIssueCreator — advanced version).

All Jira REST API calls (via requests) are mocked; no real network or
credentials are required to run these tests.

Run with:
    pytest tool-L1-jira-upload-epics-test.py -v
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
    dry_run: bool = False

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
    "tool_jira_upload_epics",
    os.path.join(_HERE, "tool-L1-jira-upload-epics.py"),
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)

JiraIssueCreator = _mod.JiraIssueCreator
create_issues = _mod.create_issues


# ── Helpers ───────────────────────────────────────────────────────────────

def _make_tool(dry_run=False):
    t = JiraIssueCreator()
    t.dry_run = dry_run
    return t


def _mock_post_response(status=201, key="PROJ-1"):
    r = MagicMock()
    r.status_code = status
    r.ok = status < 400
    r.json.return_value = {"key": key}
    r.raise_for_status.return_value = None
    r.text = f'{{"key": "{key}"}}'
    return r


_EPIC = {
    "summary": "EP-01: Platform Foundation",
    "issueType": "Epic",
    "label": ["EP-01", "S1"],
    "parentKey": None,
    "description": "Technical foundation.",
}

_STORY = {
    "summary": "F-01.1: Agent Registration",
    "issueType": "Story",
    "label": ["F-01.1"],
    "parentKey": "EP-01",
    "description": "Register the specialist agent.",
}


# ── Tests: tool metadata ──────────────────────────────────────────────────

class TestToolMetadata:
    def test_name(self):
        assert _make_tool().name == "Jira Issue Creator"

    def test_description_mentions_jira(self):
        assert "jira" in _make_tool().description.lower()


# ── Tests: dry-run mode ───────────────────────────────────────────────────

class TestDryRunMode:
    def test_no_api_calls_in_dry_run(self):
        with patch.object(_mod, "requests") as mock_requests:
            result = create_issues(
                {"projectKey": "PROJ", "issues": [_EPIC, _STORY]},
                dry_run=True,
            )
        mock_requests.post.assert_not_called()

    def test_dry_run_output_prefixed_with_dry_run(self):
        result = create_issues(
            {"projectKey": "PROJ", "issues": [_EPIC, _STORY]},
            dry_run=True,
        )
        lines = result.strip().split("\n")
        assert all("[DRY RUN]" in l for l in lines)

    def test_dry_run_parent_resolved_from_id_map(self):
        result = create_issues(
            {"projectKey": "PROJ", "issues": [_EPIC, _STORY]},
            dry_run=True,
        )
        # Story's line should reference the fake key generated for EP-01
        lines = result.strip().split("\n")
        story_line = next(l for l in lines if "F-01.1" in l)
        assert "PROJ-1" in story_line  # parent=PROJ-1 (EP-01's fake key)

    def test_dry_run_returns_two_lines_for_two_issues(self):
        result = create_issues(
            {"projectKey": "PROJ", "issues": [_EPIC, _STORY]},
            dry_run=True,
        )
        assert len(result.strip().split("\n")) == 2


# ── Tests: live creation with parent resolution ───────────────────────────

class TestLiveCreation:
    def test_epic_and_story_created_in_order(self):
        with patch.object(_mod, "requests") as mock_requests:
            mock_requests.post.side_effect = [
                _mock_post_response(key="PROJ-10"),  # epic
                _mock_post_response(key="PROJ-11"),  # story
            ]
            result = _make_tool()._run({
                "projectKey": "PROJ",
                "issues": [_EPIC, _STORY],
            })

        assert "PROJ-10" in result
        assert "PROJ-11" in result

    def test_story_receives_real_parent_key(self):
        """After EP-01 → PROJ-10, the Story's POST must include parent=PROJ-10."""
        posted_payloads = []

        def capture_post(url, json=None, **kwargs):
            posted_payloads.append(json)
            key = f"PROJ-{10 + len(posted_payloads)}"
            return _mock_post_response(key=key)

        with patch.object(_mod, "requests") as mock_requests:
            mock_requests.post.side_effect = capture_post
            _make_tool()._run({"projectKey": "PROJ", "issues": [_EPIC, _STORY]})

        story_fields = posted_payloads[1]["fields"]
        assert story_fields.get("parent") == {"key": "PROJ-11"}

    def test_create_issues_convenience_wrapper(self):
        with patch.object(_mod, "requests") as mock_requests:
            mock_requests.post.return_value = _mock_post_response(key="PROJ-99")
            result = create_issues({"projectKey": "PROJ", "issues": [_EPIC]})

        assert "PROJ-99" in result


# ── Tests: validation ─────────────────────────────────────────────────────

class TestValidation:
    def test_missing_project_key_returns_fatal_error(self):
        result = _make_tool()._run({"issues": [_EPIC]})
        assert "Fatal error" in result
        assert "projectKey" in result

    def test_empty_issues_list_returns_fatal_error(self):
        result = _make_tool()._run({"projectKey": "PROJ", "issues": []})
        assert "Fatal error" in result

    def test_non_list_issues_returns_fatal_error(self):
        result = _make_tool()._run({"projectKey": "PROJ", "issues": "not-a-list"})
        assert "Fatal error" in result


# ── Tests: ISSUE_TYPE_MAP ─────────────────────────────────────────────────

class TestIssueTypeMap:
    def test_issue_type_map_remaps_before_post(self):
        original_map = dict(_mod.ISSUE_TYPE_MAP)
        try:
            _mod.ISSUE_TYPE_MAP["Epic"] = "Task"

            with patch.object(_mod, "requests") as mock_requests:
                mock_requests.post.return_value = _mock_post_response(key="PROJ-1")
                _make_tool()._run({"projectKey": "PROJ", "issues": [_EPIC]})

            posted = mock_requests.post.call_args[1]["json"]
            assert posted["fields"]["issuetype"]["name"] == "Task"
        finally:
            _mod.ISSUE_TYPE_MAP.clear()
            _mod.ISSUE_TYPE_MAP.update(original_map)


# ── Tests: error handling ─────────────────────────────────────────────────

class TestErrorHandling:
    def test_api_error_appended_as_failed_line(self):
        with patch.object(_mod, "requests") as mock_requests:
            mock_requests.post.return_value = _mock_post_response(status=400)
            result = _make_tool()._run({"projectKey": "PROJ", "issues": [_EPIC]})

        assert "Failed" in result

    def test_second_issue_continues_after_first_fails(self):
        with patch.object(_mod, "requests") as mock_requests:
            mock_requests.post.side_effect = [
                _mock_post_response(status=400),
                _mock_post_response(key="PROJ-2"),
            ]
            result = _make_tool()._run({
                "projectKey": "PROJ",
                "issues": [_EPIC, _STORY],
            })

        lines = result.strip().split("\n")
        assert any("Failed" in l for l in lines)
        assert any("PROJ-2" in l for l in lines)

    def test_request_exception_per_issue_does_not_abort_batch(self):
        import requests as req_lib

        with patch.object(_mod, "requests") as mock_requests:
            mock_requests.post.side_effect = [
                req_lib.RequestException("connection reset"),
                _mock_post_response(key="PROJ-5"),
            ]
            result = _make_tool()._run({
                "projectKey": "PROJ",
                "issues": [_EPIC, _STORY],
            })

        assert "PROJ-5" in result


# ── Tests: ADF description conversion ────────────────────────────────────

class TestADFConversion:
    def setup_method(self):
        self.tool = _make_tool()

    def test_string_description_passes_through(self):
        result = self.tool._normalize_description("Simple text")
        assert result == "Simple text"

    def test_dict_description_formats_keys_as_headings(self):
        desc = {"goal": "Improve speed", "steps": ["Step A", "Step B"]}
        result = self.tool._normalize_description(desc)
        assert "Goal" in result
        assert "Step A" in result
        assert "Step B" in result

    def test_adf_doc_has_at_least_one_block(self):
        """An empty description must still produce a valid ADF doc with one block."""
        adf = self.tool._convert_description("", {}, "https://jira.example.com")
        assert adf["type"] == "doc"
        assert len(adf["content"]) >= 1

    def test_sanitize_removes_empty_text_nodes(self):
        """_sanitize_adf must strip out text nodes with empty string."""
        node = {
            "type": "paragraph",
            "content": [
                {"type": "text", "text": ""},
                {"type": "text", "text": "valid"},
            ]
        }
        result = self.tool._sanitize_adf(node)
        texts = [c.get("text") for c in result["content"]]
        assert "" not in texts
        assert "valid" in texts

    def test_bold_markdown_becomes_strong_mark(self):
        content = self.tool._parse_inline("**bold text**", {}, "https://jira.example.com")
        strong_nodes = [c for c in content if any(m.get("type") == "strong" for m in c.get("marks", []))]
        assert len(strong_nodes) == 1
        assert strong_nodes[0]["text"] == "bold text"

    def test_logical_id_in_id_map_becomes_hyperlink(self):
        id_map = {"EP-01": "PROJ-10"}
        content = self.tool._parse_inline("See EP-01 for details", id_map, "https://jira.example.com")
        link_nodes = [
            c for c in content
            if any(m.get("type") == "link" for m in c.get("marks", []))
        ]
        assert len(link_nodes) == 1
        assert link_nodes[0]["text"] == "PROJ-10"
