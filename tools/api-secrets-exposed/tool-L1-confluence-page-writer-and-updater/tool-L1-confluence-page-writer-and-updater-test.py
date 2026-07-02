"""Unit tests for tool-L1-confluence-page-writer-and-updater (ConfluencePageCreator).

All Confluence REST API calls (via requests) are mocked; no real network or
credentials are required to run these tests.

Run with:
    pytest tool-L1-confluence-page-writer-and-updater-test.py -v
"""

import os
import sys
import types
import importlib.util
from unittest.mock import MagicMock, patch, call

import pytest
import requests as _requests_lib

# ── Stub crewai before the tool module is loaded ──────────────────────────

class _StubBaseTool:
    """Minimal crewai BaseTool shim."""
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
    "tool_confluence_writer",
    os.path.join(_HERE, "tool-L1-confluence-page-writer-and-updater.py"),
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)

ConfluencePageCreator = _mod.ConfluencePageCreator


# ── Helpers ───────────────────────────────────────────────────────────────

BASE_URL = "https://mycompany.atlassian.net/wiki"
SPACE_KEY = "ENG"
PAGE_TITLE = "Sprint 42 Notes"
NEW_XHTML = "<h2>Outcomes</h2><p>Auth shipped.</p>"
EXISTING_XHTML = "<h2>Goals</h2><p>Ship auth module.</p>"
EXISTING_PAGE_ID = "425985"
EXISTING_VERSION = 3


def _make_tool():
    return ConfluencePageCreator()


def _search_response_empty():
    """Search returns no results — page does not exist."""
    r = MagicMock()
    r.status_code = 200
    r.json.return_value = {"results": []}
    r.raise_for_status.return_value = None
    return r


def _search_response_found(
    page_id=EXISTING_PAGE_ID,
    version=EXISTING_VERSION,
    existing_body=EXISTING_XHTML,
    title=PAGE_TITLE,
):
    """Search returns one matching page."""
    r = MagicMock()
    r.status_code = 200
    r.json.return_value = {
        "results": [{
            "id": page_id,
            "title": title,
            "version": {"number": version},
            "body": {"storage": {"value": existing_body}},
        }]
    }
    r.raise_for_status.return_value = None
    return r


def _create_response(new_id="425986"):
    r = MagicMock()
    r.status_code = 200
    r.json.return_value = {
        "id": new_id,
        "_links": {"webui": f"/spaces/{SPACE_KEY}/pages/{new_id}/Sprint+42+Notes"},
    }
    r.raise_for_status.return_value = None
    return r


def _update_response(page_id=EXISTING_PAGE_ID, new_version=EXISTING_VERSION + 1):
    r = MagicMock()
    r.status_code = 200
    r.json.return_value = {
        "id": page_id,
        "_links": {"webui": f"/spaces/{SPACE_KEY}/pages/{page_id}/Sprint+42+Notes"},
    }
    r.raise_for_status.return_value = None
    return r


def _http_error_response(status=409, message="Conflict"):
    r = MagicMock()
    r.status_code = status
    r.text = f'{{"message": "{message}"}}'
    err = _requests_lib.exceptions.HTTPError(f"{status} {message}")
    err.response = r
    r.raise_for_status.side_effect = err
    return r


# ── Tests: tool metadata ──────────────────────────────────────────────────

class TestToolMetadata:
    def test_name(self):
        assert _make_tool().name == "Confluence Page Creator"

    def test_description_mentions_append(self):
        assert "append" in _make_tool().description.lower()


# ── Tests: page creation (title not found) ───────────────────────────────

class TestPageCreation:
    def test_creates_page_when_title_not_found(self):
        with patch.object(_mod, "requests") as mock_req:
            mock_req.get.return_value = _search_response_empty()
            mock_req.post.return_value = _create_response("99001")
            result = _make_tool()._run(PAGE_TITLE, NEW_XHTML, SPACE_KEY, BASE_URL)

        assert "Page created successfully" in result
        assert "99001" in result

    def test_create_returns_version_1(self):
        with patch.object(_mod, "requests") as mock_req:
            mock_req.get.return_value = _search_response_empty()
            mock_req.post.return_value = _create_response()
            result = _make_tool()._run(PAGE_TITLE, NEW_XHTML, SPACE_KEY, BASE_URL)

        assert "Version: 1" in result

    def test_create_posts_content_as_xhtml_storage(self):
        """The POST payload must use representation=storage."""
        with patch.object(_mod, "requests") as mock_req:
            mock_req.get.return_value = _search_response_empty()
            mock_req.post.return_value = _create_response()
            _make_tool()._run(PAGE_TITLE, NEW_XHTML, SPACE_KEY, BASE_URL)

        posted = mock_req.post.call_args[1]["json"]
        storage = posted["body"]["storage"]
        assert storage["representation"] == "storage"
        assert storage["value"] == NEW_XHTML

    def test_create_includes_space_key_and_title(self):
        with patch.object(_mod, "requests") as mock_req:
            mock_req.get.return_value = _search_response_empty()
            mock_req.post.return_value = _create_response()
            _make_tool()._run(PAGE_TITLE, NEW_XHTML, SPACE_KEY, BASE_URL)

        posted = mock_req.post.call_args[1]["json"]
        assert posted["title"] == PAGE_TITLE
        assert posted["space"]["key"] == SPACE_KEY

    def test_create_result_includes_base_url_and_space_key(self):
        with patch.object(_mod, "requests") as mock_req:
            mock_req.get.return_value = _search_response_empty()
            mock_req.post.return_value = _create_response()
            result = _make_tool()._run(PAGE_TITLE, NEW_XHTML, SPACE_KEY, BASE_URL)

        assert SPACE_KEY in result
        assert "atlassian.net" in result

    def test_create_result_includes_url(self):
        with patch.object(_mod, "requests") as mock_req:
            mock_req.get.return_value = _search_response_empty()
            mock_req.post.return_value = _create_response()
            result = _make_tool()._run(PAGE_TITLE, NEW_XHTML, SPACE_KEY, BASE_URL)

        assert "URL:" in result
        assert "http" in result


