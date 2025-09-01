# Memory System Architecture

The Fresh AI memory system provides intelligent, persistent memory capabilities for autonomous agents. The system enables agents to learn from past experiences, make better decisions based on historical context, and maintain knowledge across sessions.

## Table of Contents
- [Architecture Overview](#architecture-overview)
- [Memory Store Implementations](#memory-store-implementations) 
- [Memory Classification](#memory-classification)
- [Tools and APIs](#tools-and-apis)
- [Enhanced Agents](#enhanced-agents)
- [Usage Patterns](#usage-patterns)
- [Cross-References](#cross-references)

---

## Architecture Overview

The memory system follows a layered architecture with multiple implementations offering different capabilities:

```
┌─────────────────────────────────────────────────┐
│                Enhanced Agents                   │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐│
│  │   Father    │ │ Architect   │ │ Developer   ││
│  │ Strategic   │ │ Design      │ │ Implementation│
│  │ Planning    │ │ Patterns    │ │ Learning    ││
│  └─────────────┘ └─────────────┘ └─────────────┘│
└─────────────────────────────────────────────────┘
                      ┃
┌─────────────────────────────────────────────────┐
│              Memory Tools Layer                 │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐│
│  │   Basic     │ │ Intelligent │ │ Persistent  ││
│  │   Tools     │ │   Tools     │ │   Tools     ││
│  └─────────────┘ └─────────────┘ └─────────────┘│
└─────────────────────────────────────────────────┘
                      ┃
┌─────────────────────────────────────────────────┐
│            Memory Store Layer                   │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐│
│  │ InMemory    │ │ Intelligent │ │ Firestore   ││
│  │ Store       │ │  Store      │ │   Store     ││
│  └─────────────┘ └─────────────┘ └─────────────┘│
└─────────────────────────────────────────────────┘
```

### Key Components

- **Memory Store Layer**: Storage implementations with increasing intelligence
- **Memory Tools Layer**: Agent-facing tools for memory operations
- **Enhanced Agents**: AI agents with persistent memory capabilities

---

## Memory Store Implementations

### 1. InMemoryMemoryStore 
*Basic storage for development and testing*

```python
from ai.memory.store import get_store

# Automatic selection based on environment
store = get_store()  # Returns InMemoryMemoryStore by default
```

**Features:**
- Simple key-value storage
- Zero external dependencies
- Ephemeral (lost on restart)
- Perfect for development and testing

### 2. IntelligentMemoryStore
*Advanced memory with auto-classification and relationships*

```python
from ai.memory.intelligent_store import IntelligentMemoryStore

# Explicit intelligent store
store = IntelligentMemoryStore()

# Writes return enhanced memory items
memory = store.write("Goal: Implement real-time communication", tags=["goal"])
print(f"Type: {memory.memory_type}")  # MemoryType.GOAL  
print(f"Importance: {memory.importance_score}")  # 0.85
print(f"Keywords: {memory.keywords}")  # ["goal", "implement", "real", "time"]
```

**Features:**
- **Auto-classification**: Automatically determines memory type
- **Importance scoring**: Dynamic scoring based on content analysis  
- **Keyword extraction**: Intelligent keyword identification
- **Semantic search**: Keyword-based search with relevance ranking
- **Bidirectional relationships**: Auto-linking related memories
- **Analytics**: Memory pattern analysis and statistics

### 3. FirestoreMemoryStore
*Persistent storage with cross-session capabilities*

```python
from ai.memory.firestore_store import FirestoreMemoryStore

# Requires FIREBASE_* environment variables
store = FirestoreMemoryStore(
    max_cache_size=100,  # Local cache limit
    sync_interval=300    # Auto-sync every 5 minutes
)
```

**Features:**
- **Persistent storage**: Memories survive across sessions
- **Local cache**: Fast access with intelligent cache management
- **Cross-session search**: Search memories from previous sessions
- **Memory consolidation**: Automatic cleanup of old, low-importance memories
- **Sync operations**: Bidirectional sync between local cache and Firestore
- **Analytics**: Cross-session learning pattern analysis

---

## Memory Classification

The system automatically classifies memories into semantic types:

### Memory Types

| Type | Description | Examples | Importance Range |
|------|-------------|----------|------------------|
| **GOAL** | Strategic objectives and targets | "Goal: Implement authentication", "Objective: Reduce latency" | 0.7-1.0 |
| **TASK** | Specific work items and actions | "Task: Add unit tests", "TODO: Update documentation" | 0.5-0.8 |
| **CONTEXT** | Environmental and situational info | "Using Python 3.12", "Database: PostgreSQL 15" | 0.3-0.6 |
| **DECISION** | Choices made and rationale | "Decision: Use Redis for caching", "ADR-005: GraphQL API" | 0.6-0.9 |
| **PROGRESS** | Status updates and milestones | "Progress: 80% complete", "Milestone: Beta release" | 0.4-0.7 |
| **ERROR** | Problems and failures encountered | "Error: Connection timeout", "Bug: Memory leak in handler" | 0.6-0.8 |
| **KNOWLEDGE** | Lessons learned and insights | "Learned: Async improves performance", "Pattern: Factory works well" | 0.7-0.9 |

### Importance Scoring Algorithm

Importance scores (0.0-1.0) are calculated based on:

1. **Critical Keywords**: High-value terms boost importance
   - Technical terms: "architecture", "security", "performance" 
   - Action words: "implement", "fix", "optimize"
   - Strategic terms: "goal", "objective", "decision"

2. **Content Analysis**: 
   - Length and detail level
   - Specific vs. general language
   - Presence of technical specifics

3. **Memory Type**: Certain types have higher base importance
   - Goals and decisions: High importance  
   - Context and progress: Medium importance
   - Tasks: Variable based on content

4. **Relationship Density**: Memories with many connections score higher

---

## Tools and APIs

### Basic Memory Tools

```python
from ai.tools.memory_tools import WriteMemory, ReadMemoryContext

# Simple memory storage
write_tool = WriteMemory(content="Started authentication module", tags=["task", "auth"])
memory_id = write_tool.run()

# Basic context retrieval  
read_tool = ReadMemoryContext(limit=5, tags=["auth"])
context = read_tool.run()
```

### Intelligent Memory Tools

```python
from ai.tools.enhanced_memory_tools import (
    SmartWriteMemory, SemanticSearchMemory, 
    GetMemoryByType, GetRelatedMemories
)

# Smart memory with auto-classification
smart_write = SmartWriteMemory(
    content="Goal: Implement real-time agent communication system",
    tags=["goal", "communication"]
)
result = smart_write.run()  # Returns JSON with intelligence metadata

# Semantic keyword search
search = SemanticSearchMemory(keywords=["authentication", "security"], limit=5)
results = search.run()  # Returns ranked results with relevance scores

# Type-based retrieval
goals = GetMemoryByType(memory_type="goal", limit=10)
goal_list = goals.run()  # Returns all goal memories

# Relationship exploration
related = GetRelatedMemories(memory_id="mem-0123", limit=5)
connections = related.run()  # Returns related memories
```

### Persistent Memory Tools

```python
from ai.tools.persistent_memory_tools import (
    PersistentMemorySearch, CrossSessionAnalytics,
    MemoryLearningPatterns, MemoryConsolidation
)

# Cross-session search
persistent_search = PersistentMemorySearch(
    keywords=["authentication", "security"],
    limit=10,
    memory_type="decision",  # Optional type filter
    days_back=30            # Optional time limit
)
results = persistent_search.run()

# Learning pattern analysis
patterns = MemoryLearningPatterns(focus_areas=["authentication", "testing"])
analysis = patterns.run()  # Returns learning insights and evolution

# Memory analytics
analytics = CrossSessionAnalytics(days_back=30)
stats = analytics.run()  # Returns cross-session statistics and insights

# Memory consolidation 
consolidation = MemoryConsolidation(
    days_back=7,
    min_importance=0.6,
    dry_run=True  # Simulate cleanup
)
cleanup_report = consolidation.run()
```

---

## Enhanced Agents

Enhanced agents leverage persistent memory for continuous learning and improvement.

### Agent Capabilities

#### EnhancedFather (Strategic Agent)
- **Goal Tracking**: Maintains strategic objectives across sessions
- **Decision Learning**: Learns from past planning outcomes  
- **Pattern Recognition**: Identifies successful strategic patterns
- **Context Continuity**: Maintains strategic context between sessions

```python
from ai.agents.enhanced_agents import EnhancedFather

father = EnhancedFather()
# Agent has access to:
# - SmartWriteMemory, PersistentMemorySearch
# - CrossSessionAnalytics, MemoryLearningPatterns  
# - GenerateReleaseNotes, GenerateNextSteps
```

#### EnhancedArchitect (Design Agent)
- **Design Patterns**: Remembers successful architectural decisions
- **ADR Outcomes**: Tracks long-term results of architectural choices
- **TDD Learning**: Learns effective testing strategies 
- **Complexity Management**: Remembers trade-offs and their outcomes

#### EnhancedDeveloper (Implementation Agent)  
- **Solution Patterns**: Remembers successful implementation approaches
- **Bug Learning**: Learns from past bugs and their solutions
- **Refactoring Techniques**: Tracks effective refactoring patterns
- **Code Quality**: Remembers what leads to maintainable code

#### EnhancedQA (Quality Agent)
- **Test Patterns**: Remembers effective testing strategies
- **Bug Patterns**: Learns common failure modes and edge cases
- **Quality Insights**: Tracks which quality measures work
- **Integration Testing**: Remembers integration points that commonly fail

### Memory-Driven Workflows

Enhanced agents use memory to:

1. **Check Past Experience**: Before starting, agents search for similar past work
2. **Apply Learned Patterns**: Use successful patterns from memory
3. **Avoid Known Issues**: Learn from past errors and failures
4. **Track Progress**: Compare current work against past performance
5. **Store Insights**: Capture learnings for future sessions

---

## Usage Patterns

### 1. Development Workflow Integration

```python
# Agent starts new task
search_results = SemanticSearchMemory(
    keywords=["authentication", "implementation"], 
    limit=5
).run()

# Agent writes progress updates
SmartWriteMemory(
    content="Progress: Authentication module 60% complete, JWT implementation done",
    tags=["progress", "authentication"]
).run()

# Agent captures learnings
SmartWriteMemory(
    content="Learned: JWT refresh token rotation improves security significantly", 
    tags=["knowledge", "security", "authentication"]
).run()
```

### 2. Strategic Planning

```python
# Review past goals and their outcomes
past_goals = GetMemoryByType(memory_type="goal", limit=10).run()

# Analyze learning patterns
patterns = MemoryLearningPatterns(
    focus_areas=["performance", "security", "testing"]
).run()

# Set new goal based on insights
SmartWriteMemory(
    content="Goal: Improve test coverage to 95% based on past quality issues",
    tags=["goal", "testing", "quality"]
).run()
```

### 3. Error Learning

```python
# When error occurs, search for similar past errors
similar_errors = SemanticSearchMemory(
    keywords=["database", "connection", "timeout"],
    limit=3
).run()

# Store the error and solution
SmartWriteMemory(
    content="Error: Database connection pool exhausted during high load. Fixed by increasing pool size to 50.",
    tags=["error", "database", "performance", "solved"]
).run()

# Store the learning
SmartWriteMemory(
    content="Learned: Connection pool size needs to scale with concurrent user load. Monitor pool utilization metrics.",
    tags=["knowledge", "database", "monitoring"]
).run()
```

### 4. Cross-Session Analytics

```python
# Analyze memory patterns for insights
analytics = CrossSessionAnalytics(days_back=30).run()

# Focus on specific learning areas
patterns = MemoryLearningPatterns(
    focus_areas=["security", "performance", "testing"]
).run()

# Clean up old memories
consolidation = MemoryConsolidation(
    days_back=14,
    min_importance=0.4,
    dry_run=False
).run()
```

---

## Cross-References

### Core Implementation Files
- [`ai/memory/store.py`](../ai/memory/store.py) - Base memory store interface
- [`ai/memory/in_memory_store.py`](../ai/memory/in_memory_store.py) - Basic in-memory implementation  
- [`ai/memory/intelligent_store.py`](../ai/memory/intelligent_store.py) - Intelligent memory with classification
- [`ai/memory/firestore_store.py`](../ai/memory/firestore_store.py) - Persistent Firestore implementation

### Tools and APIs
- [`ai/tools/memory_tools.py`](../ai/tools/memory_tools.py) - Basic memory tools
- [`ai/tools/enhanced_memory_tools.py`](../ai/tools/enhanced_memory_tools.py) - Intelligent memory tools  
- [`ai/tools/persistent_memory_tools.py`](../ai/tools/persistent_memory_tools.py) - Persistent memory tools

### Enhanced Agents
- [`ai/agents/enhanced_agents.py`](../ai/agents/enhanced_agents.py) - Enhanced agents with persistent memory

### Testing and Validation  
- [`tests/test_intelligent_memory.py`](../tests/test_intelligent_memory.py) - Intelligent memory tests
- [`tests/test_firestore_memory.py`](../tests/test_firestore_memory.py) - Firestore memory tests

### Architecture Documents
- [ADR-004: Persistent Agent Memory](../.cursor/rules/ADR-004.md) - Architecture decision record
- [Enhanced Agent Architecture](./ENHANCED_AGENTS.md) - Detailed agent architecture guide
- [API Reference](./API_REFERENCE.md) - Comprehensive API documentation
- [Deployment Guide](./DEPLOYMENT.md) - Operations and deployment guide

### Demo Scripts
- [`scripts/demo-persistent-memory.py`](../scripts/demo-persistent-memory.py) - Memory system demonstration
- [`scripts/demo-agent-activity.py`](../scripts/demo-agent-activity.py) - Agent activity simulation

---

*The Fresh AI Memory System enables autonomous agents to learn, adapt, and improve continuously through intelligent memory management and cross-session persistence.*
