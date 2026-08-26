import boto3
from typing import Type, List, Dict, Any
from pydantic import BaseModel, Field
from crewai.tools import BaseTool

import json
from botocore.exceptions import ClientError


class AWSSecretReaderPodIdentitySchema(BaseModel):
    """Input schema for AWSSecretReaderPodIdentity."""
    pass


class AWSSecretReaderPodIdentity(BaseTool):
    """
    AWSSecretReaderPodIdentity - Reads an AWS Secret using Pod Identity
    and returns the full key-value dict.
    """
    name: str = "AWS Secret Reader with Pod Identity"
    description: str = "Reads a fixed AWS Secret (set in code) using Pod Identity, and returns all key-value pairs as a dict."
    args_schema: Type[BaseModel] = AWSSecretReaderPodIdentitySchema

    # Review every line tagged "SETUP-REQUIRED:" below before deploying this tool to a new environment or client.
    # SETUP-REQUIRED: must match the secret name created in your AWS Secrets Manager
    SECRET_NAME: str = "aava-secret-manager-s3-credentials"


    def _run(self) -> Dict[str, Any]:
        try:
            client = boto3.client('secretsmanager', region_name='us-east-1')
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


class S3DocumentRetrieverSchema(BaseModel):
    """Input schema for S3DocumentRetriever."""
    folder_name: str = Field(
        ...,
        description="Name of the folder (prefix) in the S3 bucket whose files should be read.",
    )


class S3DocumentRetriever(BaseTool):
    """
    S3DocumentRetriever - Reads and returns the contents of every file
    inside a given folder (prefix) of a fixed S3 bucket.
    """
    name: str = "S3 Document Retriever"
    description: str = (
        "Reads all files inside a given folder of the configured S3 bucket "
        "and returns their contents. Input is the folder name only."
    )
    args_schema: Type[BaseModel] = S3DocumentRetrieverSchema

    # SETUP-REQUIRED: set to your organization's S3 bucket name
    BUCKET_NAME: str = "aava-ggm"
    # SETUP-REQUIRED: set to the AWS region that bucket lives in
    AWS_REGION: str = "us-east-1"

    # Credentials retrieved from AWS Secrets Manager
    AWS_ACCESS_KEY_ID: str = secrets.get("aws_access_key_id")
    AWS_SECRET_ACCESS_KEY: str = secrets.get("aws_secret_access_key")

    MAX_FILE_BYTES: int = 1_000_000  # skip anything larger

    def _run(self, folder_name: str) -> str:
        try:
            s3 = boto3.client(
                "s3",
                aws_access_key_id=self.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=self.AWS_SECRET_ACCESS_KEY,
                region_name=self.AWS_REGION,
            )
        except Exception as e:
            return f"S3_CLIENT_INIT_FAILED: {e}"

        prefix = folder_name.strip("/") + "/"

        try:
            objects = self._list_all_objects(s3, prefix)
        except Exception as e:
            return f"S3_LIST_FAILED: {e}"

        if not objects:
            return f"S3_RETRIEVE_FAILED: No files found under folder '{prefix}'"

        objects.sort(key=lambda x: x["Key"])

        parts = [
            "FILE_SOURCE: S3",
            f"BUCKET: {self.BUCKET_NAME}",
            f"FOLDER: {prefix}",
            f"FILE_COUNT: {len(objects)}",
            "",
        ]

        for obj in objects:
            key = obj["Key"]
            header = (
                f"===== FILE: {key} =====\n"
                f"LAST_MODIFIED: {obj['LastModified']}\n"
                f"SIZE_BYTES: {obj['Size']}\n"
            )
            if obj["Size"] > self.MAX_FILE_BYTES:
                body = "[SKIPPED: file exceeds size limit]"
            else:
                try:
                    body = self._get_object_content(s3, key)
                except Exception as e:
                    body = f"[READ_FAILED: {e}]"
            parts.append(f"{header}\n{body}\n")

        return "\n".join(parts)

    def _list_all_objects(self, s3, prefix: str) -> List[dict]:
        paginator = s3.get_paginator("list_objects_v2")
        all_objects = []
        for page in paginator.paginate(Bucket=self.BUCKET_NAME, Prefix=prefix):
            for obj in page.get("Contents", []):
                # skip the zero-byte "folder marker" object S3 consoles create
                if obj["Key"].endswith("/") and obj["Size"] == 0:
                    continue
                all_objects.append(obj)
        return all_objects

    def _get_object_content(self, s3, key: str) -> str:
        response = s3.get_object(Bucket=self.BUCKET_NAME, Key=key)
        raw = response["Body"].read()
        try:
            return raw.decode("utf-8")
        except UnicodeDecodeError:
            return f"[BINARY OR NON-UTF8 CONTENT: {len(raw)} bytes]"
