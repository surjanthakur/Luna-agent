from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.mongodb import MongoDBSaver  # type: ignore

from langchain.chat_models import init_chat_model
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

from typing_extensions import TypedDict
from typing import List, Annotated

import os
from dotenv import load_dotenv
from system_prompt import system_prompt
from tools import get_weather, web_search, get_location_by_ip
from pymongo import MongoClient

load_dotenv()

GROQ_KEY = os.getenv("GROQ_API_KEY")


# create state
class State(TypedDict):
    messages: Annotated[List, add_messages]


# call llm
llm = init_chat_model(
    model_provider="groq",
    model="openai/gpt-oss-120b",
    api_key=GROQ_KEY,
    temperature=1,
    reasoning_effort="low",
    stop=None,
)
tools = [get_weather, web_search, get_location_by_ip]
llm_with_tools = llm.bind_tools(tools=tools)


# create a chat route
def chatbot(state: State):
    SYSTEM_PROMPT = system_prompt()
    response = llm_with_tools.invoke([SystemMessage(SYSTEM_PROMPT)] + state["messages"])
    return {"messages": response}


graph_builder = StateGraph(State)
tool_node = ToolNode(tools=tools)

# add nodes
graph_builder.add_node("chatbot", chatbot)
graph_builder.add_node("tools", tool_node)

# add edges
graph_builder.add_edge(START, "chatbot")
graph_builder.add_conditional_edges("chatbot", tools_condition)
graph_builder.add_edge("tools", "chatbot")
graph_builder.add_edge("chatbot", END)


# compiling graph
graph = graph_builder.compile()


# add checkpointing using mongodb
def compile_graph_checkpointing(checkpointer):
    graph_checkpointing = graph_builder.compile(checkpointer=checkpointer)
    return graph_checkpointing


# stream graph
def run_graph(messages, chat_id):
    langchain_mesages = []
    for msg in messages:
        if msg["role"] == "user":
            langchain_mesages.append(HumanMessage(content=msg["content"]))
        else:
            langchain_mesages.append(AIMessage(content=msg["content"]))

    state = State({"messages": langchain_mesages})

    DB_URL = os.getenv("MONGO_DB_URL")
    client = MongoClient(DB_URL, serverSelectionTimeoutMS=5000)
    print(client.server_info())
    config = RunnableConfig(configurable={"thread_id": chat_id})
    assistant_response = None

    with MongoDBSaver.from_conn_string(DB_URL) as checkpointer:
        mongo_graph = compile_graph_checkpointing(checkpointer)
        for event in mongo_graph.stream(state, config=config, stream_mode="values"):
            if "messages" in event and event["messages"]:
                last_message = event["messages"][-1]
                if (
                    hasattr(last_message, "content")
                    and hasattr(last_message, "type")
                    and last_message.type == "ai"
                ):
                    assistant_response = last_message.content

    return assistant_response
