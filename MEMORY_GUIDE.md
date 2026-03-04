# LangGraph Memory Best Practices Guide

## 🧠 How Memory Works in LangGraph

LangGraph uses **Checkpointers** to save state between invocations. This enables:
- Conversation history
- Multi-turn dialogues
- Resumable workflows
- Time-travel debugging

## 📚 Memory Options (Choose Based on Your Needs)

### 1. **MemorySaver** (Development) ✅ CURRENT

**Use for:** Development, testing, single-user CLI

```python
from langgraph.checkpoint.memory import MemorySaver

memory = MemorySaver()
graph = workflow.compile(checkpointer=memory)
```

**Pros:**
- Zero setup
- Fast (in-memory)
- Perfect for learning/testing

**Cons:**
- Lost on restart
- Not production-ready

---

### 2. **SqliteSaver** (Production - Single Server)

**Use for:** Production single-server apps, persistent CLI tools

```python
from langgraph.checkpoint.sqlite import SqliteSaver

# Create checkpointer (persists to file)
memory = SqliteSaver.from_conn_string("checkpoints.db")
graph = workflow.compile(checkpointer=memory)
```

**Setup:**
```bash
pip install langgraph-checkpoint-sqlite
```

**Pros:**
- Persists across restarts
- File-based (portable)
- No external dependencies

**Cons:**
- File locking with concurrent access
- Not ideal for distributed systems

**Example: Upgrading from MemorySaver**

```python
# agents/orchestrator.py

from langgraph.checkpoint.sqlite import SqliteSaver
from pathlib import Path

def create_simple_graph():
    llm = initialize_llm()
    simple_agent = create_simple_agent_node(llm)

    workflow = StateGraph(AgentState)
    workflow.add_node("simple_agent", simple_agent)
    workflow.add_edge(START, "simple_agent")
    workflow.add_conditional_edges("simple_agent", should_continue, {...})

    # Use SQLite for persistence
    db_path = Path(__file__).parent.parent / "checkpoints.db"
    memory = SqliteSaver.from_conn_string(str(db_path))

    graph = workflow.compile(checkpointer=memory)
    return graph
```

---

### 3. **PostgresSaver** (Production - Multi-Server)

**Use for:** Production web apps, distributed systems

```python
from langgraph.checkpoint.postgres import PostgresSaver
import os

# Get from environment
conn_string = os.environ.get("POSTGRES_CONNECTION_STRING")
memory = PostgresSaver.from_conn_string(conn_string)
graph = workflow.compile(checkpointer=memory)
```

**Setup:**
```bash
pip install langgraph-checkpoint-postgres psycopg2-binary

# Set environment variable
export POSTGRES_CONNECTION_STRING="postgresql://user:pass@host:5432/dbname"
```

**Database Setup:**
```sql
-- Run this in your PostgreSQL database
CREATE TABLE checkpoints (
    thread_id TEXT,
    checkpoint_id TEXT,
    parent_id TEXT,
    checkpoint JSONB,
    metadata JSONB,
    PRIMARY KEY (thread_id, checkpoint_id)
);

CREATE INDEX idx_thread_id ON checkpoints(thread_id);
```

**Pros:**
- Scales to multiple servers
- Production-grade reliability
- Shared state across processes

**Cons:**
- Requires PostgreSQL setup

---

### 4. **RedisSaver** (High-Performance)

**Use for:** High-traffic chat apps, real-time systems

```python
from langgraph.checkpoint.redis import RedisSaver

memory = RedisSaver.from_conn_info(
    host=os.environ.get("REDIS_HOST", "localhost"),
    port=int(os.environ.get("REDIS_PORT", 6379)),
    db=0
)
graph = workflow.compile(checkpointer=memory)
```

**Setup:**
```bash
pip install langgraph-checkpoint-redis redis

# Start Redis (Docker)
docker run -d -p 6379:6379 redis:latest
```

**Pros:**
- Extremely fast
- TTL support (auto-expire old conversations)
- Horizontal scaling

**Cons:**
- Requires Redis setup

---

## 🎯 **Recommended Production Pattern**

### **Environment-Based Configuration**

Add to `config.yml`:

```yaml
memory:
  provider: "sqlite"  # "memory", "sqlite", "postgres", "redis"

  sqlite:
    db_path: "checkpoints.db"

  postgres:
    connection_string_env: "POSTGRES_CONNECTION_STRING"

  redis:
    host: "localhost"
    port: 6379
    db: 0
```

Update `settings.py`:

```python
@property
def memory_provider(self) -> str:
    return self._config.get("memory", {}).get("provider", "memory")

@property
def sqlite_db_path(self) -> str:
    return self._config.get("memory", {}).get("sqlite", {}).get("db_path", "checkpoints.db")
```

