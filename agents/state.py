"""
State definitions for LangGraph workflow.

State is a TypedDict that gets passed between all nodes in the graph.
Each node can read from state and return updates to it.
"""

from typing import TypedDict, List, Optional, Any, Annotated
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


class AgentState(TypedDict):
    """
    Shared state for all nodes in the graph.

    This is the "memory" that flows through your multi-agent system.
    Each node receives the current state and can update it.
    """

    # Core conversation
    # CRITICAL: Use Annotated[list, add_messages] for memory to work!
    # add_messages is a reducer that tells LangGraph HOW to merge messages
    messages: Annotated[list, add_messages]  # Chat history (HumanMessage, AIMessage, etc.)
    query: str  # Original user query

    # Routing control
    next_action: Optional[str]  # Controls which node to visit next

    # Agent results (customize based on your agents)
    agent_response: Optional[str]  # Response from the agent node

    # Final output
    final_response: Optional[str]  # Final answer to return to user

    # Error handling
    error: Optional[str]  # Error message if something fails

    # Tool results (for when you add tools later)
    tool_results: Optional[List[Any]]  # Results from tool executions
