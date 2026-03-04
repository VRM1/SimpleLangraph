"""
Pydantic schemas for structured LLM outputs.

These schemas enforce that the LLM returns data in a specific format.
Use with llm.with_structured_output(Schema) to guarantee parseable responses.
"""

from pydantic import BaseModel, Field
from typing import Optional


class AgentResponse(BaseModel):
    """
    Structured response from the agent node.

    The LLM will be forced to return data in this exact format.
    """

    response: str = Field(
        description="The agent's answer to the user's question"
    )

    reasoning: Optional[str] = Field(
        default=None,
        description="Brief explanation of how the agent arrived at this answer"
    )

    confidence: Optional[str] = Field(
        default=None,
        description="Confidence level: 'high', 'medium', or 'low'"
    )

    next_action: str = Field(
        default="end",
        description="Next node to visit: 'end' to finish, or another node name to continue"
    )


class ToolCallResponse(BaseModel):
    """
    Response after calling tools (for future use when you add tools).

    This shows the pattern for multi-phase agent workflows:
    Phase 1: Tool calling (this schema)
    Phase 2: Final structured output (AgentResponse)
    """

    tool_used: Optional[str] = Field(
        default=None,
        description="Name of the tool that was called"
    )

    tool_result: Optional[str] = Field(
        default=None,
        description="Result returned by the tool"
    )

    needs_more_tools: bool = Field(
        default=False,
        description="Whether more tools need to be called"
    )
