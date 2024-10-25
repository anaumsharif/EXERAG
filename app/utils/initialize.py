import os
import time
from dotenv import load_dotenv

from langchain_cohere import CohereEmbeddings
from langchain_cohere.chat_models import ChatCohere
from langchain_community.graphs import Neo4jGraph
from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings
from utils.config_settings import config
from pinecone import Pinecone





def load_env_variables():
    """Load environment variables from .env file."""

    load_dotenv(dotenv_path=".env")
    env_name = os.getenv("FLASK_ENV", "development")
    return env_name

def load_env_variables_test():
    """Load environment variables from .env file."""
    load_dotenv()
    env_name = os.getenv("FLASK_ENV", "testing")
    return env_name


# Load environment variables from .env file
env_name = load_env_variables()

# Get Neo4j credentials from Config_settings File
# NEO4J_URI = config[env_name].NEO4J_URI
# NEO4J_USERNAME = config[env_name].NEO4J_USERNAME
# NEO4J_PASSWORD = config[env_name].NEO4J_PASSWORD
# OPENAI_API_KEY = config[env_name].OPENAI_API_KEY

NEO4J_URI = os.getenv("NEO4J_URI","")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME","")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD","")
OPENAI_API_KEY = config[env_name].OPENAI_API_KEY
PINECONE_API_KEY = config[env_name].PINECONE_API_KEY
PINECONE_INDEX = config[env_name].PINECONE_INDEX_NAME

def neo4j_creds():
    url = NEO4J_URI
    username = NEO4J_USERNAME
    password = NEO4J_PASSWORD
    return url, username, password


def graph_object(url=NEO4J_URI, username=NEO4J_USERNAME, password=NEO4J_PASSWORD):
    """
    Establish a connection to the Neo4j database.

    Args:
        NEO4J_URI (str): URI of the Neo4j database
        NEO4J_USERNAME (str): Username for the Neo4j database
        NEO4J_PASSWORD (str): Password for the Neo4j database

    Returns:
        Neo4jGraph: An object representing the graph database connection
    """
    graph = Neo4jGraph(url=url, username=username, password=password)
    return graph


def openai_llm_model(
    api_key=OPENAI_API_KEY, temperature=0, model_name="gpt-3.5-turbo-0125"
):
    openai_llm = ChatOpenAI(
        temperature=temperature, model_name=model_name, api_key=api_key
    )
    return openai_llm


def openai_embed_model(api_key=OPENAI_API_KEY):
    openai_embedding = OpenAIEmbeddings(api_key=api_key)
    return openai_embedding


def cohere_llm_model(COHERE_API_KEY, temperature=0, model="command-r-plus"):
    cohere_llm = ChatCohere(
        model=model, temperature=temperature, cohere_api_key=COHERE_API_KEY
    )
    return cohere_llm


def cohere_embedding_model(COHERE_API_KEY, model="embed-english-v3.0"):
    cohere_embed_model = CohereEmbeddings(model=model, cohere_api_key=COHERE_API_KEY)
    return cohere_embed_model

def pinecone_setup(api_key=PINECONE_API_KEY,index = PINECONE_INDEX):
    
    pc = Pinecone(api_key)
    index_name = index
    return pc,index_name

