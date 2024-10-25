import os
import requests
from dotenv import load_dotenv
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import fitz  # PyMuPDF
from PIL import Image
import pytesseract
import cairosvg
from io import BytesIO
from langchain.schema import Document

from loaders.base_loader import BaseDataLoader

# Load environment variables from the .env file
from utils.initialize import load_env_variables
from utils.config_settings import config


# Initialize environment variables
env_name = load_env_variables()
FILE_URLS = config[env_name].FILE_URLS


def process_file_callback(url):
    """Extract text from HTML, PDF, or image content of the given URL and return it."""
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers)
        content_type = response.headers.get("Content-Type", "")

        if "html" in content_type:
            # Handle HTML extraction
            soup = BeautifulSoup(response.content, "html.parser")
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.extract()
            # Extract and clean the text
            text = soup.get_text()
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            clean_text = "\n".join(chunk for chunk in chunks if chunk)
            return f"Extracted text from {url}:\n{clean_text}\n"

        elif "pdf" in content_type:
            # Handle PDF extraction
            pdf_document = fitz.open(stream=response.content, filetype="pdf")
            text = ""
            for page in pdf_document:
                text += page.get_text()
            pdf_document.close()
            return f"Extracted text from {url}:\n{text}\n"

        elif any(ext in content_type for ext in ["image/png", "image/jpeg", "image/jpg", "image/webp", "image/svg+xml"]):
            # Handle SVG and other image extraction using OCR
            if "svg" in content_type:
                # Convert SVG to PNG using cairosvg
                png_image = cairosvg.svg2png(bytestring=response.content)
                image = Image.open(BytesIO(png_image))
            else:
                # For PNG, JPEG, etc.
                image = Image.open(BytesIO(response.content))
            
            text = pytesseract.image_to_string(image)
            return f"Extracted text from image {url}:\n{text}\n"

        else:
            return f"Unsupported content type for text extraction: {content_type}"

    except Exception as e:
        return f"Error extracting text from {url}: {e}"

class URLDataLoader(BaseDataLoader):
    def __init__(self):
        super().__init__()
        # Load URLs from environment variable and split by comma
        self.file_urls = FILE_URLS.split(",")
        # print(self.file_urls)

        if not self.file_urls:
            raise ValueError("FILE_URLS is not set or contains no URLs")

        # Validate each URL
        self.file_urls = [
            url.strip() for url in self.file_urls if self._is_valid_url(url)
        ]
        if not self.file_urls:
            raise ValueError("No valid URLs found in FILE_URLS")

        print(f"Ready to process the following URLs: {self.file_urls}")

    def load_data(self,file_type):
        extracted_texts = []
        extracted_documents = []
        # Process each URL
        for url in self.file_urls:
            print(f"Processing URL: {url}")
            extracted_text = process_file_callback(url)  # Use the unified function for extraction
            extracted_texts.append(extracted_text)  # Collect the returned text
              # Create a Langchain Document and add metadata
            document = Document(page_content=extracted_text, metadata={"source": url})
            extracted_documents.append(document)  # Collect the returned document

        return extracted_documents # Return all extracted texts

    def _is_valid_url(self, url):
        parsed_url = urlparse(url)
        return all([parsed_url.scheme, parsed_url.netloc])
