#!/usr/bin/env python3
"""
Test script from internet to verify LangGraph memory works correctly.
This is the canonical example from LangGraph docs.
"""

from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
env_path = Path(__file__).parent / ".env"
load_dotenv(env_path)

# 1. Define State with message history
class State(TypedDict):
    messages: Annotated[list, add_messages]

# 2. Define the node (model)
llm = ChatOpenAI(model="gpt-4o-mini")
def chatbot(state: State):
    return {"messages": [llm.invoke(state["messages"])]}

# 3. Build the Graph
graph_builder = StateGraph(State)
graph_builder.add_node("chatbot", chatbot)
graph_builder.add_edge(START, "chatbot")
graph_builder.add_edge("chatbot", END)

# 4. Add Checkpointer for Memory
memory = MemorySaver()
graph = graph_builder.compile(checkpointer=memory)

# 5. Run with thread_id for persistence
config = {"configurable": {"thread_id": "1"}}

print("=" * 70)
print("TESTING LANGGRAPH MEMORY (Canonical Example)")
print("=" * 70)
print()

# Interaction 1
print("👤 User: Hi, I'm Bob.")
user_input1 = "Hi, I'm Bob."
response1 = graph.invoke({"messages": [HumanMessage(content=user_input1)]}, config)
print(f"🤖 AI: {response1['messages'][-1].content}")
print()

# Interaction 2 (remembers name)
print("👤 User: What is my name?")
user_input2 = "What is my name?"
response2 = graph.invoke({"messages": [HumanMessage(content=user_input2)]}, config)
print(f"🤖 AI: {response2['messages'][-1].content}")
print()

print("=" * 70)
print("✅ If the AI said 'Bob', memory is working!")
print("=" * 70)
