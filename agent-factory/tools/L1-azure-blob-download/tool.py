"""L1-azure-blob-download: Downloads a document from Azure Blob Storage."""
import base64
import logging
from dataclasses import dataclass
from typing import Optional

from azure.storage.blob import BlobServiceClient

logger = logging.getLogger("L1-azure-blob-download")


@dataclass
class ToolResult:
    success: bool
    data: Optional[dict] = None
    error: Optional[str] = None


class Tool:
    name = "L1-azure-blob-download"
    timeout = 60

    def __init__(self, secrets: dict):
        self.connection_string = secrets["connection_string"]

    def execute(self, container_name: str, folder_path: str, file_name: str) -> ToolResult:
        # 1. Validate input
        if not container_name or not folder_path or not file_name:
            return ToolResult(success=False, error="container_name, folder_path, and file_name are required")

        # Block path traversal
        if ".." in folder_path or ".." in file_name:
            return ToolResult(success=False, error="Invalid path: directory traversal not allowed")

        folder_path = folder_path.strip("/")
        blob_path = f"{folder_path}/{file_name}"

        # 2. Download from Azure Blob Storage
        try:
            blob_service = BlobServiceClient.from_connection_string(self.connection_string)
            blob_client = blob_service.get_blob_client(container=container_name, blob=blob_path)

            if not blob_client.exists():
                return ToolResult(success=False, error=f"Blob not found: {blob_path}")

            download = blob_client.download_blob()
            file_bytes = download.readall()
            properties = blob_client.get_blob_properties()

            logger.info("download_success", extra={"container": container_name, "path": blob_path, "size": len(file_bytes)})

            return ToolResult(success=True, data={
                "file_content": base64.b64encode(file_bytes).decode("utf-8"),
                "content_type": properties.content_settings.content_type or "application/octet-stream",
                "size_bytes": len(file_bytes),
                "last_modified": properties.last_modified.isoformat() if properties.last_modified else None,
            })

        except Exception as e:
            logger.error("download_failed", extra={"error": str(e)})
            return ToolResult(success=False, error=f"Download failed: {type(e).__name__}")
