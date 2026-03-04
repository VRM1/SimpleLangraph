# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A minimal LangGraph multi-agent system designed as a learning template. Uses a single `simple_agent` node with conversation memory, structured Pydantic outputs, and optional tool-calling. Supports OpenAI and Ollama as LLM backends.

## Commands

```bash
# Install dependencies (uses uv)
uv sync

# Run tests and enter interactive mode
python test_simple.py

# Run interactive mode only
python agents/orchestrator.py

# Lint
ruff check .

# Format
black .
```

**Note:** Run scripts from the project root. `test_simple.py` adds the project root to `sys.path`, so imports work without installing the package.

## Architecture

### Data Flow

```
User query → orchestrator.run_query()
  → graph.stream(input_state, config)
    → START → simple_agent node → should_continue() router → END
```

### Key Files

| File | Role |
|------|------|
| `agents/state.py` | `AgentState` TypedDict — the shared state passed between all nodes. `messages` uses `Annotated[list, add_messages]` reducer for memory. |
| `agents/schema.py` | Pydantic schemas for structured LLM outputs. `AgentResponse.next_action` controls routing. |
| `agents/prompts.py` | System prompts for agents. `AGENT_PROMPT` takes `{query}` as a format variable. |
| `agents/simple_agent_node.py` | The sole agent node. Two-phase pattern: optional tool-calling (commented out) → structured output via `llm.with_structured_output(AgentResponse)`. |
| `agents/orchestrator.py` | Graph creation (`create_simple_graph`), LLM initialization (`initialize_llm`), routing (`should_continue`), and query execution (`run_query`). Entry point for interactive mode. |
| `config/config.yml` | LLM provider selection (`openai` or `ollama`), model names, temperatures, and logging flags. |
| `config/settings.py` | Singleton `settings` object that loads `config.yml`. All config access goes through here. |
| `tools/tools.py` | `@tool`-decorated functions + `AVAILABLE_TOOLS` list + `get_tools()`. Tool-calling is currently disabled in `simple_agent_node.py` (commented out). |
| `utils/formatter.py` | Terminal output formatting helpers. |

### Routing Pattern

`AgentResponse.next_action` (from the LLM's structured output) drives the `should_continue` router in `orchestrator.py`. The agent sets `"end"` to finish or `"simple_agent"` to loop back. When adding new nodes, update both the router mapping and `workflow.add_conditional_edges`.

### Memory / Thread IDs

The graph is compiled with `MemorySaver()`. Conversation history persists per `thread_id`. Pass different `thread_id` values to `run_query()` for isolated conversation sessions.

## Configuration

LLM provider is set in `config/config.yml`. OpenAI requires `OPENAI_API_KEY` in a `.env` file at the project root (loaded via `python-dotenv`). Ollama requires a running local server at the configured `base_url`.

Logging verbosity is controlled by `config.yml` flags: `show_routing`, `show_node_completion`, `show_llm_responses`.

## Extending the System

To add a new agent node:
1. Create `agents/my_node.py` following the `create_simple_agent_node` factory pattern
2. Add a response schema to `agents/schema.py`
3. Add any new state fields to `AgentState` in `agents/state.py`
4. Register the node and update conditional edges in `agents/orchestrator.py`
5. Add the new `next_action` value to `should_continue`

To enable tool-calling, uncomment Phase 1 in `agents/simple_agent_node.py` and add tools to `AVAILABLE_TOOLS` in `tools/tools.py`.
