# Hardcoded credentials:
api_key = "REDACTED-SECRET-KEY"
user_email = "varun.raaghav@ascendion.com"



import os
import requests
from typing import Type
from pydantic import BaseModel, Field
from crewai.tools import BaseTool


class ConfluencePageReaderSchema(BaseModel):
    """Input schema for ConfluencePageReader."""
    page_id: str = Field(..., description="The numeric ID of the Confluence page, e.g. '425985'.")
    base_url: str = Field(..., description="The base URL of the Confluence instance, e.g. 'https://your-domain.atlassian.net/wiki'.")


class ConfluencePageReader(BaseTool):
    """Reads the contents of a Confluence page via the REST API."""
    name: str = "Confluence Page Reader"
    description: str = "Reads and retrieves the contents of a specified Confluence page."
    args_schema: Type[BaseModel] = ConfluencePageReaderSchema

    def _run(self, page_id: str, base_url: str) -> str:
        # Guard against swapped arguments
        if base_url.isdigit() or page_id.startswith("http"):
            page_id, base_url = base_url, page_id


        url = f"{base_url.rstrip('/')}/rest/api/content/{page_id}?expand=body.storage"
        headers = {"Accept": "application/json"}
        auth = (user_email, api_key)

        try:
            response = requests.get(url, headers=headers, auth=auth)
            response.raise_for_status()
            data = response.json()
            content = data.get("body", {}).get("storage", {}).get("value", "")
            title = data.get("title", "")
            return f"Title: {title}\nContent: {content}"
        except requests.RequestException as e:
            return f"Error reading Confluence page: {str(e)}"