from langchain.agents import AgentExecutor
from langchain.agents import create_tool_calling_agent
from langchain.tools.base import StructuredTool
from langchain.tools.retriever import create_retriever_tool
from langchain_core.pydantic_v1 import BaseModel, Field
from langsmith import traceable


@traceable
def get_retriever_tool(retriever):
    retriever_tool = create_retriever_tool(
        retriever,
        "document_search",
        "Search for information about contracts. For any questions about contracts, you must use this tool!",
    )

    return retriever_tool


@traceable
def get_knowledge_graph_for_entity(kg_retriever):
    return StructuredTool(
        args_schema=ArgsSchema,
        name="get_knowledge_graph_for_entity",
        func=kg_retriever,
        description="Use this tool to extract entities and relationships using the knowledge graph.",
    )


@traceable
def get_knowledge_graph_for_documents(hybrid_kg_retrieved_info):
    return StructuredTool(
        args_schema=ArgsSchema,
        func=hybrid_kg_retrieved_info,
        name="knowledge_graph_for_documents",
        description="Use this tool to extract information from documents which are embedded in the knowledge graph.",
    )


@traceable
def get_sql_db(sql_question_retriever):
    return StructuredTool(
        args_schema=ArgsSchema,
        func=sql_question_retriever,
        name="sql_db_for_documents",
        description="Use this tool to extract information about number of documents which are embedded in the "
        "knowledge graph and their names",
    )


def create_agent_executor(llm, tools, prompt):
    agent = create_tool_calling_agent(llm, tools, prompt)
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
    return agent_executor


class ArgsSchema(BaseModel):
    question: str = Field()
