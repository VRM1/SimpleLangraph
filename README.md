# Simple LangGraph - Beginner's Guide

A minimal, well-documented LangGraph multi-agent system to help you understand the fundamentals and easily extend with your own agents and tools.

## 🎯 What This Is

This is a **distilled version** of the NFL Fantasy Football multi-agent system, simplified to show the core LangGraph patterns without domain-specific complexity.

- ✅ One simple agent (easily add more)
- ✅ Tool-ready infrastructure (add your own tools)
- ✅ Config-driven LLM selection (Ollama/OpenAI)
- ✅ Faithful to production patterns
- ✅ Extensively documented

## 📁 Project Structure

```
simple_langraph/
├── config/
│   ├── config.yml          # LLM provider settings
│   └── settings.py         # Config loader
├── agents/
│   ├── state.py            # Shared state TypedDict
│   ├── schema.py           # Pydantic response schemas
│   ├── prompts.py          # Agent system prompts
│   ├── simple_agent_node.py  # Example agent with tool-calling
│   └── orchestrator.py     # Graph creation, routing, execution
├── tools/
│   └── tools.py            # Example tools (calculator, etc.)
├── utils/
│   └── formatter.py        # Terminal output formatting
├── test_simple.py          # Test runner with example queries
└── README.md               # This file
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install langgraph langchain-ollama langchain-openai pydantic pyyaml python-dotenv
```

### 2. Set Up Environment Variables

Copy the example environment file and add your API keys:

```bash
cp .env.example .env
```

Edit `.env` and add your API key:
```bash
# For OpenAI
OPENAI_API_KEY=your-openai-api-key-here
```

**Note**: The `.env` file is gitignored to keep your API keys safe.

### 3. Configure Your LLM

Edit [`config/config.yml`](config/config.yml):

```yaml
llm:
  provider: "openai"  # or "ollama"

  openai:
    model: "gpt-4o-mini"
    temperature: 0.7

  # OR for local (free) Ollama
  ollama:
    model: "qwen3:14b"  # or llama3, mistral, etc.
    base_url: "http://localhost:11434"
    temperature: 0.7
```

### 4. Run the Test

```bash
cd simple_langraph
python test_simple.py
```

### 4. Interactive Mode

```bash
python agents/orchestrator.py
```

## 🧠 LangGraph Fundamentals

### What is LangGraph?

LangGraph is a framework for building **stateful, multi-agent workflows** using a graph structure:

- **Nodes** = Agents/functions that process data
- **Edges** = Connections between nodes
- **State** = Shared data structure passed between nodes
- **Routing** = Conditional logic to decide which node to visit next

### The Core Pattern

```python
# 1. Define state (TypedDict)
class AgentState(TypedDict):
    messages: List[BaseMessage]
    query: str
    next_action: str
    ...

# 2. Create the graph
workflow = StateGraph(AgentState)

# 3. Add nodes (agents)
workflow.add_node("agent_name", agent_function)

# 4. Add edges (flow)
workflow.add_edge(START, "agent_name")
workflow.add_conditional_edges("agent_name", router_function, {...})

# 5. Compile
graph = workflow.compile(checkpointer=MemorySaver())

# 6. Execute
graph.stream(initial_state, config=config)
```

## 📚 Understanding Each Component

### 1. State ([`agents/state.py`](agents/state.py))

The **state** is a TypedDict that flows through your graph:

```python
class AgentState(TypedDict):
    messages: List[BaseMessage]  # Conversation history
    query: str                   # User's question
    next_action: str             # Controls routing
    final_response: str          # Answer to return
    ...
```

- Each node **reads** from state
- Each node **returns updates** to merge into state
- State persists across the entire workflow

### 2. Nodes ([`agents/simple_agent_node.py`](agents/simple_agent_node.py))

A **node** is a Python function with this signature:

```python
def agent_node(state: AgentState) -> Dict[str, Any]:
    """
    Process state and return updates.

    Args:
        state: Current graph state

    Returns:
        Dictionary of updates to merge into state
    """
    # Your logic here
    return {
        "final_response": "answer",
        "next_action": "end"
    }
```

**Two-Phase Agent Pattern:**

1. **Phase 1 (optional)**: Tool calling - LLM autonomously uses tools
2. **Phase 2**: Structured output - LLM formats response into Pydantic schema

