from fastapi.responses import JSONResponse
from langchain_core.messages import HumanMessage
from langchain_core.prompts import ChatPromptTemplate

from agents.agent import Agent
from agents.tools import (
    create_agent_executor,
    get_retriever_tool,
    get_knowledge_graph_for_documents,
    get_knowledge_graph_for_entity,
    get_sql_db,
)


async def agent_with_sql_and_kg_for_docs(
    question, llm, sql_question_retriever, hybrid_kg_retriever
):
    prompt_template = """You are an AI assistant tasked with answering questions using the best available tools.

    Information about the tools is below : 

    1. If the question is related to document which needs multiple parts or hop across the documents, use knowledge 
    knowledge_graph_for_documents.
    name of tool - `knowledge_graph_for_documents` - have knowledge graph of all the content of documents .
    Try to always return the source file name in a structured format for each answer.Sources should always be in 
    Bullet points
    Input & Output args : str -> str

    2. If the question is related to name of documents, or number of documents, or some question which can be answered 
    using sql database then use sql_db_for_documents, it is using other llm so you have to wait to get the answer.
    name of tool - `sql_db_for_documents` - have information about number of documents which are embedded in the knowledge graph and their names.
    Input & Output args : str -> str


    For some complex queries you might have to make multiple trips to these documents, feel free to do and if you 
    find some older year info, try to find again if latest year info is also available about the info.

    Do not call any tool more than 3 times.
    Maximum you can try same tool is 3 times.
    
    Use your judgment to choose the right tool and give me final answer in the end.

    If you don't have any tool to use, then use llm call to fetch info about user question.

    And Before giving the final answer , pls evaluate the answer and user question with llm and tell 
    how pertinent the answer is to user question. 
    And if it's not relevant or pertinent , fetch more info using tools at your disposal and try to answer it.

    "placeholder", "{agent_scratchpad}"

    Question: {input}
    Answer:
    """
    sql_db_for_documents = get_sql_db(sql_question_retriever)
    knowledge_graph_for_documents = get_knowledge_graph_for_documents(
        hybrid_kg_retriever
    )
    abot = Agent(
        llm, [knowledge_graph_for_documents, sql_db_for_documents], prompt_template
    )
    messages = [HumanMessage(content=question)]
    result = abot.graph.invoke({"messages": messages})
    return JSONResponse(
        content={"question": question, "answer": result["messages"][-1].content}
    )


async def agent_with_kg_for_entity_and_docs(
    question, llm, kg_retriever, hybrid_kg_retriever
):
    prompt_template = """You are an AI assistant tasked with answering questions using the best available retriever.

    Information about the tools is below : 

    1. If the question is related to document which needs multiple parts or hop across the documents, use knowledge 
    get_knowledge_graph_for_documents.
    name of tool - `knowledge_graph_for_documents` - have knowledge graph of all the content of documents .
    Input & Output args : str -> str

    2. If the question is related to entities, relationships, or specific knowledge-based queries, use the knowledge 
    get_knowledge_graph_for_entity.
    name of tool - `knowledge_graph_for_entity` - have knowledge graph of entities in these documents.
    Input & Output args : str -> str


    For some complex queries you might have to make multiple trips to these documents, feel free to do and if you 
    find some older year info, try to find again if latest year info is also available about the info.

    Use your judgment to choose the right tool and give me final answer in the end.

    If you don't have any tool to use, then use llm call to fetch info about user question.

    And Before giving the final answer , pls evaluate the answer and user question with llm and tell 
    how pertinent the answer is to user question. 
    And if it's not relevant or pertinent , fetch more info using tools at your disposal and try to answer it.

    "placeholder", "{agent_scratchpad}"

    Question: {input}
    Answer:
    """
    knowledge_graph_for_entity = get_knowledge_graph_for_entity(kg_retriever)
    knowledge_graph_for_documents = get_knowledge_graph_for_documents(
        hybrid_kg_retriever
    )
    abot = Agent(
        llm,
        [knowledge_graph_for_documents, knowledge_graph_for_entity],
        prompt_template,
    )
    messages = [HumanMessage(content=question)]
    result = abot.graph.invoke({"messages": messages})
    return JSONResponse(
        content={"question": question, "answer": result["messages"][-1].content}
    )


