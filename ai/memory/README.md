# 🧠 Memory System Guide

> **Persistent Context & Knowledge Sharing**: How agents store, retrieve, and coordinate through shared memory.

**📚 Cross-References**: [Documentation Index](../../docs/INDEX.md) | [Agent Development Guide](../../docs/AGENT_DEVELOPMENT.md) | [Tool Reference](../../docs/TOOLS.md#memory-context-tools)

---

## 🎯 Memory System Overview

The Fresh memory system enables **persistent context sharing** between agents across sessions and workflows. Memory is essential for:

- **Agent Coordination**: Share context between specialized agents
- **Goal Persistence**: Maintain objectives across multiple sessions  
- **Progress Tracking**: Record decisions, completed tasks, and learnings
- **Context Handoffs**: Transfer knowledge between agent roles

### Architecture Components

- **[Memory Store](store.py)** - Abstract storage interface with in-memory and Firestore backends
- **[Memory Tools](../tools/memory_tools.py)** - Agent interfaces for reading/writing memory
- **[Activity Monitoring](../monitor/activity.py)** - Track memory operations for debugging

---

## 🛠️ Memory Tools

### WriteMemory
**Purpose**: Store knowledge and context for other agents  
**Documentation**: [Tool Reference](../../docs/TOOLS.md#writememory)

```python path=/Users/am/Code/Fresh/ai/tools/memory_tools.py start=33
WriteMemory(
    content="Goal: Implement MCP browser integration",
    tags=["feature", "mcp", "browser"]
).run()
```

### ReadMemoryContext  
**Purpose**: Retrieve relevant stored context  
**Documentation**: [Tool Reference](../../docs/TOOLS.md#readmemorycontext)

```python path=/Users/am/Code/Fresh/ai/tools/memory_tools.py start=63
context = ReadMemoryContext(
    tags=["feature", "mcp"], 
    limit=10
).run()
```

---

## 🎨 Memory Usage Patterns

### Goal Setting & Planning
```python path=null start=null
# Strategic planning
WriteMemory(
    content="Strategic goal: Enhance agent MCP capabilities",
    tags=["goal", "strategic", "mcp"]
)

# Task breakdown  
WriteMemory(
    content="Next: Create MCP client tools for browser automation",
    tags=["task", "mcp", "browser"]
)
```

### Agent Handoff Coordination
```python path=null start=null
# From Architect to Developer
WriteMemory(
    content="Architecture decision: Use factory pattern for MCP clients",
    tags=["architecture", "mcp", "handoff"]
)

# Developer progress update
WriteMemory(
    content="Completed: Basic MCP client implementation with mock responses",
    tags=["progress", "mcp", "implementation"]
)
```

### Context Retrieval for Decision Making
```python path=null start=null
# Get relevant context for current task
context = ReadMemoryContext(
    tags=["mcp", "architecture"], 
    limit=15
)

# Get all recent activity
recent_context = ReadMemoryContext(limit=20)
```

---

## ⚙️ Memory Store Configuration

### In-Memory Store (Default)
**Use for**: Development, testing, isolated sessions

```python path=/Users/am/Code/Fresh/ai/memory/store.py start=115
from ai.memory.store import set_memory_store, InMemoryMemoryStore
set_memory_store(InMemoryMemoryStore())
```

### Firestore Backend (Staging)
**Use for**: Persistent storage, multi-session continuity  
**Documentation**: [ADR-003](../../.cursor/rules/ADR-003.md), [ADR-004](../../.cursor/rules/ADR-004.md)

```python path=null start=null
from ai.memory.store import set_memory_store, FirestoreMemoryStore
set_memory_store(FirestoreMemoryStore())
```

**Environment Variables**:
- `FIREBASE_PROJECT_ID` - Firestore project ID
- `FIREBASE_CLIENT_EMAIL` - Service account email  
- `FIREBASE_PRIVATE_KEY` - Service account private key

---

## 🔍 Memory Context Rendering

Memory context is automatically formatted for agent consumption:

```markdown path=null start=null
## Recent Memory Context

**Goal Context:**
- Strategic goal: Enhance agent MCP capabilities [feature, mcp]
- Architecture decision: Use factory pattern for MCP clients [architecture, mcp]

**Progress Context:**  
- Completed: Basic MCP client implementation [progress, mcp]
- Next: Add browser automation tools [task, mcp, browser]

**Recent Activity:**
- 3 memory writes in last session
- Focus areas: mcp, architecture, implementation
```

**Implementation**: See [store.py render_context()](store.py) function

---

## 📊 Memory Monitoring

### Activity Tracking
**Location**: [../monitor/activity.py](../monitor/activity.py)

```python path=null start=null
from ai.monitor.activity import record_memory_operation

# Automatically called by memory tools
record_memory_operation("write")  # or "read"
```

### Status Monitoring  
**Interface**: [../../scripts/monitor.sh](../../scripts/monitor.sh)  
**Documentation**: [Monitoring Guide](../../docs/MONITORING.md)

```bash
# Check memory usage and recent activity
./scripts/monitor.sh
```

---

## 🔧 Implementation Details

### Memory Entry Structure
```python path=/Users/am/Code/Fresh/ai/memory/store.py start=12
@dataclass
class MemoryEntry:
    id: str
    content: str
    tags: List[str]
    timestamp: datetime
```

### Store Interface
```python path=/Users/am/Code/Fresh/ai/memory/store.py start=25
class MemoryStore(ABC):
    @abstractmethod
    def write(self, content: str, tags: List[str]) -> MemoryEntry: ...
    
    @abstractmethod  
    def read(self, limit: int, tags: List[str] = None) -> List[MemoryEntry]: ...
```

---

## 🎯 Best Practices

### Effective Tagging
- **Use consistent tags**: `feature`, `bug`, `docs`, `refactor`, `adr`
- **Add context tags**: `mcp`, `browser`, `api`, `testing`  
- **Include stage tags**: `planning`, `implementation`, `review`, `done`

### Memory Hygiene
- **Be specific**: Write clear, actionable content
- **Tag appropriately**: Use relevant tags for easy retrieval
- **Update context**: Record progress and state changes

### Agent Coordination
- **Set clear goals**: Use memory for shared objectives
- **Track handoffs**: Record context transfers between agents
- **Monitor progress**: Regular updates on task completion

---

## 📦 Dependencies

### Core Dependencies
- `dataclasses` - Memory entry data structures
- `datetime` - Timestamp handling
- `uuid` - Unique identifier generation
- `typing` - Type hints and annotations

### Optional Dependencies
- `firebase-admin` - Firestore memory store backend
- `google-cloud-firestore` - Direct Firestore client (alternative)

### Installation
```bash
# Core memory system (no external dependencies)
poetry install --no-root

# With Firestore support
poetry install --no-root --extras firestore
# OR: pip install firebase-admin
```

### Environment Setup
For Firestore memory store:
```bash
export FIREBASE_PROJECT_ID="your-project-id"
export FIREBASE_CLIENT_EMAIL="service-account@project.iam.gserviceaccount.com"
export FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
```

---

## 🔗 Related Documentation

- **[Tool Reference](../../docs/TOOLS.md#memory-context-tools)** - Memory tool API and usage
- **[Agent Development Guide](../../docs/AGENT_DEVELOPMENT.md#memory-context)** - Memory in agent workflows  
- **[ADR-003](../../.cursor/rules/ADR-003.md)** - Firebase Firestore adoption decision
- **[ADR-004](../../.cursor/rules/ADR-004.md)** - Memory store abstraction design
- **[Monitoring Guide](../../docs/MONITORING.md)** - Memory activity monitoring

---

> 💡 **Agent Tip**: Always use memory tools for context that needs to persist beyond your current session. Tag memory entries with relevant categories for efficient retrieval by other agents. Check existing context with `ReadMemoryContext()` before writing new goals or decisions.
