from unstructured.partition.auto import partition
from unstructured.partition.csv import partition_csv
from unstructured.partition.xlsx import partition_xlsx
from unstructured.partition.pdf import partition_pdf
from unstructured.partition.docx import partition_docx
from unstructured.partition.html import partition_html
from unstructured.partition.md import partition_md
from unstructured.partition.image import partition_image
from unstructured.partition.xml import partition_xml
from unstructured.partition.text import partition_text
from langchain.docstore.document import Document  # Import the Document class

# Load environment variables from the .env file
from utils.initialize import load_env_variables
from utils.config_settings import config

env_name = load_env_variables()

FILES = config[env_name].FILES 

def return_loaded_content(all_data):
    """
    Returns the loaded content for each file as a string.
    
    Args:
        all_data (list): The list of extracted file data to return.
    
    Returns:
        str: A formatted string containing the contents of all files.
    """
    content_output = ""

    for file_data in all_data:
        for file_name, elements in file_data.items():
            content_output += f"File: {file_name}\n"
            for element in elements:
                content_output += f"{element}\n"

    return content_output

class DocumentLoader:
    def __init__(self):
        """
        Initializes the loader with a list of file paths.
        
        Args:
            file_paths (list): List of file paths to process.
        """
        self.file_paths = FILES.split(",")  # List of file paths
        self.loader_map = {
            "csv": partition_csv,
            "xlsx": partition_xlsx,
            "xls": partition_xlsx,
            "pdf": partition_pdf,
            "docx": partition_docx,
            "html": partition_html,
            "md": partition_md,
            "bmp": partition_image,
            "jpeg": partition_image,
            "jpg": partition_image,
            "png": partition_image,
            "tiff": partition_image,
            "txt": partition_text,
            "xml": partition_xml,
            "eml": partition,
            "epub": partition,
            "odt": partition,
            "rst": partition,
            "ppt": partition,
            "pptx": partition,
        }

    def get_loader(self, file_path):
        """
        Determines the appropriate loader function based on file extension.
        
        Args:
            file_path (str): The file path to determine the loader for.
        
        Returns:
            function: The loader function for the given file type.
        """
        extension = file_path.split(".")[-1].lower()
        return self.loader_map.get(extension, partition)

    def load_data(self, file_type):
        """
        Loads data from all file paths provided in the initializer.
        
        Returns:
            list: A list of LangChain Document objects extracted from all the files.
        """
        all_data = []

        for file_path in self.file_paths:
            loader_func = self.get_loader(file_path)
            print(f"Loading file: {file_path}")
            elements = loader_func(file_path)  # Process each file

            # Convert each extracted element to a LangChain Document
            documents = [Document(page_content=element.text, metadata={"source": file_path}) for element in elements]
            all_data.append(documents[0])
            print(all_data)
        return all_data  
