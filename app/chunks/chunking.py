from copy import deepcopy
from llama_index.core.schema import Document as LlamaDoc
from langchain.schema import Document as LangChainDoc
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_experimental.text_splitter import SemanticChunker
from langchain_text_splitters import RecursiveCharacterTextSplitter
from llama_index.core import SimpleDirectoryReader
from llama_index.core.schema import Document as lid
from llama_parse import LlamaParse
from utils.config_settings import config
from utils.initialize import load_env_variables
import nest_asyncio

nest_asyncio.apply()

env_name = load_env_variables()

LLAMA_PARSE_API_KEY = config[env_name].LLAMA_PARSE_API_KEY


def normal_chunking(documents):
    """
    Load PDF documents and split them into manageable chunks.

    Returns:
        list: A list of document chunks
    """
    # Load PDF documents from a directory
    # loader = PyPDFDirectoryLoader(folder_path)
    # pages = loader.load()

    # Split documents into chunks
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=200)
    docs = text_splitter.split_documents(documents)

    return docs


####==========================SemanticChunking====================####
def semantic_chunking(documents, embedding):
    # loader = PyPDFDirectoryLoader(folder_path)

    # pages = loader.load()
    semantic_splitter = SemanticChunker(
        embedding,
        # breakpoint_threshold_type="gradient"
    )
    semantic_docs = semantic_splitter.split_documents(documents)
    return semantic_docs


####==========================LLAMAINDEX==========================####
async def llama_parse(folder_path):
    """
    Parse documents using the LlamaParse API.

    Returns:
        list: Parsed documents
    """
    print("### Setting parser ###")
    parser = LlamaParse(
        api_key=LLAMA_PARSE_API_KEY, result_type="markdown", verbose=True
    )

    print("### Setting extractor ###")
    file_extractor = {".pdf": parser}

    print("### Setting directory reader ###")
    filename_fn = lambda filename: {"file_name": filename}
    reader = SimpleDirectoryReader(
        folder_path, file_metadata=filename_fn, file_extractor=file_extractor
    )

    print("### Loading documents using reader ###")
    
    documents = await reader.aload_data()
    print(documents)
    return documents



from llama_index.core.schema import Document as LlamaDoc
from langchain.schema import Document as LangChainDoc

from llama_index.core.schema import Document as LlamaDoc
from langchain.schema import Document as LangChainDoc

def get_page_nodes(docs, separator="\n---\n"):
    """
    Split each document into page nodes by a separator.

    Args:
        docs (list): List of documents
        separator (str): Separator string to split documents

    Returns:
        list: List of page nodes
    """
    nodes = []
    for doc in docs:
        # Check if it's a LlamaIndex document or a LangChain document
        if isinstance(doc, LlamaDoc):
            doc_chunks = doc.text.split(separator)
        elif isinstance(doc, LangChainDoc):
            doc_chunks = doc.page_content.split(separator)
        else:
            raise TypeError(f"Unsupported document type: {type(doc)}")

        # Process each chunk, ignoring empty ones
        for doc_chunk in doc_chunks:
            doc_chunk = doc_chunk.strip()  # Remove leading/trailing whitespace
            if doc_chunk:  # Skip empty chunks
                node = LlamaDoc(text=doc_chunk, metadata=deepcopy(doc.metadata))
                nodes.append(node)

    return nodes




####==========================LLAMAINDEX TO LANGCHAIN==========================####


def convert_llama_to_langchain(llama_docs):
    """
    Convert LlamaParse documents into Langchain Document format.

    Args:
        llama_docs (list): List of LlamaParse documents

    Returns:
        list: List of Langchain formatted documents
    """
    langchain_docs = []
    for llama_doc in llama_docs:

        text_content = llama_doc.text
        file_name = llama_doc.metadata["file_name"]

        # Create metadata for LangChain document
        metadata = {
            "source_name": file_name,
            "page": 0,  # Default to page 0; adjust if needed for multi-page documents
        }

        # Create a new LangChain Document
        langchain_doc = LangChainDoc(metadata=metadata, page_content=text_content)
        langchain_docs.append(langchain_doc)

    return langchain_docs
