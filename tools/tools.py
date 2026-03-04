"""
Tools for LangGraph agents.

Tools are functions that the LLM can call to perform actions or retrieve information.
They are bound to the LLM using llm.bind_tools([tool1, tool2, ...])

This is a placeholder - add your own tools here as you extend the system!
"""

from langchain_core.tools import tool
from typing import Optional


# Example tool: Simple calculator
@tool
def calculate(expression: str) -> str:
    """
    Evaluate a mathematical expression.

    Args:
        expression: A mathematical expression as a string (e.g., "2 + 2", "10 * 5")

    Returns:
        The result of the calculation as a string

    Example:
        calculate("5 + 3") -> "8"
    """
    try:
        # Safe evaluation (be careful with eval in production!)
        result = eval(expression, {"__builtins__": {}}, {})
        return str(result)
    except Exception as e:
        return f"Error calculating: {str(e)}"


# Example tool: String manipulation
@tool
def reverse_string(text: str) -> str:
    """
    Reverse a string.

    Args:
        text: The string to reverse

    Returns:
        The reversed string

    Example:
        reverse_string("hello") -> "olleh"
    """
    return text[::-1]


# Example tool: Information lookup (placeholder)
@tool
def lookup_information(query: str) -> str:
    """
    Look up information (placeholder - replace with actual data source).

    Args:
        query: What to look up

    Returns:
        Information about the query

    Example:
        lookup_information("Python") -> "Python is a programming language..."
    """
    # In a real system, this would query a database, API, or knowledge base
    return f"Placeholder result for: {query}"


# List of all available tools
# Add new tools to this list when you create them
AVAILABLE_TOOLS = [
    calculate,
    reverse_string,
    lookup_information,
]


def get_tools():
    """
    Get all available tools.

    Returns:
        List of tool functions that can be bound to an LLM
    """
    return AVAILABLE_TOOLS


def get_tool_descriptions() -> str:
    """
    Get human-readable descriptions of all tools.

    Useful for injecting into prompts.

    Returns:
        Formatted string describing all available tools
    """
    descriptions = []
    for tool in AVAILABLE_TOOLS:
        descriptions.append(f"- {tool.name}: {tool.description}")
    return "\n".join(descriptions)
