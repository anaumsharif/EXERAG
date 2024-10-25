from utils.initialize import load_env_variables, pinecone_setup
from utils.config_settings import config
from langchain.vectorstores import Weaviate
from langchain.vectorstores import FAISS
from pinecone import ServerlessSpec
from langchain.docstore import InMemoryDocstore
from langchain_chroma import Chroma
from langchain_pinecone import PineconeVectorStore

import time
import faiss
import numpy as np
env_name = load_env_variables()


def get_vector_store(store_name: str, embeddings, embedding_model,embedding_model_name):
    env = load_env_variables()
    if store_name.lower() == "faiss":
        # Create the FAISS index
        dimension = len(embeddings[0])
        faiss_index = faiss.IndexFlatL2(dimension)  # Using L2 (Euclidean distance) for flat index
        
        # Create an in-memory document store
        docstore = InMemoryDocstore()
        
        # Create the index to docstore id mapping
        index_to_docstore_id = {i: str(i) for i in range(len(embeddings))}
        
        # Initialize the FAISS vector store
        faiss_vector_store = FAISS(
            index=faiss_index,
            docstore=docstore,
        
            index_to_docstore_id=index_to_docstore_id,
            embedding_function=embedding_model
        )
        
        # Add embeddings to the vector store
        faiss_vector_store.index.add(np.array(embeddings))
        
        return faiss_vector_store

    elif store_name.lower() == "pinecone":
        pc,index_name = pinecone_setup()

        existing_indexes = [index_info["name"] for index_info in pc.list_indexes()]
        if index_name not in existing_indexes:
            print(f"Creating new index: {index_name}")
        
            try:
                if embedding_model_name == "openai":
                    pc.create_index(
                        name=index_name,
                        dimension=1536,
                        metric="cosine",
                        spec=ServerlessSpec(
                            cloud="aws",
                            region="us-east-1"
                        ),
                        deletion_protection="disabled"
                    )
                elif embedding_model_name == "cohere":
                    pc.create_index(
                        name=index_name,
                        dimension=1024,
                        metric="cosine",
                        spec=ServerlessSpec(
                            cloud="aws",
                            region="us-east-1"
                        ),
                        deletion_protection="disabled"
                    )
                print(f"Index {index_name} created successfully.")
            except Exception as e:
                print(f"Error creating index: {e}")
                
        index = pc.Index(index_name)

        print(index.describe_index_stats())
        pinecone_vector_store = PineconeVectorStore(index=index, embedding=embedding_model)
        return index,pinecone_vector_store


        
    elif store_name.lower() == "chroma":

        chroma_vector_store = Chroma(
            collection_name="test_collection",
            embedding_function=embedding_model,
            persist_directory="./chroma_langchain_db",  # Where to save data locally, remove if not necessary
            )
        return chroma_vector_store

    else:
        raise ValueError(f"Unknown vector store: {store_name}")
