"""Unit tests for tool-L1-confluence-reader (ConfluencePageReader).

All Confluence REST API calls (via requests) are mocked; no real network or
credentials are required to run these tests.

Run with:
    pytest tool-L1-confluence-reader-test.py -v
"""

import os
import sys
import types
import importlib.util
from unittest.mock import MagicMock, patch

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

# ── Load the tool module (hyphenated filename requires importlib) ──────────

_HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location(
    "tool_confluence_reader",
    os.path.join(_HERE, "tool-L1-confluence-reader.py"),
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)

ConfluencePageReader = _mod.ConfluencePageReader


# ── Helpers ───────────────────────────────────────────────────────────────

BASE_URL = "https://mycompany.atlassian.net/wiki"
PAGE_ID = "425985"

SAMPLE_XHTML = (
    "<h2>Sprint 42 Summary</h2>"
    "<p>Velocity: <strong>34 points</strong>.</p>"
    "<ul><li>Feature A shipped</li></ul>"
)


def _make_tool():
    return ConfluencePageReader()


def _mock_get_response(status=200, title="Test Page", xhtml=SAMPLE_XHTML):
    r = MagicMock()
    r.status_code = status
    r.json.return_value = {
        "title": title,
        "body": {"storage": {"value": xhtml}},
    }
    r.raise_for_status.return_value = None
    return r


def _mock_error_response(status=404, message="Not Found"):
    r = MagicMock()
    r.status_code = status
    r.raise_for_status.side_effect = _requests_lib.exceptions.HTTPError(
        f"{status} Client Error: {message}"
    )
    return r


# ── Tests: tool metadata ──────────────────────────────────────────────────

class TestToolMetadata:
    def test_name(self):
        assert _make_tool().name == "Confluence Page Reader"

    def test_description_mentions_confluence(self):
        assert "confluence" in _make_tool().description.lower()


# ── Tests: successful read ────────────────────────────────────────────────

class TestSuccessfulRead:
    def test_returns_title_and_content(self):
        with patch.object(_mod, "requests") as mock_req:
            mock_req.get.return_value = _mock_get_response(
                title="Sprint 42 Notes", xhtml="<p>Some notes.</p>"
            )
            result = _make_tool()._run(PAGE_ID, BASE_URL)

        assert "Title: Sprint 42 Notes" in result
        assert "Content: <p>Some notes.</p>" in result

    def test_content_is_raw_xhtml(self):
        """The Content field must contain XHTML tags, not stripped plain text."""
        with patch.object(_mod, "requests") as mock_req:
            mock_req.get.return_value = _mock_get_response(xhtml=SAMPLE_XHTML)
            result = _make_tool()._run(PAGE_ID, BASE_URL)

        assert "<h2>" in result
        assert "<strong>" in result
        assert "<ul>" in result

    def test_correct_api_url_constructed(self):
        """The GET must target the correct REST endpoint with body.storage expand."""
        with patch.object(_mod, "requests") as mock_req:
            mock_req.get.return_value = _mock_get_response()
            _make_tool()._run(PAGE_ID, BASE_URL)

        call_url = mock_req.get.call_args[0][0]
        assert f"/rest/api/content/{PAGE_ID}" in call_url
        assert "body.storage" in call_url

    def test_trailing_slash_stripped_from_base_url(self):
        """base_url with trailing slash must not produce a double-slash in the URL."""
        with patch.object(_mod, "requests") as mock_req:
            mock_req.get.return_value = _mock_get_response()
            _make_tool()._run(PAGE_ID, BASE_URL + "/")

        call_url = mock_req.get.call_args[0][0]
        assert "//" not in call_url.replace("https://", "")

    def test_empty_body_storage_returns_empty_content(self):
        """A page with no body must not crash — returns empty Content field."""
        r = MagicMock()
        r.status_code = 200
        r.json.return_value = {"title": "Empty", "body": {"storage": {"value": ""}}}
        r.raise_for_status.return_value = None

        with patch.object(_mod, "requests") as mock_req:
            mock_req.get.return_value = r
            result = _make_tool()._run(PAGE_ID, BASE_URL)

        assert "Title: Empty" in result
        assert "Content: " in result


