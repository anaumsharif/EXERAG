# aws_loader.py
import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError
from langchain_community.document_loaders import S3DirectoryLoader
from unstructured.partition.pdf import partition_pdf  # Unstructured PDF handling
from unstructured.partition.docx import partition_docx  # Unstructured DOCX handling
from unstructured.partition.image import partition_image  # Unstructured image handling
from io import BytesIO
from loaders.base_loader import BaseDataLoader
from langchain.schema import Document
import os


# Load environment variables from the .env file
from utils.initialize import load_env_variables
from utils.config_settings import config

env_name = load_env_variables()

AWS_BUCKET_NAME = config[env_name].AWS_BUCKET_NAME
AWS_SECRET_ACCESS_KEY = config[env_name].AWS_SECRET_ACCESS_KEY
AWS_ACCESS_KEY_ID = config[env_name].AWS_ACCESS_KEY_ID


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

class AWSDataLoader(BaseDataLoader):
    def __init__(self):
        super().__init__()
        self.bucket_name = AWS_BUCKET_NAME
        self.aws_access_key_id = AWS_ACCESS_KEY_ID  # Initialize here
        self.aws_secret_access_key = AWS_SECRET_ACCESS_KEY

        
        # Initialize S3DirectoryLoader only if file_types includes 'all'

    def load_data(self,file_type):

        """
        Loads data from the S3 bucket and processes files based on the given file types.
        Returns a list of extracted texts.
        """

        self.file_types=file_type.split(",")  
        extracted_texts = []
        try:
            if 'all' in self.file_types:
                extracted_texts = self.process_all_files_s3_directory()
            else:
                extracted_texts = self.process_files_by_type()
        except (NoCredentialsError, PartialCredentialsError) as e:
            raise RuntimeError(f"Credential error: {str(e)}")
        except Exception as e:
            raise RuntimeError(f"An error occurred: {str(e)}")

        return extracted_texts

    def process_all_files_s3_directory(self):
        """
        Process all files in the S3 bucket using S3DirectoryLoader.
        Returns a list of extracted texts.
        """

        self.loader = S3DirectoryLoader(
                bucket=self.bucket_name,
                aws_access_key_id=self.aws_access_key_id,
                aws_secret_access_key=self.aws_secret_access_key
            )


        extracted_texts = []
        try:
            documents = self.loader.load()  # Use S3DirectoryLoader to load all files
            for doc in documents:
                file_key = doc.metadata['source']
                file_content = doc.page_content  # Use content directly without conversion
                extracted_texts.append((file_key, file_content))  # Collect extracted texts
        except Exception as e:
            print(f"Error processing files: {str(e)}")

        return documents

    def process_files_by_type(self):
        """
        Process specific file types (e.g., pdf, docx, image) from S3.
        Returns a list of LangChain Document objects.
        """
        # Initialize the S3 client
        self.s3_client = boto3.client(
            "s3",
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_access_key,
        )

        extracted_documents = []
        try:
            paginator = self.s3_client.get_paginator('list_objects_v2')
            pages = paginator.paginate(Bucket=self.bucket_name)

            file_type_filters = {
                "pdf": ".pdf",
                "docx": ".docx",
                "image": (".png", ".jpeg", ".jpg"),
            }

            for page in pages:
                if 'Contents' in page:
                    for obj in page['Contents']:
                        file_key = obj['Key']
                        for file_type in self.file_types:
                            extension = file_type_filters.get(file_type.strip())
                            if extension and (
                                (isinstance(extension, tuple) and file_key.endswith(extension)) or 
                                file_key.endswith(extension)
                            ):
                                # Retrieve file content directly from S3
                                response = self.s3_client.get_object(Bucket=self.bucket_name, Key=file_key)
                                file_content = response['Body'].read()  # Retrieve content directly
                                
                                # Extract text content from the file
                                extracted_text = process_file_callback(file_key, file_content)

                                # Create LangChain Document object with extracted text and metadata
                                document = Document(
                                    page_content=extracted_text,  # The extracted text/content
                                    metadata={
                                        "source": file_key,       # File name or path in S3
                                        "file_type": file_type    # File type (pdf, docx, image)
                                    }
                                )
                                extracted_documents.append(document)  # Collect LangChain Documents

        except Exception as e:
            print(f"Error processing files: {str(e)}")

        return extracted_documents 