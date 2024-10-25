from enum import Enum
from chunks.chunking import (
    normal_chunking,
    semantic_chunking,
    llama_parse,
    convert_llama_to_langchain,
    get_page_nodes,
)
from utils.initialize import load_env_variables
from utils.config_settings import config

env_name = load_env_variables()



LLAMA_PARSE_API_KEY = config[env_name].LLAMA_PARSE_API_KEY


# Define the Enum for chunking strategies
class ChunkingStrategy(Enum):
    RECURSIVE = "recursive"
    MARKDOWN = "markdown"
    SEMANTIC = "semantic"

def get_chunking_strategy(strategy: ChunkingStrategy, documents: str, embedding_model=None):
    try:
        # Convert the string input to the appropriate Enum value
        strategy_enum = ChunkingStrategy(strategy.lower())
    except ValueError:
        raise ValueError(f"Unsupported source: {strategy}")
    if strategy_enum == ChunkingStrategy.RECURSIVE:
        return normal_chunking(documents)
    elif strategy_enum == ChunkingStrategy.MARKDOWN:
        # documents = await llama_parse(documents)
        sub_docs = get_page_nodes(documents)
        return convert_llama_to_langchain(sub_docs)
    elif strategy_enum == ChunkingStrategy.SEMANTIC:
        return semantic_chunking(documents, embedding_model)
    else:
        raise ValueError(f"Unknown chunking strategy: {strategy}")


