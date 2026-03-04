"""
LangGraph Orchestrator - Creates and manages the multi-agent workflow.

This is the heart of your LangGraph system:
1. Initializes the LLM
2. Creates the graph structure (nodes + edges)
3. Defines routing logic
4. Executes queries
"""

import logging
import os
from pathlib import Path
from dotenv import load_dotenv
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage

from .state import AgentState
from .simple_agent_node import create_simple_agent_node
from config.settings import settings
from utils.formatter import format_final_response, format_error

# Load environment variables from .env file
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

logger = logging.getLogger(__name__)


def initialize_llm():
    """
    Initialize the LLM based on config.yml settings.

    Returns:
        Initialized LLM (ChatOllama or ChatOpenAI)
    """
    provider = settings.llm_provider.lower()

    logger.info(f"🚀 Initializing {provider.upper()} LLM...")

    if provider == "ollama":
        llm = ChatOllama(
            model=settings.ollama_model,
            base_url=settings.ollama_base_url,
            temperature=settings.ollama_temperature,
        )
        logger.info(f"✅ Ollama LLM ({settings.ollama_model}) ready")
        return llm

    elif provider == "openai":
        api_key = os.environ.get(settings.openai_api_key_env)
        if not api_key:
            raise ValueError(f"OpenAI API key not found: {settings.openai_api_key_env}")

        llm = ChatOpenAI(
            model=settings.openai_model,
            openai_api_key=api_key,
            temperature=settings.openai_temperature,
        )
        logger.info(f"✅ OpenAI LLM ({settings.openai_model}) ready")
        return llm

    else:
        raise ValueError(f"Unsupported LLM provider: {provider}")


def should_continue(state: AgentState) -> str:
    """
    Router function - determines which node to visit next.

    This is called by conditional_edges to decide the graph flow.

    Args:
        state: Current graph state

    Returns:
        Name of next node to visit: "simple_agent", "end", etc.
    """
    next_action = state.get("next_action", "end")

    if settings.show_routing:
        logger.info(f"🔀 Router: next_action = {next_action}")

    # Route based on next_action
    if next_action == "simple_agent":
        return "simple_agent"
    elif next_action == "end":
        return "end"
    else:
        # Default: end the workflow
        return "end"


def create_simple_graph():
    """
    Create and compile the LangGraph workflow.

    This is where you define your multi-agent system structure:
    - Add nodes (agents)
    - Add edges (connections between nodes)
    - Add conditional routing

    Returns:
        Compiled LangGraph workflow
    """
    logger.info("🔧 Creating LangGraph workflow...")

    # ============================================
    # 1. Initialize shared LLM
    # ============================================
    # One LLM instance is shared by all nodes
    llm = initialize_llm()

    # ============================================
    # 2. Create node functions
    # ============================================
    # Each node is a Python function: state -> state_updates
    simple_agent = create_simple_agent_node(llm)

    # ============================================
    # 3. Create the StateGraph
    # ============================================
    # StateGraph manages state flow between nodes
    workflow = StateGraph(AgentState)

    # ============================================
    # 4. Add nodes to the graph
    # ============================================
    # Nodes are the agents/functions in your system
    workflow.add_node("simple_agent", simple_agent)

    # ============================================
    # 5. Add edges (define the flow)
    # ============================================

    # Static edge: Always start at simple_agent
    workflow.add_edge(START, "simple_agent")

    # Conditional edge: Route based on state
    workflow.add_conditional_edges(
        "simple_agent",  # From this node
        should_continue,  # Use this function to decide where to go
        {
            "simple_agent": "simple_agent",  # Loop back if needed
            "end": END  # Finish the workflow
        }
    )

    # ============================================
    # 6. Compile the graph with memory
    # ============================================
    # MemorySaver enables conversation history across runs
    memory = MemorySaver()
    graph = workflow.compile(checkpointer=memory)

    logger.info("✅ LangGraph workflow created successfully")

    return graph


def run_query(graph, query: str, thread_id: str = "default") -> str:
    """
    Execute a query through the LangGraph workflow.

    Args:
        graph: Compiled LangGraph workflow
        query: User's question
        thread_id: Thread identifier for conversation memory

    Returns:
        Final response string
    """
    # Config for memory/checkpointing
    config = {"configurable": {"thread_id": thread_id}}

    logger.info(f"🏈 Processing query: {query[:100]}...")

    try:
        # ============================================
        # Prepare input (only the new message)
        # ============================================
        # LangGraph will automatically load previous state from checkpointer
        # We just need to provide the NEW user message
        input_state = {
            "messages": [HumanMessage(content=query)],
            "query": query,
        }

        # ============================================
        # Stream execution
        # ============================================
        # graph.stream() automatically:
        # 1. Loads previous state for this thread_id (if exists)
        # 2. Merges our input_state into it
        # 3. Executes the graph
        # 4. Saves the new state
        final_response = None
        for event in graph.stream(input_state, config=config, stream_mode="updates"):
            for node_name, output in event.items():
                if settings.show_node_completion:
                    logger.info(f"✓ Node '{node_name}' completed")

                # Capture final response
                if output.get("final_response"):
                    final_response = output["final_response"]

        # ============================================
        # Return result
        # ============================================
        if final_response:
            format_final_response(final_response)
            return final_response
        else:
            # Check for errors
            final_state = graph.get_state(config)
            error = final_state.values.get("error")
            if error:
                format_error(error)
                return f"Error: {error}"
            else:
                error_msg = "No response generated. Please try rephrasing your query."
                format_error(error_msg)
                return error_msg

    except Exception as e:
        logger.error(f"Execution failed: {e}", exc_info=True)
        error_msg = f"System error: {str(e)}"
        format_error(error_msg)
        return error_msg


def main():
    """Standalone test runner (for quick testing)"""
    print("=" * 60)
    print("Simple LangGraph System")
    print("=" * 60)

    # Create graph
    graph = create_simple_graph()

    print("\nReady! Ask questions (type 'exit' to quit):\n")

    # Interactive loop
    while True:
        user_input = input("Your question: ")
        if user_input.lower() in ['exit', 'quit']:
            break

        response = run_query(graph, user_input, "interactive_session")
        print()


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.INFO, format='%(message)s')

    # Suppress noisy HTTP logs
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("openai").setLevel(logging.WARNING)

    main()
