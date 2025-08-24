from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition

from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

from typing_extensions import TypedDict
from typing import List, Annotated

import os
from dotenv import load_dotenv
from system_prompt import system_prompt
from tools import get_weather, web_search, get_location_by_ip
import streamlit as st

load_dotenv()

GROQ_KEY = os.getenv("GROQ_API_KEY")


# create state
class State(TypedDict):
    messages: Annotated[List, add_messages]


# call llm
llm = init_chat_model(
    model_provider="groq",
    model="moonshotai/kimi-k2-instruct",
    api_key=GROQ_KEY,
    temperature=1,
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


# stream graph
def run_graph(messages):
    try:
        langchain_mesages = []
        for msg in messages:
            if msg["role"] == "user":
                langchain_mesages.append(HumanMessage(content=msg["content"]))
            else:
                langchain_mesages.append(AIMessage(content=msg["content"]))

        state = State({"messages": langchain_mesages})
        assistant_response = None

        for event in graph.stream(state, stream_mode="values"):
            if "messages" in event and event["messages"]:
                last_message = event["messages"][-1]
            if (
                hasattr(last_message, "content")
                and hasattr(last_message, "type")
                and last_message.type == "ai"
            ):
                assistant_response = last_message.content

        return assistant_response
    except Exception as e:
        st.error(f"Something went Wrong {e} Please try again later.")
        st.stop()
