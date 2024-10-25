import logging
from fastapi import FastAPI, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from enum import Enum
from typing import List, Union
from langchain.schema import Document
from agents.llm_functions import agent_with_sql_and_kg_for_docs
from graphs.graph_ops import *
from retrievers.kg_retriever import *
from utils.initialize import graph_object
from configurables.llm_configs import get_llm_model
from configurables.embed_configs import get_embedding_model
from configurables.vectordb_configs import get_vector_store
from configurables.chunking_configs import get_chunking_strategy, ChunkingStrategy
from utils.loader import load_source
from graphs.graph_ops import add_graph_to_db   
from langchain_pinecone import PineconeVectorStore
 

# Set logging level to ERROR to suppress warnings
logging.getLogger("langchain_core").setLevel(logging.ERROR)
logging.getLogger("neo4j.notifications").setLevel(logging.ERROR)

graph = graph_object()

# Initialize FastAPI app
app = FastAPI()

# Allow CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this to allow specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
persisted_chunked_docs = []

# Define FastAPI endpoints
@app.get("/")
async def hello_world():
    """
    Basic Hello World ENDPOINT
    """
    return "Hello, Graph RAG llm-service with fastapi!"


@app.post("/api/parsing_and_loading")
async def do_parsing_and_loading(
    source: str = Form(...),
    file_type: str = Form(...),
    embedding_model_name: str = Form(...),
    chunking_strategy: str = Form(...),
    vector_index: str = Form(...),
):
    """
    Combined endpoint to load, parse, chunk, and embed documents.
    """
    # Load documents from the specified source (Google Drive, etc.)
    loader = load_source(source)
    loaded_docs = loader.load_data(file_type=file_type)

    if not loaded_docs:
        return {"error": "No documents found or failed to load documents."}

    # Select embedding model dynamically
    selected_embedding_model = get_embedding_model(embedding_model_name)

    # Select chunking strategy dynamically and apply it to loaded documents
    chunked_docs = get_chunking_strategy(
        chunking_strategy, documents=loaded_docs, embedding_model=selected_embedding_model
    )

    # Ensure the input to embed_documents is a list of strings
    texts = [chunk.page_content for chunk in chunked_docs]
    embeddings = selected_embedding_model.embed_documents(texts)

    global persisted_chunked_docs
    persisted_chunked_docs.extend(chunked_docs)
    
    # Add embeddings and chunked documents to the vector store
    if vector_index == "pinecone":
        index , vector_store = get_vector_store(vector_index, embeddings,selected_embedding_model,embedding_model_name)
    else:    
        vector_store = get_vector_store(vector_index, embeddings,selected_embedding_model,embedding_model_name)
    vector_store.add_documents(chunked_docs) 
    if vector_index == "pinecone":
        print(index.describe_index_stats())
    # Check the number of vectors stored in the FAISS index

    return {"message": "Documents loaded, chunked, and embedded successfully!" , "Chunks":chunked_docs}



@app.post("/api/persist")
async def persist():
    return {"persisted_chunked_docs": persisted_chunked_docs}


@app.post("/api/question/testing")
async def ask_agentic_question(
    question: str = Form(...), llm_model: str = Form(...),
):
    """
    Endpoint to handle user asking a question to chatbot
    """
    # Select LLM model dynamically
    selected_llm_model = get_llm_model(llm_model)

    retriever = hybrid_kg_retriever()
    chain = qa_chain_with_source(selected_llm_model, retriever)
    result = chain.invoke({"input": question})

    return JSONResponse(content={"question": question, "answer": result})


@app.post("/api/questions")
async def ask_question(
    question: str = Form(...),
    llm_model: str = Form(...),
    temprature: float = Form(...),
):
    # Get embedding and LLM models
    selected_llm_model = get_llm_model(llm_model, temprature)

    return await agent_with_sql_and_kg_for_docs(
        question, selected_llm_model, sql_question_retriever, hybrid_kg_retrieved_info
    )

@app.post("/api/retrieval")
async def retrieve(
    query: str = Form(...),
    vector_store: str = Form(...),
):
    embed_model=get_embedding_model("cohere")
    index,vector_store = get_vector_store("pinecone",0,embed_model)
    response = vector_store.similarity_search(query,k=3)
    return response
# @app.post("/api/llamaparse_to_graph")
# async def llamaparse(folder_path : str = Form(...)):
#     chunked_docs = await get_chunking_strategy("markdown", folder_path)
#     graph = graph_object()
#     selected_llm_model = get_llm_model("openai", 0)

#     add_graph_to_db(chunked_docs,llm=selected_llm_model,graph=graph)
    
#     return {"message" : f"Documents Loaded , Chunked Docs:{chunked_docs}, Graph Loaded"}
    

def sql_question_retriever(question: str):
    chain = sql_chain(get_llm_model("openai", 0))
    response = chain.invoke({"question": question})
    return response


def hybrid_kg_retrieved_info(question: str):
    retriever = hybrid_kg_retriever()
    chain = qa_chain_with_source(get_llm_model("cohere", 0), retriever)
    response = chain.invoke({"input": question})
    return response


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app=app, host="127.0.0.1", port=8000)
