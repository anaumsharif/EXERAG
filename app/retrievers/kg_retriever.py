import sqlite3
from operator import itemgetter

from langchain.chains import create_sql_query_chain
from langchain.schema.runnable import RunnableMap
from langchain_community.tools.sql_database.tool import QuerySQLDataBaseTool
from langchain_community.utilities import SQLDatabase
from langchain_community.vectorstores import Neo4jVector
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from utils.initialize import neo4j_creds
from utils.config_settings import config
from utils.initialize import openai_embed_model, cohere_embedding_model
from prompt.templates import system_prompt, sql_prompt
from utils.initialize import load_env_variables

env_name = load_env_variables()
COHERE_API_KEY = config[env_name].COHERE_API_KEY

url, username, password = neo4j_creds()
openai_embedding = openai_embed_model()
cohere_embedding = cohere_embedding_model(COHERE_API_KEY, model="embed-english-v3.0")
vector_index = Neo4jVector.from_existing_graph(
    openai_embedding,
    search_type="hybrid",
    node_label="Document",
    text_node_properties=["text"],
    embedding_node_property="openai_embedding",
    url=url,
    username=username,
    password=password,
)


def hybrid_kg_retriever():
    retriever = vector_index.as_retriever(search_kwargs={"k": 8})
    return retriever


def qa_chain_with_source(llm, retriever):
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            ("human", "{input}"),
        ]
    )
    chain = (
        RunnableMap(
            {
                "context": lambda x: retriever.invoke(x["input"]),
                "input": lambda x: x["input"],
            }
        )
        | prompt
        | llm
        | StrOutputParser()
    )

    return chain


def sql_chain(llm):
    db = SQLDatabase.from_uri("sqlite:///./app/documents.db")
    print(db.dialect)
    print(db.get_usable_table_names())

    execute_query = QuerySQLDataBaseTool(db=db)
    write_query = create_sql_query_chain(llm, db)
    sql_prompt_template = PromptTemplate.from_template(sql_prompt)
    answer = sql_prompt_template | llm | StrOutputParser()
    chain = (
        RunnablePassthrough.assign(query=write_query).assign(
            result=itemgetter("query") | execute_query
        )
        | answer
    )

    return chain
