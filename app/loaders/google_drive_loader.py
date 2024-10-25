import os
from dotenv import load_dotenv
from google.oauth2 import service_account
from googleapiclient.discovery import build
from unstructured.partition.pdf import partition_pdf
from unstructured.partition.docx import partition_docx
from unstructured.partition.image import partition_image
import mimetypes
from io import BytesIO
from loaders.base_loader import BaseDataLoader
from langchain.schema import Document
# Load environment variables
from utils.initialize import load_env_variables
from utils.config_settings import config

env_name = load_env_variables()
GOOGLE_DRIVE_FOLDER_ID = config[env_name].GOOGLE_DRIVE_FOLDER_ID
GOOGLE_APPLICATION_CREDENTIALS = config[env_name].GOOGLE_APPLICATION_CREDENTIALS

def process_file_callback(file_id, mime_type, service, file_name):
    """
    Process and extract content from a file based on its MIME type using `unstructured`.
    Returns a Langchain Document with the extracted text and metadata.
    """
    try:
        request = service.files().get_media(fileId=file_id)
        file_content = BytesIO(request.execute())  # Retrieve file content

        extracted_text = f"Processing file: {file_name}\n"

        # Process PDF files using `unstructured`
        if mime_type == "application/pdf":
            elements = partition_pdf(file=file_content)
            extracted_text += ''.join([str(el) for el in elements])

        # Process DOCX files using `unstructured`
        elif mime_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            elements = partition_docx(file=file_content)
            extracted_text += ''.join([str(el) for el in elements])

        # Process image files using `unstructured`
        elif mime_type in ["image/png", "image/jpeg"]:
            elements = partition_image(file=file_content)
            extracted_text += ''.join([str(el) for el in elements])

        else:
            return None, f"Unsupported MIME type: {mime_type}"

        # Create and return Langchain Document
        document = Document(page_content=str(extracted_text), metadata={"source": file_name, "mime_type": mime_type})
        return document, None

    except Exception as e:
        return None, f"Failed to extract content for file {file_name} (ID: {file_id}): {str(e)}"


class GoogleDriveDataLoader(BaseDataLoader):
    def __init__(self):
        super().__init__()
        self.folder_id = GOOGLE_DRIVE_FOLDER_ID
        if not self.folder_id:
            raise ValueError("Missing Google Drive folder ID.")

        # Store the file types (if specified)
        self.file_types = os.getenv("FILE_TYPE", "pdf").split(
            ","
        ) 
        # Load Google Drive API credentials
        self.creds = service_account.Credentials.from_service_account_file(
            GOOGLE_APPLICATION_CREDENTIALS
        )
        self.service = build("drive", "v3", credentials=self.creds)

    def load_data(self, file_type):

        file_type = "pdf,image,docx"
        self.file_types = file_type.split(",")
        """
        Load and process the files in the specified Google Drive folder.
        """
        try:
            # Process the files in the specified folder
            return self.process_files_by_type(self.folder_id, self.service, self.file_types)

        except Exception as e:
            raise RuntimeError(f"An error occurred while loading data: {str(e)}")

    def process_files_by_type(self, folder_id, service, file_types=None):
        """
        Process all files in the specified Google Drive folder by file type using `unstructured`.
        This method is now part of the `GoogleDriveDataLoader` class.
        """
        
        try:
            query = f"'{folder_id}' in parents"
            results = (
                service.files()
                .list(q=query, fields="files(id, name, mimeType)")
                .execute()
            )
            items = results.get("files", [])

            if not items:
                return "No files found in the folder."

            extracted_documents = []  # List to store extracted Langchain Document objects
            for item in items:
                mime_type = item.get("mimeType")
                file_id = item.get("id")
                file_name = item.get("name")
            
                # Check if the file type matches the specified types before processing
                if mime_type == "application/pdf" and 'pdf' in file_types:
                    document, error = process_file_callback(file_id, mime_type, service, file_name)
                elif mime_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document" and 'docx' in file_types:
                    document, error = process_file_callback(file_id, mime_type, service, file_name)
                elif mime_type in ["image/png", "image/jpeg"] and 'image' in file_types:
                    document, error = process_file_callback(file_id, mime_type, service, file_name)
                else:
                    error = f"Unsupported file type: {mime_type}"
                    document = None

                if document:
                    extracted_documents.append(document)
                elif error:
                    print(error)

            return extracted_documents

        except Exception as e:
            raise RuntimeError(f"An error occurred while processing files by type: {str(e)}")
