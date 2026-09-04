"""Unit tests for tool-L1-system-current-date (CurrentDateTool).

The host clock is patched so the assertions are deterministic; crewai is stubbed
so no agent framework is required to run these tests.

Run with:
    pytest tool-L1-system-current-date-test.py -v
"""

import os
import re
import sys
import json
import types
import importlib.util
from datetime import datetime, timezone as _utc_timezone, timedelta
from unittest.mock import patch

import pytest

# ── Stub unavailable packages before the tool module is loaded ────────────

class _StubBaseTool:
    """Minimal BaseTool stub so the tool class can be defined without crewai."""
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
    "tool_system_current_date",
    os.path.join(_HERE, "tool-L1-system-current-date.py"),
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)

CurrentDateTool = _mod.CurrentDateTool


# ── Helpers ───────────────────────────────────────────────────────────────

DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")

# A fixed instant, deliberately late in the day so a timezone shift moves the
# date across midnight — that is the behaviour worth pinning down.
FIXED_UTC = datetime(2026, 9, 2, 21, 30, 0, tzinfo=_utc_timezone.utc)


def _make_tool():
    return CurrentDateTool()


def _frozen_now(tz):
    """Stand-in for datetime.now(tz) that converts the fixed instant into tz."""
    return FIXED_UTC.astimezone(tz)


def _run(tool, **kwargs):
    with patch.object(_mod, "datetime") as mock_dt:
        mock_dt.now.side_effect = _frozen_now
        return json.loads(tool.get_current_date(**kwargs))


# ── Tests ─────────────────────────────────────────────────────────────────

def test_default_timezone_is_utc():
    result = _run(_make_tool())
    assert result["success"] is True
    assert result["current_date"] == "2026-09-02"
    assert result["timezone"] == "UTC"
    assert result["warning"] is None
    assert result["error"] is None


def test_date_format_is_yyyy_mm_dd():
    result = _run(_make_tool())
    assert DATE_RE.match(result["current_date"])


def test_named_timezone_shifts_the_date_across_midnight():
    # 21:30 UTC is already the 3rd in Asia/Kolkata (+05:30).
    pytest.importorskip("zoneinfo")
    result = _run(_make_tool(), timezone="Asia/Kolkata")
    if result["warning"]:
        pytest.skip("IANA tz database not installed on this host")
    assert result["timezone"] == "Asia/Kolkata"
    assert result["current_date"] == "2026-09-03"


def test_unrecognised_timezone_falls_back_to_utc_with_a_warning():
    result = _run(_make_tool(), timezone="Middle/Earth")
    assert result["success"] is True
    assert result["current_date"] == "2026-09-02"
    assert result["timezone"] == "UTC"
    assert result["requested_timezone"] == "Middle/Earth"
    # The substitution must be visible — a silently wrong timezone is the same
    # class of defect as a guessed date.
    assert result["warning"] is not None
    assert "Middle/Earth" in result["warning"]


def test_empty_timezone_defaults_to_utc_without_a_warning():
    result = _run(_make_tool(), timezone="   ")
    assert result["timezone"] == "UTC"
    assert result["warning"] is None


def test_clock_failure_returns_structured_error_not_an_exception():
    tool = _make_tool()
    with patch.object(_mod, "datetime") as mock_dt:
        mock_dt.now.side_effect = OSError("clock unavailable")
        result = json.loads(tool.get_current_date())
    assert result["success"] is False
    assert result["current_date"] is None
    assert result["error"] == "Could not read the current date from the host clock"
    # No internal detail leaks to the caller.
    assert "clock unavailable" not in json.dumps(result)


def test_run_delegates_to_get_current_date():
    tool = _make_tool()
    with patch.object(_mod, "datetime") as mock_dt:
        mock_dt.now.side_effect = _frozen_now
        result = json.loads(tool._run("UTC"))
    assert result["current_date"] == "2026-09-02"


def test_iso_timestamp_carries_an_offset():
    result = _run(_make_tool())
    # ISO-8601 with offset, e.g. 2026-09-02T21:30:00+00:00
    assert result["iso_timestamp"].startswith("2026-09-02T")
    assert "+" in result["iso_timestamp"] or result["iso_timestamp"].endswith("Z")


def test_output_is_always_valid_json():
    tool = _make_tool()
    with patch.object(_mod, "datetime") as mock_dt:
        mock_dt.now.side_effect = _frozen_now
        raw = tool.get_current_date()
    assert isinstance(raw, str)
    json.loads(raw)  # raises if the contract is broken