```python
# Phase 1: Tool calling
llm_with_tools = llm.bind_tools([tool1, tool2])
response = llm_with_tools.invoke(messages)

# Phase 2: Structured output
llm_with_structure = llm.with_structured_output(AgentResponse)
final = llm_with_structure.invoke(messages)
```

### 3. Routing ([`agents/orchestrator.py`](agents/orchestrator.py))

The **router function** decides which node to visit next:

```python
def should_continue(state: AgentState) -> str:
    """Examine state and return next node name"""
    next_action = state.get("next_action", "end")

    if next_action == "simple_agent":
        return "simple_agent"
    else:
        return "end"
```

Used in conditional edges:

```python
workflow.add_conditional_edges(
    "simple_agent",      # From this node
    should_continue,     # Use this router
    {
        "simple_agent": "simple_agent",  # Can loop back
        "end": END                       # Or finish
    }
)
```

### 4. Schemas ([`agents/schema.py`](agents/schema.py))

**Pydantic schemas** enforce structured LLM outputs:

```python
class AgentResponse(BaseModel):
    response: str           # The answer
    reasoning: str          # Explanation
    next_action: str        # Where to route next

# Force LLM to return this exact format
llm_with_structure = llm.with_structured_output(AgentResponse)
structured_response = llm_with_structure.invoke(messages)
```

No more parsing LLM text output - you get Python objects!

### 5. Tools ([`tools/tools.py`](tools/tools.py))

**Tools** are functions the LLM can call autonomously:

```python
from langchain_core.tools import tool

@tool
def calculate(expression: str) -> str:
    """Evaluate a mathematical expression."""
    return str(eval(expression))

# Bind tools to LLM
llm_with_tools = llm.bind_tools([calculate, other_tool])

# LLM will automatically call tools when needed
response = llm_with_tools.invoke([("human", "What's 5 + 3?")])
```

### 6. Memory ([`agents/orchestrator.py`](agents/orchestrator.py))

**MemorySaver** enables conversation history:

```python
memory = MemorySaver()
graph = workflow.compile(checkpointer=memory)

# Use thread_id to maintain separate conversations
config = {"configurable": {"thread_id": "user_123"}}
graph.stream(state, config=config)
```

## 🔧 How to Extend

### Adding a New Agent Node

1. **Create the node file** (`agents/my_new_node.py`):

```python
from .state import AgentState
from .schema import MyNodeResponse

def create_my_node(llm):
    def my_node(state: AgentState) -> Dict[str, Any]:
        # Your logic here
        llm_with_structure = llm.with_structured_output(MyNodeResponse)
        response = llm_with_structure.invoke([...])

        return {
            "my_data": response.data,
            "next_action": "end"
        }
    return my_node
```

2. **Add response schema** (`agents/schema.py`):

```python
class MyNodeResponse(BaseModel):
    data: str
    next_action: str = "end"
```

3. **Update state** (`agents/state.py`):

```python
class AgentState(TypedDict):
    # ... existing fields ...
    my_data: Optional[str]  # Add your field
```

4. **Wire into graph** (`agents/orchestrator.py`):

```python
from .my_new_node import create_my_node

def create_simple_graph():
    llm = initialize_llm()

    # Create nodes
    simple_agent = create_simple_agent_node(llm)
    my_node = create_my_node(llm)  # Add this

    workflow = StateGraph(AgentState)
    workflow.add_node("simple_agent", simple_agent)
    workflow.add_node("my_node", my_node)  # Add this

    # Update routing
    workflow.add_conditional_edges(
        "simple_agent",
        should_continue,
        {
            "simple_agent": "simple_agent",
            "my_node": "my_node",  # Add this
            "end": END
        }
    )

    # ... rest of graph setup
```

5. **Update router** (`should_continue` function):

```python
def should_continue(state: AgentState) -> str:
    next_action = state.get("next_action", "end")

    if next_action == "simple_agent":
        return "simple_agent"
    elif next_action == "my_node":  # Add this
        return "my_node"
    else:
        return "end"
```

### Adding Tools

1. **Define tool** in [`tools/tools.py`](tools/tools.py):

```python
@tool
def my_custom_tool(input: str) -> str:
    """Description of what this tool does."""
    # Your implementation
    return result

# Add to AVAILABLE_TOOLS list
AVAILABLE_TOOLS = [
    calculate,
    reverse_string,
    my_custom_tool,  # Add this
]
```

