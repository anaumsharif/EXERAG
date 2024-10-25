# azure_loader.py
import os
from dotenv import load_dotenv
from azure.storage.blob import BlobServiceClient, ContainerClient
from azure.core.exceptions import ResourceNotFoundError, ClientAuthenticationError
from langchain_community.document_loaders import AzureBlobStorageContainerLoader
import nltk
from unstructured.partition.pdf import partition_pdf  # Unstructured PDF handling
from unstructured.partition.docx import partition_docx  # Unstructured DOCX handling
from unstructured.partition.image import partition_image  # Unstructured image handling
from io import BytesIO
from loaders.base_loader import BaseDataLoader
from langchain.schema import Document

# Load environment variables
from utils.initialize import load_env_variables
from utils.config_settings import config

env_name = load_env_variables()


SAS_URL = config[env_name].SAS_URL
AZURE_CONTAINER_NAME=config[env_name].AZURE_CONTAINER_NAME
CONN_STR=config[env_name].CONNECTION_STR

def process_file_callback(file_key, file_content):
    """
    Extract text from the file content based on the file type and return it.
    """
    extracted_text = f"\nProcessing file: {file_key}\nFile size: {len(file_content)} bytes."

    # Handle PDF files
    if file_key.endswith('.pdf'):
        try:
            pdf_parts = partition_pdf(file=BytesIO(file_content))
            pdf_text = "\n".join([str(part) for part in pdf_parts])
            extracted_text += f"\nExtracted text from {file_key}:\n{pdf_text}"
        except Exception as e:
            extracted_text += f"\nFailed to extract text from {file_key}: {str(e)}"

    # Handle DOCX files
    elif file_key.endswith('.docx'):
        try:
            docx_parts = partition_docx(file=BytesIO(file_content))
            docx_text = "\n".join([str(part) for part in docx_parts])
            extracted_text += f"\nExtracted text from {file_key}:\n{docx_text}"
        except Exception as e:
            extracted_text += f"\nFailed to extract text from {file_key}: {str(e)}"

    # Handle image files (JPG, PNG) using Unstructured
    elif file_key.lower().endswith(('.png', '.jpeg', '.jpg')):
        try:
            image_parts = partition_image(file=BytesIO(file_content))
            image_text = "\n".join([str(part) for part in image_parts])
            extracted_text += f"\nExtracted text from image {file_key}:\n{image_text}"
        except Exception as e:
            extracted_text += f"\nFailed to extract text from image {file_key}: {str(e)}"

    # If the file type isn't recognized
    else:
        extracted_text += f"\nUnrecognized file type for {file_key}."

    return extracted_text


class AzureDataLoader(BaseDataLoader):
    def __init__(self):
        # Fetch credentials and file types from .env
        super().__init__()
        self.sas_url = SAS_URL
        self.conn_str = CONN_STR
        self.container_name = AZURE_CONTAINER_NAME
        self.file_types = os.getenv("FILE_TYPE", "all").split(
            ","
        ) 


    def load_data(self,file_type):
        """
        Loads data from the Azure Blob Storage and processes files based on the given file types.
        Returns a list of extracted texts.
        """

        self.file_types=file_type.split(",")   

        try:
            if 'all' in self.file_types:
                extracted_texts = self.process_all_files()
            else:
                extracted_texts = self.process_files_by_type()
        except Exception as e:
            raise RuntimeError(f"An error occurred: {str(e)}")

        return extracted_texts

    def process_all_files(self):
        """
        Process all files in the Azure Blob Storage using AzureBlobStorageContainerLoader.
        Returns a list of extracted texts.
        """

        self.loader = AzureBlobStorageContainerLoader(
                conn_str=self.conn_str,
                container=self.container_name
            )
        langchain_documents = []  # Initialize a list for Langchain Document objects
        try:
            documents = self.loader.load()  # Load all files using AzureBlobStorageContainerLoader
            for doc in documents:
                file_key = doc.metadata['source']
                file_content = doc.page_content  # Get the content directly
                # Create a Langchain Document
                langchain_doc = Document(page_content=file_content, metadata={"source": file_key})
                langchain_documents.append(langchain_doc)  # Collect Langchain Documents
        except Exception as e:
            raise RuntimeError(f"Error processing files: {str(e)}")  # Raise an error instead of printing
        print(langchain_documents)
        return langchain_documents

    def process_files_by_type(self):
            """
            Process specific file types (e.g., pdf, docx, image).
            Returns a list of LangChain Document objects.
            """
            self.blob_service_client = BlobServiceClient.from_connection_string(self.conn_str)
            self.container_client = self.blob_service_client.get_container_client(self.container_name)

            extracted_documents = []
            try:
                blob_list = self.container_client.list_blobs()

                file_type_filters = {
                    "pdf": ".pdf",
                    "docx": ".docx",
                    "image": (".png", ".jpeg", ".jpg"),
                }

                for blob in blob_list:
                    file_key = blob.name
                    for file_type in self.file_types:
                        extension = file_type_filters.get(file_type.strip())
                        
                        if extension and (
                            (isinstance(extension, tuple) and file_key.endswith(extension)) or 
                            file_key.endswith(extension)
                        ):
                            # Retrieve file content directly from Azure Blob Storage
                            blob_data = self.container_client.download_blob(blob).readall()
                            # Process file and extract text
                            extracted_text = process_file_callback(file_key, blob_data)

                            # Create LangChain Document object with extracted text and metadata
                            document = Document(
                                page_content=extracted_text,  # The extracted text/content
                                metadata={
                                    "source": file_key,       # File name or path
                                    "file_type": file_type    # File type (pdf, docx, image)
                                }
                            )
                            extracted_documents.append(document)  # Collect LangChain Documents

            except Exception as e:
                print(f"Error processing files: {str(e)}")

            return extracted_documents 