async def agent_with_doc_retrieval_and_kg_for_entity_and_docs(
    question, llm, vectordb_retriever, kg_retriever, hybrid_kg_retriever
):
    prompt_template = """You are an AI assistant tasked with answering questions using the best available retriever.

    You have following tasks in order 
    1) For user question, divide the user question into smaller parts and paraphrase those smaller parts.
    2) For each paraphrased question, choose the right retriever tool and fetch the information using tools you have
    3) Combine all the info you receive from the tools and try to answer the question.


    Information about the tools is below : 
    1. If the question is related to retrieving chunks of documents or content 
    from text, use the doc_retriever_tool retriever.

    2. If the question is related to entities, relationships, or specific knowledge-based queries, use the knowledge 
    get_knowledge_graph_for_entity.

    3. If the question is related to document which needs multiple parts or hop across the documents, use knowledge 
    get_knowledge_graph_for_documents.

    Questions will be asked about contract , pricing , terms & conditions between these entities and different 
    entities in these contracts, whose information is provided `doc_retriever_tool`, `knowledge_graph_for_entity` and 
    `knowledge_graph_for_documents`.

    `doc_retriever_tool` - have document embedding

    `knowledge_graph_for_entity` - have knowledge graph of entities in these documents.

    `knowledge_graph_for_documents` - have knowledge graph of all the content of documents .

    For some complex queries you might have to make multiple trips to these documents, feel free to do and if you 
    find some older year info, try to find again if latest year info is also available about the info.

    Use your judgment to choose the right tool and give me final answer in the end.

    If you don't have any tool to use, then use llm call to fetch info about user question.

    And Before giving the final answer , pls evaluate the answer and user question with llm and tell 
    how pertinent the answer is to user question. 
    And if it's not relevant or pertinent , fetch more info using tools at your disposal and try to answer it.

    "placeholder", "{agent_scratchpad}"

    Question: {input}
    Answer:
    """
    doc_retriever_tool = get_retriever_tool(vectordb_retriever)
    knowledge_graph_for_entity = get_knowledge_graph_for_entity(kg_retriever)
    knowledge_graph_for_documents = get_knowledge_graph_for_documents(
        hybrid_kg_retriever
    )
    abot = Agent(
        llm,
        [doc_retriever_tool, knowledge_graph_for_entity, knowledge_graph_for_documents],
        prompt_template,
    )
    messages = [HumanMessage(content=question)]
    result = abot.graph.invoke({"messages": messages})
    return JSONResponse(
        content={"question": question, "answer": result["messages"][-1].content}
    )


async def agent_with_doc_retrieval_and_kg_for_entity(
    question,
    llm,
    vectordb_retriever,
    kg_retriever,
):
    prompt_template = """
    You are an AI assistant tasked with answering questions using the best available retriever. 

    1. If the question is related to retrieving chunks of documents or content from text, use the doc_retriever_tool retriever.

    2. If the question is related to entities, relationships, or specific knowledge-based queries, use the knowledge graph retriever.

    Use your judgment to choose the right tool and give me final answer in the end.

    If you don't have any tool to use, then use llm call to fetch info about user question.

    Try to limit yourself to max of 2 calls, not more than it.

    "placeholder", "{agent_scratchpad}"

    Question: {input}
    Answer:
    """
    prompt = ChatPromptTemplate.from_template(prompt_template)
    doc_retriever_tool = get_retriever_tool(vectordb_retriever)
    knowledge_graph_retriever = get_knowledge_graph_for_entity(kg_retriever)
    agent_executor = create_agent_executor(
        llm, [doc_retriever_tool, knowledge_graph_retriever], prompt
    )
    answer = agent_executor.invoke({"input": question})
    return JSONResponse(content={"question": question, "answer": answer})