2. **Enable tools in agent** ([`agents/simple_agent_node.py`](agents/simple_agent_node.py)):

Uncomment the Phase 1 section:

```python
# Phase 1: Tool calling
tools = get_tools()
llm_with_tools = llm.bind_tools(tools)
response = llm_with_tools.invoke([...])

# Check if tools were called
if hasattr(response, 'tool_calls') and response.tool_calls:
    # Process tool calls
    for tool_call in response.tool_calls:
        # Execute the tool
        # See player_stats_node.py in main codebase for full example
```

### Adding a New LLM Provider

1. **Update config** ([`config/config.yml`](config/config.yml)):

```yaml
llm:
  provider: "my_provider"

  my_provider:
    model: "model-name"
    api_key_env: "MY_API_KEY"
    temperature: 0.7
```

2. **Update settings** ([`config/settings.py`](config/settings.py)):

```python
@property
def my_provider_model(self) -> str:
    return self._config["llm"]["my_provider"]["model"]
```

3. **Update LLM initialization** ([`agents/orchestrator.py`](agents/orchestrator.py)):

```python
def initialize_llm():
    provider = settings.llm_provider.lower()

    if provider == "ollama":
        # ... existing ...
    elif provider == "openai":
        # ... existing ...
    elif provider == "my_provider":  # Add this
        from langchain_my_provider import ChatMyProvider
        llm = ChatMyProvider(
            model=settings.my_provider_model,
            # ... other settings ...
        )
        return llm
```

## 🎓 Learning Path

### Beginner
1. Run [`test_simple.py`](test_simple.py) to see it work
2. Read [`agents/state.py`](agents/state.py) - understand the state structure
3. Read [`agents/simple_agent_node.py`](agents/simple_agent_node.py) - see how nodes work
4. Read [`agents/orchestrator.py`](agents/orchestrator.py) - understand graph creation

### Intermediate
1. Modify [`agents/prompts.py`](agents/prompts.py) to change agent behavior
2. Add a custom tool in [`tools/tools.py`](tools/tools.py)
3. Enable tool calling in [`agents/simple_agent_node.py`](agents/simple_agent_node.py)
4. Create a second agent node following the pattern

### Advanced
1. Study the parent NFL codebase to see multi-agent coordination
2. Implement a planner/orchestrator pattern with multiple specialized agents
3. Add custom routing logic with complex state conditions
4. Integrate external data sources and APIs

## 🔍 Key Differences from NFL System

| Feature | NFL System | Simple System |
|---------|-----------|---------------|
| **Agents** | 3 specialized (Planner, PlayerStats, Defense) | 1 general agent |
| **Data** | Pre-loaded NFL DataFrames | No data dependencies |
| **Tools** | Pandas query execution, fuzzy matching | Simple examples (calculator, etc.) |
| **Routing** | Complex multi-step (planning → specialized → synthesis) | Simple single-agent flow |
| **State** | 15+ fields tracking plan, data, nodes called | 8 essential fields |
| **Purpose** | Fantasy football analysis | Learning LangGraph fundamentals |

## 🐛 Troubleshooting

### "No module named 'langgraph'"
```bash
pip install langgraph langchain-ollama langchain-openai
```

### "Connection refused" (Ollama)
Make sure Ollama is running:
```bash
ollama serve
```

### "OpenAI API key not found"
Export your API key:
```bash
export OPENAI_API_KEY="sk-..."
```

Or use Ollama (local, free):
```yaml
llm:
  provider: "ollama"
```

### Agent returns empty response
- Check [`config/config.yml`](config/config.yml) - ensure provider is set correctly
- Check logs with `logging: level: "DEBUG"`
- Try a simpler query first

## 📖 Additional Resources

- **LangGraph Docs**: https://langchain-ai.github.io/langgraph/
- **LangChain Docs**: https://python.langchain.com/docs/
- **Parent NFL System**: See `../CLAUDE.md` for full multi-agent example

## 🤝 Contributing

This is a learning template - feel free to modify and extend!

Common extensions:
- Add more specialized agents
- Integrate with databases
- Add web search capabilities
- Build a chat interface (Streamlit/Gradio)
- Add streaming responses
- Implement agent memory/long-term storage

## 📝 License

Same as parent project (check repository root).

---

**Happy Learning!** 🚀

Start simple, understand the patterns, then extend with your own agents and tools.
