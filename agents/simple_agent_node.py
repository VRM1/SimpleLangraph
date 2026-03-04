"""
Simple Agent Node - Example LangGraph agent with tool-calling capability.

This demonstrates the two-phase agent pattern:
1. Phase 1 (optional): Tool calling - LLM decides what tools to use
2. Phase 2: Structured output - LLM formats final response

This is the core pattern for building LangGraph agent nodes.
"""

import logging
from typing import Dict, Any
from langchain_core.messages import AIMessage

from .state import AgentState
from .schema import AgentResponse
from .prompts import AGENT_PROMPT
from tools.tools import get_tools
from config.settings import settings

logger = logging.getLogger(__name__)


def create_simple_agent_node(llm):
    """
    Create the simple agent node function.

    Args:
        llm: Initialized language model (shared across all nodes)

    Returns:
        Node function that takes state and returns state updates
    """

    def simple_agent_node(state: AgentState) -> Dict[str, Any]:
        """
        Process user query and generate response.

        This is a LangGraph node - it receives state and returns updates.

        Two-phase workflow:
        1. OPTIONAL: Tool calling phase (if tools are needed)
        2. Structured output phase (always happens)

        Args:
            state: Current graph state with messages, query, etc.

        Returns:
            Dictionary of state updates to merge into state
        """
        if settings.show_llm_responses:
            logger.info("🤖 SIMPLE AGENT: Processing query...")

        query = state["query"]

        try:
            # ============================================
            # PHASE 1: Tool Calling (Optional)
            # ============================================
            # This phase is where the LLM can call tools autonomously
            # Uncomment to enable tool usage:

            # tools = get_tools()
            # llm_with_tools = llm.bind_tools(tools)
            # tool_response = llm_with_tools.invoke([
            #     ("system", AGENT_PROMPT.format(query=query)),
            #     ("human", query)
            # ])
            #
            # # Check if LLM wants to call tools
            # if hasattr(tool_response, 'tool_calls') and tool_response.tool_calls:
            #     # Process tool calls here
            #     # Execute the tool and append the result to messages
            #     pass

            # ============================================
            # PHASE 2: Structured Output
            # ============================================
            # Force LLM to return data in AgentResponse schema
            llm_with_structure = llm.with_structured_output(AgentResponse)

            # Create prompt with query
            prompt = AGENT_PROMPT.format(query=query)

            # Build messages with conversation history
            # IMPORTANT: Pass the full message history for memory to work!
            messages = [("system", prompt)] + [
                (msg.type, msg.content) for msg in state["messages"]
            ]

            # DEBUG: Show message count
            logger.info(f"🔍 DEBUG: Passing {len(state['messages'])} messages to LLM")

            # Get structured response (with full conversation context)
            response: AgentResponse = llm_with_structure.invoke(messages)

            if settings.show_llm_responses:
                logger.info(f"🤖 SIMPLE AGENT: {response.response[:100]}...")

            # ============================================
            # Update State
            # ============================================
            # Return updates to merge into the graph state
            return {
                "messages": state["messages"] + [
                    AIMessage(content=response.response)
                ],
                "agent_response": response.response,
                "final_response": response.response,  # This is the final answer
                "next_action": response.next_action,  # Controls routing
            }

        except Exception as e:
            logger.error(f"Agent error: {e}", exc_info=True)
            return {
                "error": str(e),
                "next_action": "end"
            }

    return simple_agent_node
