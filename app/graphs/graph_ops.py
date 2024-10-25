from langchain_experimental.graph_transformers import LLMGraphTransformer
from chunks.chunking import *


def add_graph_to_db(documents, llm, graph):
    """
    Add document chunks to the Neo4j graph database.

    Args:
        graph (Neo4jGraph): The Neo4j graph object

    Returns:
        str: Success message
    """
    llm_transformer = LLMGraphTransformer(llm=llm)
    graph_documents = llm_transformer.convert_to_graph_documents(documents)
    print(graph_documents)
    graph.add_graph_documents(
        graph_documents, baseEntityLabel=True, include_source=True
    )
    print("Docs Added")
    return "Graph added to DB"
