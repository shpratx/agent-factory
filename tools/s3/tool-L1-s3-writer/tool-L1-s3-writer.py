import boto3
from datetime import datetime, timezone
from typing import Type
from pydantic import BaseModel, Field
from crewai.tools import BaseTool


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

    # --- hardcoded config (must match S3DocumentRetriever) ---
    BUCKET_NAME: str = "aava-ggm"
    AWS_REGION: str = "us-east-1"
    AWS_ACCESS_KEY_ID: str = "AKIA4NGJMIPJIZOAF3P7"
    AWS_SECRET_ACCESS_KEY: str = "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"

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