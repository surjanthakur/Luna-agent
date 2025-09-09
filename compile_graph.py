from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import MemorySaver

from langchain.chat_models import init_chat_model
from langchain_core.messages import SystemMessage


from typing_extensions import TypedDict
from typing import List, Annotated

import os
from dotenv import load_dotenv
from system_prompt import system_prompt
from tools import get_weather, web_search, play_song, wikipidia_search
import streamlit as st

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
    stop=None,
)
tools = [get_weather, web_search, play_song, wikipidia_search]
llm_with_tools = llm.bind_tools(tools=tools)


# create a chat route
def chatbot(state: State):
    SYSTEM_PROMPT = system_prompt()
    messages = state["messages"]
    response = llm_with_tools.invoke([SystemMessage(SYSTEM_PROMPT)] + messages)
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
checkpointer = MemorySaver()
graph = graph_builder.compile(checkpointer=checkpointer)
