import os
import sys
import json
import pytest
from pathlib import Path

# ensure package path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ivanti_connector import IvantiITSMConnector, IvantiITSMConnectorSchema


def test_validation_pass():
    obj = IvantiITSMConnectorSchema(
        incident_title="Test",
        incident_description="Details about the issue.",
        priority="High",
        category="Software",
    )
    assert obj.priority == "High"


def test_validation_fail():
    with pytest.raises(Exception):
        IvantiITSMConnectorSchema(
            incident_title="x",
            incident_description="d",
            priority="urgent",
            category="unknown",
        )


def test_missing_api_key(monkeypatch):
    monkeypatch.delenv("IVANTI_API_KEY", raising=False)
    # ensure AVASecret not present
    try:
        import AVASecret  # type: ignore

        del sys.modules["AVASecret"]
    except Exception:
        pass

    tool = IvantiITSMConnector(post_url="https://example.invalid/api")
    out = tool._run("Title", "Desc here", "Low", "Other")
    assert "Configuration error" in out
