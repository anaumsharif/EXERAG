# main.py
import os
from enum import Enum


# Define the Enum for data loader types
class DataLoaderType(Enum):
    AWS = "aws"
    AZURE = "azure"
    GOOGLE_DRIVE = "google_drive"
    URL = "url"
    SHAREPOINT = "sharepoint"
    GITHUB='github'
    NOTION='notion'
    DOCUMENT='document'


# Function to load the appropriate data loader based on the source
def load_source(source: str):
    try:
        # Convert the string input to the appropriate Enum value
        source_enum = DataLoaderType(source.lower())
    except ValueError:
        raise ValueError(f"Unsupported source: {source}")

    if source_enum == DataLoaderType.AWS:
        from loaders.aws_loader import AWSDataLoader
        loader = AWSDataLoader()
    elif source_enum == DataLoaderType.AZURE:
        from loaders.azure_loader import AzureDataLoader
        loader = AzureDataLoader()
    elif source_enum == DataLoaderType.GOOGLE_DRIVE:
        from loaders.google_drive_loader import GoogleDriveDataLoader
        loader = GoogleDriveDataLoader()
    elif source_enum == DataLoaderType.URL:
        from loaders.url_loader import URLDataLoader
        loader = URLDataLoader()
    elif source_enum == DataLoaderType.SHAREPOINT:
        from loaders.sharepoint_loader import SharePointDataLoader
        loader = SharePointDataLoader()
    elif source_enum == DataLoaderType.GITHUB:
        from loaders.github_loader import GithubLoader
        loader = GithubLoader()
    elif source_enum == DataLoaderType.NOTION:
        from loaders.notion_loader import NotionDataLoader
        loader = NotionDataLoader()
    elif source_enum == DataLoaderType.DOCUMENT:
        from loaders.document_loader import DocumentLoader
        loader = DocumentLoader()
    else:
        raise ValueError(f"Unsupported source: {source_enum}")

    return loader
