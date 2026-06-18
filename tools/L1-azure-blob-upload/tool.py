"""L1-azure-blob-upload: Creates folder in Azure Blob Storage and uploads a file."""
import base64
import logging
from dataclasses import dataclass
from typing import Optional

from azure.storage.blob import BlobServiceClient, ContentSettings

logger = logging.getLogger("L1-azure-blob-upload")


@dataclass
class ToolResult:
    success: bool
    data: Optional[dict] = None
    error: Optional[str] = None


class Tool:
    name = "L1-azure-blob-upload"
    timeout = 60

    def __init__(self, secrets: dict):
        self.connection_string = secrets["connection_string"]

    def execute(self, container_name: str, folder_path: str, file_name: str,
                file_content: str, content_type: str = "application/octet-stream") -> ToolResult:
        # 1. Validate input
        if not container_name or not folder_path or not file_name or not file_content:
            return ToolResult(success=False, error="container_name, folder_path, file_name, and file_content are required")

        # Sanitise folder_path (strip leading/trailing slashes)
        folder_path = folder_path.strip("/")
        blob_path = f"{folder_path}/{file_name}"

        # 2. Decode file content
        try:
            file_bytes = base64.b64decode(file_content)
        except Exception:
            return ToolResult(success=False, error="file_content is not valid base64")

        # 3. Upload to Azure Blob Storage
        try:
            blob_service = BlobServiceClient.from_connection_string(self.connection_string)
            container_client = blob_service.get_container_client(container_name)

            # Create container if it doesn't exist
            if not container_client.exists():
                container_client.create_container()

            # Upload blob (folder is implicit in the blob name)
            blob_client = container_client.get_blob_client(blob_path)
            blob_client.upload_blob(
                file_bytes,
                overwrite=True,
                content_settings=ContentSettings(content_type=content_type),
            )

            logger.info("upload_success", extra={"container": container_name, "path": blob_path, "size": len(file_bytes)})

            return ToolResult(success=True, data={
                "blob_url": blob_client.url,
                "folder_path": folder_path,
                "file_name": file_name,
                "size_bytes": len(file_bytes),
            })

        except Exception as e:
            logger.error("upload_failed", extra={"error": str(e)})
            return ToolResult(success=False, error=f"Upload failed: {type(e).__name__}")
