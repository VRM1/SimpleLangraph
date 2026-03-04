"""
Output formatting utilities for terminal display.

Provides color-coded output for better readability.
"""

# ANSI color codes
GREEN = "\033[92m"
RED = "\033[91m"
BLUE = "\033[94m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
BOLD = "\033[1m"
RESET = "\033[0m"


def format_final_response(response: str):
    """
    Format and print the final response with green color.

    Args:
        response: The final answer to display
    """
    print(f"\n{GREEN}{BOLD}{'=' * 60}{RESET}")
    print(f"{GREEN}{BOLD}FINAL ANSWER{RESET}")
    print(f"{GREEN}{BOLD}{'=' * 60}{RESET}")
    print(f"{GREEN}{response}{RESET}")
    print(f"{GREEN}{BOLD}{'=' * 60}{RESET}\n")


def format_error(error: str):
    """
    Format and print an error message with red color.

    Args:
        error: The error message to display
    """
    print(f"\n{RED}{BOLD}ERROR:{RESET} {RED}{error}{RESET}\n")


def format_agent_output(agent_name: str, message: str, icon: str = "🤖"):
    """
    Format and print agent output with icon and color.

    Args:
        agent_name: Name of the agent
        message: The agent's message
        icon: Icon to display (default: robot emoji)
    """
    print(f"\n{BLUE}{BOLD}{icon} {agent_name.upper()}{RESET}")
    print(f"{CYAN}{message}{RESET}\n")


def format_tool_call(tool_name: str, args: dict):
    """
    Format and print a tool call.

    Args:
        tool_name: Name of the tool being called
        args: Arguments passed to the tool
    """
    print(f"{YELLOW}🔧 Calling tool: {tool_name}{RESET}")
    print(f"{YELLOW}   Args: {args}{RESET}")


def format_section(title: str):
    """
    Format and print a section header.

    Args:
        title: Section title
    """
    print(f"\n{BOLD}{'─' * 60}{RESET}")
    print(f"{BOLD}{title}{RESET}")
    print(f"{BOLD}{'─' * 60}{RESET}\n")
