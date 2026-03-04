#!/usr/bin/env python3
"""
Interactive test script for the LangGraph system with memory support.

This script demonstrates:
1. Basic question-answering
2. Conversation memory (follow-up questions)
3. Multi-turn conversations within the same thread

Usage:
    python test_simple.py
"""

import sys
import logging
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from agents.orchestrator import create_simple_graph, run_query
from config.settings import settings

# Setup logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format='%(message)s'
)

# Suppress noisy HTTP logs
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("openai").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


def test_basic_qa(graph):
    """Test basic question-answering"""
    print("=" * 70)
    print("TEST 1: Basic Question-Answering")
    print("=" * 70)
    print()

    queries = [
        "What is the capital of France?",
        "Explain what LangGraph is in simple terms",
    ]

    for i, query in enumerate(queries, 1):
        print(f"\n📝 Question {i}: {query}\n")
        try:
            run_query(graph, query, thread_id=f"basic_test_{i}")
            print("✅ Answered\n")
        except Exception as e:
            print(f"❌ Error: {e}\n")
            logger.error(f"Query failed", exc_info=True)


def test_conversation_memory(graph):
    """Test conversation memory with follow-up questions"""
    print("\n" + "=" * 70)
    print("TEST 2: Conversation Memory (Follow-up Questions)")
    print("=" * 70)
    print()

    # Use same thread_id to maintain conversation history
    thread_id = "memory_test"

    conversation = [
        "What is Python?",
        "What are its main benefits?",  # Follow-up - should remember we're talking about Python
        "Can you give me an example use case?",  # Another follow-up
    ]

    for i, query in enumerate(conversation, 1):
        print(f"\n📝 Turn {i}: {query}\n")
        try:
            run_query(graph, query, thread_id=thread_id)
            print("✅ Answered\n")
        except Exception as e:
            print(f"❌ Error: {e}\n")
            logger.error(f"Query failed", exc_info=True)


def interactive_mode(graph):
    """Interactive Q&A mode with memory"""
    print("\n" + "=" * 70)
    print("INTERACTIVE MODE (Type 'exit' or 'quit' to stop)")
    print("=" * 70)
    print()
    print("💡 Tip: All questions in this session share memory!")
    print("   Try asking follow-up questions like 'tell me more' or 'what about X?'\n")

    thread_id = "interactive_session"
    question_num = 1

    while True:
        try:
            user_input = input(f"\n🤔 Question {question_num}: ")

            if user_input.lower().strip() in ['exit', 'quit', 'q', '']:
                print("\n👋 Goodbye!\n")
                break

            print()  # Blank line before answer
            run_query(graph, user_input, thread_id=thread_id)
            question_num += 1

        except (KeyboardInterrupt, EOFError):
            print("\n\n👋 Goodbye!\n")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}\n")
            logger.error("Interactive query failed", exc_info=True)


def main():
    print("=" * 70)
    print("🤖 SIMPLE LANGRAPH SYSTEM - INTERACTIVE TEST")
    print("=" * 70)
    print()

    # Create the graph (with memory enabled)
    print("🔧 Creating LangGraph workflow with memory...")
    graph = create_simple_graph()
    print("✅ Graph ready with conversation memory enabled\n")

    # Run tests
    test_basic_qa(graph)
    test_conversation_memory(graph)

    # Interactive mode
    print("\n" + "=" * 70)
    print("TESTS COMPLETE - Starting Interactive Mode")
    print("=" * 70)
    interactive_mode(graph)


if __name__ == "__main__":
    main()
