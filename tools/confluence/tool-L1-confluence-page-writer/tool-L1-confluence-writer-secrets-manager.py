import requests
import urllib3
from typing import Type
from pydantic import BaseModel, Field
from crewai.tools import BaseTool


import json
import boto3
from botocore.exceptions import ClientError
from typing import Dict, Any


class AWSSecretReaderPodIdentitySchema(BaseModel):
    """Input schema for AWSSecretReaderPodIdentity. """
    pass


class AWSSecretReaderPodIdentity(BaseTool):
    """
    AWSSecretReaderPodIdentity - Reads a AWS Secret using Pod Identity
    and returns the full key-value dict.
    """
    name: str = "AWS Secret Reader with Pod Identity"
    description: str = "Reads a fixed AWS Secret (set in code) using Pod Identity, and returns all key-value pairs as a dict."
    args_schema: Type[BaseModel] = AWSSecretReaderPodIdentitySchema

    
    SECRET_NAME: str = "aava-secret-manager-confluence-credentials"

    # region = us-east-1 or us-east-2 depending on deployment of AWS Secrets Manager
    region_name = "us-east-1"
    

    def _run(self) -> Dict[str, Any]:
        try:

            client = boto3.client('secretsmanager', region_name=self.region_name)
            get_secret_value_response = client.get_secret_value(SecretId=self.SECRET_NAME)
            secret_string = get_secret_value_response.get('SecretString', '{}')
            secret_dict = json.loads(secret_string)

            if not isinstance(secret_dict, dict):
                raise ValueError(f"Secret value is not a JSON object: {secret_dict}")

            return secret_dict

        except ClientError as e:
            raise RuntimeError(f"Error retrieving secret: {str(e)}")
        except Exception as ex:
            raise RuntimeError(f"Unexpected error: {str(ex)}")


reader = AWSSecretReaderPodIdentity()
secrets = reader._run()

# Secrets retrieved from AWS Secrets Manager 
api_key = secrets.get("api_key")
user_email = secrets.get("user_email")

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class ConfluencePageCreatorSchema(BaseModel):
    """Input schema for ConfluencePageCreator."""
    title: str = Field(..., description="The title of the Confluence page. If it exists, content is appended; otherwise a new page is created.")
    content: str = Field(..., description="The body content to add, in Confluence storage format (XHTML). Basic tags like <p>, <h1>, <ul>, <table> are accepted.")
    space_key: str = Field(..., description="The key of the space, e.g. '~7120208dde8969e5854fbfbe0185df21567c33'.")
    base_url: str = Field(..., description="The base URL of the Confluence instance, e.g. 'https://your-domain.atlassian.net/wiki'.")


class ConfluencePageCreator(BaseTool):
    """Creates a Confluence page, or appends to it if the title already exists."""
    name: str = "Confluence Page Creator"
    description: str = "Creates a new Confluence page, or appends content to the bottom of an existing page with the same title."
    args_schema: Type[BaseModel] = ConfluencePageCreatorSchema

    def _run(self, title: str, content: str, space_key: str, base_url: str) -> str:
        base = base_url.rstrip("/")
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
        auth = (user_email, api_key)

        try:
            # 1. Look for an existing page with this title in the space
            search = requests.get(
                f"{base}/rest/api/content",
                headers=headers,
                auth=auth,
                params={
                    "spaceKey": space_key,
                    "title": title,
                    "expand": "body.storage,version",
                },
                verify=False
            )
            search.raise_for_status()
            results = search.json().get("results", [])

            if results:
                # 2a. Page exists -> append content and update
                page = results[0]
                page_id = page["id"]
                existing_body = page.get("body", {}).get("storage", {}).get("value", "")
                current_version = page.get("version", {}).get("number", 1)

                new_body = existing_body + "<p></p>" + content

                update_payload = {
                    "type": "page",
                    "title": title,
                    "space": {"key": space_key},
                    "version": {"number": current_version + 1},
                    "body": {
                        "storage": {
                            "value": new_body,
                            "representation": "storage",
                        }
                    },
                }

                update = requests.put(
                    f"{base}/rest/api/content/{page_id}",
                    headers=headers,
                    auth=auth,
                    json=update_payload,
                    verify=False
                )
                update.raise_for_status()
                data = update.json()
                webui = data.get("_links", {}).get("webui", "")
                full_link = f"{base}{webui}" if webui else "(link unavailable)"
                return (
                    f"Content appended to existing page.\n"
                    f"confluence_page_id: {page_id} \nbase_url: {base_url}\nspace_key: {space_key}\n"
                    f"\nPage Title: {title}\nVersion: {current_version + 1}\nURL: {full_link}"
                )

            else:
                # 2b. Page doesn't exist -> create it
                create_payload = {
                    "type": "page",
                    "title": title,
                    "space": {"key": space_key},
                    "body": {
                        "storage": {
                            "value": content,
                            "representation": "storage",
                        }
                    },
                }
                create = requests.post(
                    f"{base}/rest/api/content",
                    headers=headers,
                    auth=auth,
                    json=create_payload,
                    verify=False
                )
                create.raise_for_status()
                data = create.json()
                new_id = data.get("id", "")
                webui = data.get("_links", {}).get("webui", "")
                full_link = f"{base}{webui}" if webui else "(link unavailable)"
                return (
                    f"Page created successfully.\n"
                    f"confluence_page_id: {new_id} \nbase_url: {base_url}\nspace_key: {space_key}\n"
                    f"\nPage Title: {title}\nVersion: 1 \nURL: {full_link}"
                )

        except requests.RequestException as e:
            body = getattr(e.response, "text", "") if getattr(e, "response", None) else ""
            return f"Error writing to Confluence page: {str(e)}\nDetails: {body}"



'''
Notes:
The append is a full-page rewrite. Confluence has no "append" endpoint, so the tool reads the existing storage-format body, concatenates your new content onto the end, and PUTs the whole thing back. That's why it fetches body.storage and version in the search call — both are needed to do the update.

Version bumping is mandatory. Confluence uses optimistic locking: an update must specify version.number as exactly current + 1, or it rejects the request with a 409 Conflict. The code reads the current version and increments it.

Concurrency caveat. Because it's read-modify-write, if two runs update the same page at nearly the same moment, one can fail with a version conflict (or overwrite the other). For a single agent running sequentially this won't happen, but worth knowing if you ever parallelize.

Search matches exact title within the space. The title param does an exact match, so "KB Notes" won't match "kb notes". If the title has special characters, requests handles the URL encoding for you since it's passed via params.
'''