# ── Tests: page append (title found) ─────────────────────────────────────

class TestPageAppend:
    def test_appends_to_existing_page(self):
        with patch.object(_mod, "requests") as mock_req:
            mock_req.get.return_value = _search_response_found()
            mock_req.put.return_value = _update_response()
            result = _make_tool()._run(PAGE_TITLE, NEW_XHTML, SPACE_KEY, BASE_URL)

        assert "Content appended to existing page" in result

    def test_new_content_concatenated_onto_existing_body(self):
        """PUT body must contain EXISTING_XHTML + separator + NEW_XHTML."""
        with patch.object(_mod, "requests") as mock_req:
            mock_req.get.return_value = _search_response_found(
                existing_body=EXISTING_XHTML
            )
            mock_req.put.return_value = _update_response()
            _make_tool()._run(PAGE_TITLE, NEW_XHTML, SPACE_KEY, BASE_URL)

        put_payload = mock_req.put.call_args[1]["json"]
        put_body = put_payload["body"]["storage"]["value"]
        assert EXISTING_XHTML in put_body
        assert NEW_XHTML in put_body
        # Must appear in order: existing first, new second
        assert put_body.index(EXISTING_XHTML) < put_body.index(NEW_XHTML)

    def test_empty_paragraph_separator_used(self):
        """The separator between existing and new content must be <p></p>."""
        with patch.object(_mod, "requests") as mock_req:
            mock_req.get.return_value = _search_response_found(
                existing_body=EXISTING_XHTML
            )
            mock_req.put.return_value = _update_response()
            _make_tool()._run(PAGE_TITLE, NEW_XHTML, SPACE_KEY, BASE_URL)

        put_payload = mock_req.put.call_args[1]["json"]
        put_body = put_payload["body"]["storage"]["value"]
        assert "<p></p>" in put_body

    def test_version_incremented_by_one(self):
        """The PUT version.number must be exactly current_version + 1."""
        with patch.object(_mod, "requests") as mock_req:
            mock_req.get.return_value = _search_response_found(version=EXISTING_VERSION)
            mock_req.put.return_value = _update_response()
            _make_tool()._run(PAGE_TITLE, NEW_XHTML, SPACE_KEY, BASE_URL)

        put_payload = mock_req.put.call_args[1]["json"]
        assert put_payload["version"]["number"] == EXISTING_VERSION + 1

    def test_append_result_includes_new_version_number(self):
        with patch.object(_mod, "requests") as mock_req:
            mock_req.get.return_value = _search_response_found(version=EXISTING_VERSION)
            mock_req.put.return_value = _update_response()
            result = _make_tool()._run(PAGE_TITLE, NEW_XHTML, SPACE_KEY, BASE_URL)

        assert f"Version: {EXISTING_VERSION + 1}" in result

    def test_append_result_includes_page_id(self):
        with patch.object(_mod, "requests") as mock_req:
            mock_req.get.return_value = _search_response_found(page_id=EXISTING_PAGE_ID)
            mock_req.put.return_value = _update_response()
            result = _make_tool()._run(PAGE_TITLE, NEW_XHTML, SPACE_KEY, BASE_URL)

        assert EXISTING_PAGE_ID in result

    def test_no_post_called_on_append(self):
        """When the page exists, POST (create) must never be called."""
        with patch.object(_mod, "requests") as mock_req:
            mock_req.get.return_value = _search_response_found()
            mock_req.put.return_value = _update_response()
            _make_tool()._run(PAGE_TITLE, NEW_XHTML, SPACE_KEY, BASE_URL)

        mock_req.post.assert_not_called()

    def test_no_put_called_on_create(self):
        """When the page does not exist, PUT (update) must never be called."""
        with patch.object(_mod, "requests") as mock_req:
            mock_req.get.return_value = _search_response_empty()
            mock_req.post.return_value = _create_response()
            _make_tool()._run(PAGE_TITLE, NEW_XHTML, SPACE_KEY, BASE_URL)

        mock_req.put.assert_not_called()


