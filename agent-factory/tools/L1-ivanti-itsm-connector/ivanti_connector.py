import os
import re
import json
import logging
from typing import Any, Type
from pydantic import BaseModel, Field, validator
from crewai.tools import BaseTool

import requests

logger = logging.getLogger("ivanti_connector")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)


class IvantiITSMConnectorSchema(BaseModel):
    """Input schema for IvantiITSMConnector with validation."""
    incident_title: str = Field(..., description="Title of the incident to be created in Ivanti ITSM")
    incident_description: str = Field(..., description="Detailed description of the incident")
    priority: str = Field(..., description="Priority level of the incident (Low|Medium|High)")
    category: str = Field(..., description="Category of the incident (Network|Software|Hardware|Other)")

    @validator("incident_title")
    def title_safe(cls, v: str) -> str:
        v = v.strip()
        if not (3 <= len(v) <= 200):
            raise ValueError("incident_title must be 3-200 characters")
        # basic sanitization: remove control chars
        v = re.sub(r"[\x00-\x1f\x7f]", "", v)
        return v

    @validator("incident_description")
    def desc_safe(cls, v: str) -> str:
        v = v.strip()
        if not (5 <= len(v) <= 5000):
            raise ValueError("incident_description must be 5-5000 characters")
        v = re.sub(r"[\x00-\x1f\x7f]", "", v)
        return v

    @validator("priority")
    def priority_allowed(cls, v: str) -> str:
        allowed = {"low", "medium", "high"}
        if v.lower() not in allowed:
            raise ValueError(f"priority must be one of {allowed}")
        return v.title()

    @validator("category")
    def category_allowed(cls, v: str) -> str:
        allowed = {"network", "software", "hardware", "other"}
        if v.lower() not in allowed:
            raise ValueError(f"category must be one of {allowed}")
        return v.title()


class IvantiITSMConnector(BaseTool):
    """
    IvantiITSMConnector - Secure tool to integrate Aava with Ivanti ITSM for creating incidents.
    Environment variables required:
      - IVANTI_ENDPOINT: full HTTPS endpoint URL
      - IVANTI_API_KEY: API key for Ivanti (read-only via secure store)
    """

    name: str = "Ivanti ITSM Connector"
    description: str = "A secure tool to integrate Aava with Ivanti ITSM for creating incidents."  # brief
    args_schema: Type[BaseModel] = IvantiITSMConnectorSchema

    def __init__(self, post_url: str | None = None, verify_ssl: bool = True, timeout: int = 10):
        self.post_url = post_url or os.environ.get("IVANTI_ENDPOINT")
        self.verify_ssl = verify_ssl
        self.timeout = timeout
        if not self.post_url:
            raise ValueError("IVANTI_ENDPOINT must be configured in environment or passed to constructor")

    def _run(self, incident_title: str, incident_description: str, priority: str, category: str) -> str:
        # validate input via schema
        try:
            payload_obj = IvantiITSMConnectorSchema(
                incident_title=incident_title,
                incident_description=incident_description,
                priority=priority,
                category=category,
            )
        except Exception as e:
            logger.warning("Invalid input for IvantiITSMConnector: %s", str(e))
            return "Invalid input: please check title, description, priority, and category."

        # build request payload safely
        payload = {
            "records": [
                {
                    "Incident_Title": payload_obj.incident_title,
                    "Incident_Description": payload_obj.incident_description,
                    "Priority": payload_obj.priority,
                    "Category": payload_obj.category,
                }
            ]
        }

        # retrieve secret from environment or secret manager wrapper
        api_key = os.environ.get("IVANTI_API_KEY")
        if not api_key:
            # fallback to AVASecret if present but encourage env var
            try:
                import AVASecret as _ava

                api_key = _ava.getValue("IVANTI_KEY")
            except Exception:
                api_key = None

        if not api_key:
            logger.error("Ivanti API key not configured")
            return "Configuration error: integration not configured."  # generic message

        headers = {
            "Content-Type": "application/json",
            "access-key": api_key,
        }

        # perform request with safe defaults
        try:
            # ensure HTTPS
            if not self.post_url.lower().startswith("https://"):
                logger.error("Insecure endpoint configured: %s", self.post_url)
                return "Configuration error: endpoint must use HTTPS."

            resp = requests.post(
                self.post_url,
                json=payload,
                headers=headers,
                timeout=self.timeout,
                verify=self.verify_ssl,
            )
            # raise for HTTP errors
            resp.raise_for_status()

            # parse response safely
            try:
                data = resp.json()
            except ValueError:
                data = {"status": "ok", "detail": "non-json response"}

            logger.info("Ivanti incident created (masked): status=%s", resp.status_code)
            # do not return raw response to avoid leaking secrets
            return "Incident successfully created in Ivanti ITSM."

        except requests.RequestException as e:
            # log details internally, but return a generic message
            logger.exception("Error creating incident in Ivanti ITSM: %s", str(e))
            return "Error creating incident in Ivanti ITSM. Please retry or contact support."


# Simple CLI runner for manual testing
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 5:
        print("Usage: ivanti_connector.py <title> <desc> <priority> <category>")
        sys.exit(1)

    tool = IvantiITSMConnector()
    out = tool._run(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
    print(out)
