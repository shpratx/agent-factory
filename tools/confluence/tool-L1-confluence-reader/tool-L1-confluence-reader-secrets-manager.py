import os
import requests
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

    # Review every line tagged "SETUP-REQUIRED:" below before deploying this tool to a new environment or client.
    # SETUP-REQUIRED: must match the secret name created in your AWS Secrets Manager
    SECRET_NAME: str = "aava-secret-manager-confluence-credentials"

    # SETUP-REQUIRED: AWS region where that secret lives (us-east-1 or us-east-2 depending on deployment)
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
