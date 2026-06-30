## ADJUST THESE CREDENTIALS WHEN NEEDED ______________________________________________________________________
# Create the BlobServiceClient
connection_string = "REDACTED-SECRET-KEY"

# Use only the predefined container name
container_name = "aava-ggm"

blob_storage_url = "avaplusstorageprod.blob.core.windows.net/aava-ggm"

from crewai.tools import BaseTool
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
from pydantic import BaseModel, Field
import logging
import re
import os


# Define the args schema for your tool
class AzureBlobWriterSchema(BaseModel):
    folder_name: str = Field(..., description="Name of the folder to create in Azure Blob Storage")
    file_name: str = Field(..., description="Name of the file to create in the folder")
    content: str = Field(..., description="Content to write to the file")


# Set up secure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='azure_blob_operations.log'
)
logger = logging.getLogger('AzureBlobWriterTool')


class AzureBlobWriterTool(BaseTool):
    name: str = "Azure Blob Storage Tool"
    description: str = "Creates folders and files in Azure Blob Storage."
    args_schema: type[BaseModel] = AzureBlobWriterSchema

    def __init__(self):
        super().__init__(
            name="Azure Blob Storage Tool",
            description="Creates folders and files in Azure Blob Storage."
        )

    def _sanitize_path_component(self, component):
        """
        Sanitizes path components to prevent directory traversal and other issues.
        """
        if not component:
            return "default"

        # Remove any path traversal sequences and other potentially dangerous characters
        sanitized = re.sub(r'[\\/*?:"<>|]', '_', component)
        sanitized = re.sub(r'\.\.', '_', sanitized)

        # Ensure the component doesn't start with a dot or slash
        sanitized = sanitized.lstrip('./\\')

        return sanitized if sanitized else "default"

    def _validate_content(self, content):
        """
        Validates content to ensure it's safe to upload.
        """
        if not isinstance(content, str):
            logger.warning("Content is not a string, converting to string")
            return str(content)

        # Limit content size if needed
        max_size = 10 * 1024 * 1024  # 10 MB
        if len(content.encode('utf-8')) > max_size:
            logger.warning("Content exceeds maximum allowed size")
            return content[:max_size]  # Truncate to max size

        return content

    def create_folder_and_file_in_blob_storage(self, folder_name, file_name, content):
        """
        Creates a folder and a file in Azure Blob Storage.
        :param folder_name: string, name of the folder to create.
        :param file_name: string, name of the file to create.
        :param content: string, the content you want to save.
        """
        try:

            # Sanitize inputs
            # sanitized_folder_name = self._sanitize_path_component(folder_name)
            sanitized_folder_name = folder_name  # removed sanitization for the subfolder
            sanitized_file_name = self._sanitize_path_component(file_name)
            validated_content = self._validate_content(content)

            # Log if sanitization changed the inputs
            if sanitized_folder_name != folder_name:
                logger.warning(f"Folder name sanitized from '{folder_name}' to '{sanitized_folder_name}'")
            if sanitized_file_name != file_name:
                logger.warning(f"File name sanitized from '{file_name}' to '{sanitized_file_name}'")

            blob_service_client = BlobServiceClient.from_connection_string(connection_string)

            # Check if container exists, create if not
            try:
                container_client = blob_service_client.get_container_client(container_name)
                if not container_client.exists():
                    container_client = blob_service_client.create_container(container_name)
                    result = f"Container '{container_name}' created successfully. blob_storage_url = '{blob_storage_url}'"
    
                else:
                    result = f"Container '{container_name}' already exists.  blob_storage_url = '{blob_storage_url}'"


            except Exception as e:
                logger.error(f"Error checking/creating container: {str(e)}", exc_info=True)
                return "Error accessing container. Please try again later or contact support."
                

            # In Azure Blob Storage, folders are virtual and represented by prefixes in blob names
            # Create a blob with the folder prefix to simulate folder creation
            folder_path = f"{sanitized_folder_name}/"
            folder_blob_client = container_client.get_blob_client(folder_path)

            try:
                # Upload empty content to create the "folder"
                folder_blob_client.upload_blob("", overwrite=True)
                result += f"\nFolder '{sanitized_folder_name}' created successfully."
            except Exception as e:
                logger.error(f"Error creating folder: {str(e)}", exc_info=True)
                return "Error creating folder. Please try again later or contact support."

            # Create the file within the folder
            file_path = f"{sanitized_folder_name}/{sanitized_file_name}"
            file_blob_client = container_client.get_blob_client(file_path)

            try:
                # Upload the content to the file
                file_blob_client.upload_blob(validated_content, overwrite=True)
                result += f"\nFile '{sanitized_file_name}' created successfully in folder '{sanitized_folder_name}'."
            except Exception as e:
                logger.error(f"Error creating file: {str(e)}", exc_info=True)
                return "Error creating file. Please try again later or contact support."

            return result

        except Exception as e:
            # Log the full error details but return a generic message
            logger.error(f"An error occurred: {str(e)}", exc_info=True)
            return "An error occurred while processing your request. Please try again later or contact support."

    def _run(self, folder_name, file_name, content):
        """
        Run method required by CrewAI BaseTool.
        """
        return self.create_folder_and_file_in_blob_storage(folder_name, file_name, content)