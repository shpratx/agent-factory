import boto3
from datetime import datetime, timezone
from typing import Type, Dict, Any
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


class S3UploadSchema(BaseModel):
    """Input schema for S3UploadTool."""
    folder_name: str = Field(
        ...,
        description="Name of the folder (prefix) in the S3 bucket to upload into, e.g. 'incoming'.",
    )
    file_name: str = Field(
        ..., description="Name of the file to create, e.g. 'report.txt'."
    )
    contents: str = Field(
        ..., description="Text content to write into the file."
    )


class S3UploadTool(BaseTool):
    """
    S3UploadTool - Uploads text content to a fixed S3 bucket under a
    caller-specified folder, with a UTC timestamp prefixed to the filename.
    """
    name: str = "S3 Upload Tool"
    description: str = (
        "Uploads text content to the configured S3 bucket. Inputs are the "
        "folder name, the file name, and the contents to write."
    )
    args_schema: Type[BaseModel] = S3UploadSchema

    # SETUP-REQUIRED: set to your organization's S3 bucket name (must match S3DocumentRetriever)
    BUCKET_NAME: str = "aava-ggm"
    # SETUP-REQUIRED: set to the AWS region that bucket lives in (must match S3DocumentRetriever)
    AWS_REGION: str = "us-east-1"

    # Credentials retrieved from AWS Secrets Manager
    AWS_ACCESS_KEY_ID: str = secrets.get("aws_access_key_id")
    AWS_SECRET_ACCESS_KEY: str = secrets.get("aws_secret_access_key")

    def _run(self, folder_name: str, file_name: str, contents: str) -> dict:
        try:
            s3 = boto3.client(
                "s3",
                aws_access_key_id=self.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=self.AWS_SECRET_ACCESS_KEY,
                region_name=self.AWS_REGION,
            )
        except Exception as e:
            return {"status": "FAILED", "reason": f"S3_CLIENT_INIT_FAILED: {e}"}

        prefix = folder_name.strip("/") + "/"
        safe_name = file_name.strip("/").split("/")[-1]
        if not safe_name:
            return {"status": "FAILED", "reason": "INVALID_FILE_NAME"}

        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        object_key = f"{prefix}{timestamp}_{safe_name}"

        try:
            s3.put_object(
                Bucket=self.BUCKET_NAME,
                Key=object_key,
                Body=contents.encode("utf-8"),
                ContentType="text/plain; charset=utf-8",
            )
        except Exception as e:
            return {"status": "FAILED", "reason": f"S3_UPLOAD_FAILED: {e}"}

        return {
            "status": "SUCCESS",
            "bucket": self.BUCKET_NAME,
            "key": object_key,
            "folder": prefix,
            "size_bytes": len(contents.encode("utf-8")),
            "uploaded_at": timestamp,
        }