Update `orchestrator.py`:

```python
def create_simple_graph():
    llm = initialize_llm()
    simple_agent = create_simple_agent_node(llm)

    workflow = StateGraph(AgentState)
    workflow.add_node("simple_agent", simple_agent)
    workflow.add_edge(START, "simple_agent")
    workflow.add_conditional_edges("simple_agent", should_continue, {...})

    # Initialize memory based on config
    memory = initialize_memory()

    graph = workflow.compile(checkpointer=memory)
    return graph


def initialize_memory():
    """Initialize memory provider based on config"""
    provider = settings.memory_provider.lower()

    if provider == "memory":
        from langgraph.checkpoint.memory import MemorySaver
        logger.info("Using in-memory checkpointer (development mode)")
        return MemorySaver()

    elif provider == "sqlite":
        from langgraph.checkpoint.sqlite import SqliteSaver
        db_path = Path(__file__).parent.parent / settings.sqlite_db_path
        logger.info(f"Using SQLite checkpointer: {db_path}")
        return SqliteSaver.from_conn_string(str(db_path))

    elif provider == "postgres":
        from langgraph.checkpoint.postgres import PostgresSaver
        conn_string = os.environ.get(settings.postgres_connection_string_env)
        logger.info("Using PostgreSQL checkpointer")
        return PostgresSaver.from_conn_string(conn_string)

    elif provider == "redis":
        from langgraph.checkpoint.redis import RedisSaver
        logger.info("Using Redis checkpointer")
        return RedisSaver.from_conn_info(
            host=settings.redis_host,
            port=settings.redis_port,
            db=settings.redis_db
        )

    else:
        raise ValueError(f"Unsupported memory provider: {provider}")
```

---

## 🔑 **Key Concepts**

### **thread_id** - Conversation Isolation

```python
# Each conversation gets unique thread_id
config = {"configurable": {"thread_id": user_id}}
graph.stream(initial_state, config=config)
```

- Same `thread_id` = continues conversation
- Different `thread_id` = separate conversation
- Use user_id, session_id, or conversation_id

### **messages** - Conversation History

```python
class AgentState(TypedDict):
    messages: List[BaseMessage]  # Accumulates conversation
```

- LangGraph automatically saves `messages` after each node
- `messages` list grows with each turn
- LLM sees full history for context

### **Checkpointing** - State Snapshots

- LangGraph saves state after **every node execution**
- You can "rewind" to any previous checkpoint
- Enables time-travel debugging

---

## 🧪 **Testing Memory**

### Test 1: Same thread_id (should remember)

```python
# First query
run_query(graph, "My name is Alice", thread_id="user_123")

# Follow-up (should remember Alice)
run_query(graph, "What's my name?", thread_id="user_123")
# Expected: "Your name is Alice"
```

### Test 2: Different thread_id (should NOT remember)

```python
# First query
run_query(graph, "My name is Bob", thread_id="user_456")

# Different thread (should NOT know Bob)
run_query(graph, "What's my name?", thread_id="user_789")
# Expected: "I don't know your name"
```

---

## 📊 **Decision Matrix**

| Scenario | Recommended | Why |
|----------|-------------|-----|
| **Learning/Development** | MemorySaver | Simple, no setup |
| **CLI tool (single user)** | SqliteSaver | Persists, portable |
| **Web app (single server)** | SqliteSaver or PostgresSaver | Depends on scale |
| **Web app (multi-server)** | PostgresSaver or RedisSaver | Shared state |
| **Chat app (high traffic)** | RedisSaver | Fast, TTL support |
| **Enterprise system** | PostgresSaver | Reliability, backups |

---

## 🚀 **Quick Upgrade Path**

1. **Start with MemorySaver** (development)
2. **Upgrade to SqliteSaver** (first deployment)
3. **Scale to PostgresSaver** (when you need multiple servers)
4. **Optimize with RedisSaver** (when performance matters)

---

## 💡 **Pro Tips**

1. **Always use thread_id** - Even with MemorySaver, practice using thread_id
2. **Clean up old conversations** - Implement TTL or cleanup jobs
3. **Monitor checkpoint size** - Large conversations can slow down
4. **Test memory isolation** - Ensure thread_ids don't leak data
5. **Version your state** - Add version field to handle schema changes

---

## 🔗 **Further Reading**

- [LangGraph Checkpointing Docs](https://langchain-ai.github.io/langgraph/concepts/persistence/)
- [Memory & State Management](https://langchain-ai.github.io/langgraph/concepts/low_level/)
- [Production Deployment Guide](https://langchain-ai.github.io/langgraph/deployment/)
