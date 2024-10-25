import os
from abc import ABC, abstractmethod
import mimetypes


class BaseDataLoader(ABC):
    def __init__(self):
        self.download_folder = os.path.join(
            os.getcwd(), "downloaded_files"
        )  # Folder to store downloaded files
        self.file_types = os.getenv("FILE_TYPE", "pdf").split(
            ","
        )  # Get file types from .env file

        # Define folder structure for different file types
        self.file_type_folder = {
            "pdf": "pdf_files",
            "docx": "docx_files",
            "image": "image_files",
            "all":"all_files",
        }

        # Ensure type-specific folders exist
        for folder_name in self.file_type_folder.values():
            folder_path = os.path.join(self.download_folder, folder_name)
            os.makedirs(folder_path, exist_ok=True)

    @abstractmethod
    def load_data(self):
        """
        Abstract method that must be implemented by each child class.
        It defines how to load data from a specific source.
        """
        pass

    def process_files(self, files, file_type_folder):
        """
        Process files and save them to the local system.
        """
        pass

    def get_mime_type(self, file_path):
        """
        Determine the MIME type of the file.
        """
        mime_type, _ = mimetypes.guess_type(file_path)
        return mime_type or "unknown"
