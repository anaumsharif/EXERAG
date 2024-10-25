from langchain_community.document_loaders import NotionDBLoader
import logging
from typing import Any, Dict, List, Optional
import requests
from langchain_core.documents import Document
from langchain_community.document_loaders.base import BaseLoader
import os
from utils.preprocess import make_text_tokenization_safe
# Load environment variables from the .env file
from utils.initialize import load_env_variables
from utils.config_settings import config

env_name = load_env_variables()

INTEGRATION_TOKEN = config[env_name].INTEGRATION_TOKEN # db
DATABASE_IDS = config[env_name].DATABASE_IDS .split(",") # db
PAGE_IDS = config[env_name].PAGE_IDS.split(",")  # pages
NOTION_BASE_URL = config[env_name].NOTION_BASE_URL  # all
DATABASE_URL = NOTION_BASE_URL + config[env_name].DATABASE_URL
PAGE_URL = NOTION_BASE_URL + config[env_name].PAGE_URL
BLOCK_URL = NOTION_BASE_URL + config[env_name].BLOCK_URL

def docs_preprocessing(documents):
    """Process and clean documents."""
    cleaned_docs = []
    try:
        for doc in documents:
            metadata = doc.metadata
            file_content = make_text_tokenization_safe(doc.page_content)  # Safely tokenize the content
            cleaned_docs.append(Document(page_content=file_content, metadata=metadata))
    except Exception as e:
        print(f"Error processing files: {str(e)}")
    return cleaned_docs


class NotionDataLoader(BaseLoader):
    def __init__(self):
        super().__init__()  # Add super initialization for the loader

        self.integration_token = INTEGRATION_TOKEN
        self.database_ids = DATABASE_IDS
        self.page_ids = PAGE_IDS
        self.headers = {
            "Authorization": f"Bearer {self.integration_token}",
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28",
        }

    def load_data(self,file_type) -> List[Document]:
        """Load data based on the specified file_type (database, pages, or all)."""
        self.file_type = file_type
        if self.file_type == 'database':
            documents = self._load_from_database()
        elif self.file_type == 'pages':
            documents = self._load_from_pages()
        elif self.file_type == 'all':
            documents = self._load_from_all()
        else:
            raise ValueError(f"Unsupported file_type: {self.file_type}")

        return docs_preprocessing(documents)  # Process and return cleaned documents

    def _load_from_database(self) -> List[Document]:
        """Load documents from Notion databases."""
        docs = []
        for single_id in self.database_ids:
            loader = NotionDBLoader(
                integration_token=self.integration_token,
                database_id=single_id,
                request_timeout_sec=30,  # optional, defaults to 10
            )
            docs1 = loader.load()
            docs.extend(docs1)
        return docs

    def _load_from_pages(self) -> List[Document]:
        """Load documents from Notion pages."""
        class NotionPageLoader(BaseLoader):
            """Load content from multiple Notion Pages using the Notion API."""
            def __init__(self, integration_token: str, page_ids: List[str], request_timeout_sec: Optional[int] = 10) -> None:
                if not integration_token:
                    raise ValueError("integration_token must be provided")
                
                # self.page_ids = ["10b1d5ce94bb80ea85e4c15797d26aeb", "10b1d5ce94bb80feb721ceb225ce2d5d"] 
                # print(type(self.page_ids))
                
                # if not page_ids or not isinstance(page_ids, list):
                #     raise ValueError("page_ids must be a valid list of strings")

                self.token = integration_token
                self.page_ids = PAGE_IDS
                self.headers = {
                    "Authorization": f"Bearer {self.token}",
                    "Content-Type": "application/json",
                    "Notion-Version": "2022-06-28",
                }
                self.request_timeout_sec = request_timeout_sec

            def load(self) -> List[Document]:
                documents = []
                for page_id in self.page_ids:
                    page_data = self._retrieve_page(page_id)
                    documents.append(self._process_page(page_data))
                return documents

            def _retrieve_page(self, page_id: str) -> Dict[str, Any]:
                url = PAGE_URL.format(page_id=page_id)
                response = requests.get(url, headers=self.headers, timeout=self.request_timeout_sec)
                response.raise_for_status()
                return response.json()

            def _process_page(self, page_data: Dict[str, Any]) -> Document:
                page_id = page_data["id"]
                metadata = {prop_name.lower(): prop_data.get("rich_text", [{}])[0].get("plain_text", None) for prop_name, prop_data in page_data["properties"].items() if prop_data["type"] == "rich_text"}
                metadata["id"] = page_id
                content = self._load_blocks(page_id)
                return Document(page_content=content, metadata=metadata)

            def _load_blocks(self, block_id: str, num_tabs: int = 0) -> str:
                url = BLOCK_URL.format(block_id=block_id)
                response = requests.get(url, headers=self.headers, timeout=self.request_timeout_sec)
                response.raise_for_status()
                data = response.json()

                result_lines = []
                for result in data["results"]:
                    block_type = result["type"]
                    block_data = result[block_type]
                    if "rich_text" in block_data:
                        cur_result_text = [
                            "\t" * num_tabs + rich_text["text"]["content"]
                            for rich_text in block_data["rich_text"] if "text" in rich_text
                        ]
                        result_lines.extend(cur_result_text)

                    if result["has_children"]:
                        children_text = self._load_blocks(result["id"], num_tabs=num_tabs + 1)
                        result_lines.append(children_text)

                return "\n".join(result_lines)

        loader = NotionPageLoader(integration_token=self.integration_token, page_ids=self.page_ids)
        return loader.load()

    def _load_from_all(self) -> List[Document]:
        """Load documents from both Notion databases and pages."""
        return self._load_from_database() + self._load_from_pages()