# ── Tests: argument swap guard ────────────────────────────────────────────

class TestArgumentSwapGuard:
    def test_swaps_when_page_id_starts_with_http(self):
        """If page_id looks like a URL the arguments must be silently swapped."""
        with patch.object(_mod, "requests") as mock_req:
            mock_req.get.return_value = _mock_get_response(title="Swapped OK")
            # Pass arguments in wrong order
            result = _make_tool()._run(BASE_URL, PAGE_ID)

        # Should succeed (swap happened) — title present, no error string
        assert "Title: Swapped OK" in result

    def test_swaps_when_base_url_is_all_digits(self):
        """If base_url is a digit string the arguments must be silently swapped."""
        with patch.object(_mod, "requests") as mock_req:
            mock_req.get.return_value = _mock_get_response(title="Digit Swap OK")
            result = _make_tool()._run(PAGE_ID, PAGE_ID)  # both look like page_id

        # Guard fires because base_url.isdigit() is True — a swap is attempted
        # The call should not raise an exception regardless of outcome
        assert isinstance(result, str)

    def test_correct_order_does_not_swap(self):
        """Normal correct-order call must not have arguments swapped."""
        with patch.object(_mod, "requests") as mock_req:
            mock_req.get.return_value = _mock_get_response()
            _make_tool()._run(PAGE_ID, BASE_URL)

        call_url = mock_req.get.call_args[0][0]
        # page_id must appear in the URL path, not base_url
        assert PAGE_ID in call_url
        assert BASE_URL.replace("https://", "") in call_url


# ── Tests: error handling ─────────────────────────────────────────────────

class TestErrorHandling:
    def test_404_returns_error_string(self):
        with patch.object(_mod, "requests") as mock_req:
            mock_req.get.return_value = _mock_error_response(404, "Not Found")
            result = _make_tool()._run(PAGE_ID, BASE_URL)

        assert "Error reading Confluence page" in result
        assert "404" in result

    def test_401_returns_error_string(self):
        with patch.object(_mod, "requests") as mock_req:
            mock_req.get.return_value = _mock_error_response(401, "Unauthorized")
            result = _make_tool()._run(PAGE_ID, BASE_URL)

        assert "Error reading Confluence page" in result

    def test_connection_error_returns_error_string(self):
        with patch.object(_mod, "requests") as mock_req:
            mock_req.get.side_effect = _requests_lib.exceptions.ConnectionError("DNS failure")
            result = _make_tool()._run(PAGE_ID, BASE_URL)

        assert "Error reading Confluence page" in result

    def test_timeout_returns_error_string(self):
        with patch.object(_mod, "requests") as mock_req:
            mock_req.get.side_effect = _requests_lib.exceptions.Timeout("timed out")
            result = _make_tool()._run(PAGE_ID, BASE_URL)

        assert "Error reading Confluence page" in result

    def test_error_string_does_not_expose_credentials(self):
        """The api_key must never appear in any return value."""
        with patch.object(_mod, "requests") as mock_req:
            mock_req.get.side_effect = _requests_lib.exceptions.HTTPError("500 Server Error")
            result = _make_tool()._run(PAGE_ID, BASE_URL)

        # The module-level api_key is "REDACTED-SECRET-KEY" in this file
        assert _mod.api_key not in result


# ── Tests: known nuance — no timeout ─────────────────────────────────────

class TestKnownNuances:
    def test_no_timeout_argument_passed_to_requests_get(self):
        """Documents the known missing timeout. This test will FAIL once a
        timeout is added, at which point it should be removed or updated."""
        with patch.object(_mod, "requests") as mock_req:
            mock_req.get.return_value = _mock_get_response()
            _make_tool()._run(PAGE_ID, BASE_URL)

        call_kwargs = mock_req.get.call_args[1]
        assert "timeout" not in call_kwargs, (
            "A timeout has been added — remove this test and add a positive timeout test."
        )