# ── Tests: trailing slash handling ────────────────────────────────────────

class TestBaseUrlNormalisation:
    def test_trailing_slash_stripped_from_base_url(self):
        with patch.object(_mod, "requests") as mock_req:
            mock_req.get.return_value = _search_response_empty()
            mock_req.post.return_value = _create_response()
            _make_tool()._run(PAGE_TITLE, NEW_XHTML, SPACE_KEY, BASE_URL + "/")

        search_url = mock_req.get.call_args[0][0]
        assert "//" not in search_url.replace("https://", "")


# ── Tests: error handling ─────────────────────────────────────────────────

class TestErrorHandling:
    def test_search_error_returns_error_string(self):
        with patch.object(_mod, "requests") as mock_req:
            mock_req.get.return_value = _http_error_response(403, "Forbidden")
            result = _make_tool()._run(PAGE_TITLE, NEW_XHTML, SPACE_KEY, BASE_URL)

        assert "Error writing to Confluence page" in result

    def test_update_409_conflict_returns_error_with_details(self):
        """A version-conflict 409 must return error string including Details."""
        with patch.object(_mod, "requests") as mock_req:
            mock_req.get.return_value = _search_response_found()
            mock_req.put.return_value = _http_error_response(409, "Conflict")
            result = _make_tool()._run(PAGE_TITLE, NEW_XHTML, SPACE_KEY, BASE_URL)

        assert "Error writing to Confluence page" in result
        assert "Details:" in result

    def test_create_400_bad_xhtml_returns_error_with_details(self):
        with patch.object(_mod, "requests") as mock_req:
            mock_req.get.return_value = _search_response_empty()
            mock_req.post.return_value = _http_error_response(400, "Bad Request")
            result = _make_tool()._run(PAGE_TITLE, "<not valid xhtml", SPACE_KEY, BASE_URL)

        assert "Error writing to Confluence page" in result

    def test_connection_error_returns_error_string(self):
        with patch.object(_mod, "requests") as mock_req:
            mock_req.get.side_effect = _requests_lib.exceptions.ConnectionError("unreachable")
            result = _make_tool()._run(PAGE_TITLE, NEW_XHTML, SPACE_KEY, BASE_URL)

        assert "Error writing to Confluence page" in result

    def test_error_does_not_expose_api_key(self):
        """The api_key must never appear in any error return value."""
        with patch.object(_mod, "requests") as mock_req:
            mock_req.get.side_effect = _requests_lib.exceptions.HTTPError("500 Server Error")
            result = _make_tool()._run(PAGE_TITLE, NEW_XHTML, SPACE_KEY, BASE_URL)

        assert _mod.api_key not in result


# ── Tests: known nuances ──────────────────────────────────────────────────

class TestKnownNuances:
    def test_no_timeout_on_search_get(self):
        """Documents the missing timeout on the search GET.
        This test will FAIL once a timeout is added — update it accordingly."""
        with patch.object(_mod, "requests") as mock_req:
            mock_req.get.return_value = _search_response_empty()
            mock_req.post.return_value = _create_response()
            _make_tool()._run(PAGE_TITLE, NEW_XHTML, SPACE_KEY, BASE_URL)

        get_kwargs = mock_req.get.call_args[1]
        assert "timeout" not in get_kwargs, (
            "A timeout has been added to the search GET — remove this test."
        )

    def test_no_timeout_on_put(self):
        """Documents the missing timeout on the update PUT."""
        with patch.object(_mod, "requests") as mock_req:
            mock_req.get.return_value = _search_response_found()
            mock_req.put.return_value = _update_response()
            _make_tool()._run(PAGE_TITLE, NEW_XHTML, SPACE_KEY, BASE_URL)

        put_kwargs = mock_req.put.call_args[1]
        assert "timeout" not in put_kwargs, (
            "A timeout has been added to the PUT — remove this test."
        )

    def test_plain_text_content_is_sent_without_validation(self):
        """The tool does NOT validate that content is XHTML — plain text is
        submitted as-is, which will render incorrectly in Confluence."""
        plain_text = "This is just plain text, no tags"
        with patch.object(_mod, "requests") as mock_req:
            mock_req.get.return_value = _search_response_empty()
            mock_req.post.return_value = _create_response()
            _make_tool()._run(PAGE_TITLE, plain_text, SPACE_KEY, BASE_URL)

        posted = mock_req.post.call_args[1]["json"]
        # The plain text is accepted and submitted verbatim — no error raised
        assert posted["body"]["storage"]["value"] == plain_text

    def test_title_matching_is_exact_for_search(self):
        """The search params must pass the exact title string provided."""
        with patch.object(_mod, "requests") as mock_req:
            mock_req.get.return_value = _search_response_empty()
            mock_req.post.return_value = _create_response()
            _make_tool()._run("My Exact Title", NEW_XHTML, SPACE_KEY, BASE_URL)

        search_params = mock_req.get.call_args[1]["params"]
        assert search_params["title"] == "My Exact Title"
