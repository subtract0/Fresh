# API Reference

Comprehensive API reference for the Fresh AI memory system, tools, and enhanced agents. This reference provides detailed documentation for all public interfaces, classes, and methods.

## Table of Contents
- [Memory Store APIs](#memory-store-apis)
- [Memory Tool APIs](#memory-tool-apis)
- [Enhanced Agent APIs](#enhanced-agent-apis)
- [Data Models](#data-models)
- [Utility APIs](#utility-apis)
- [Error Handling](#error-handling)
- [Usage Examples](#usage-examples)
- [Cross-References](#cross-references)

---

## Memory Store APIs

### Base Memory Store Interface

#### `MemoryStore`
Abstract base class for all memory store implementations.

```python
from ai.memory.store import MemoryStore

class MemoryStore:
    def write(self, content: str, tags: List[str] = None) -> MemoryItem:
        """Store a memory item."""
        
    def read(self, memory_id: str) -> Optional[MemoryItem]:
        """Retrieve a specific memory item."""
        
    def query(self, tags: List[str] = None, limit: int = 10) -> List[MemoryItem]:
        """Query memory items by tags."""
        
    def delete(self, memory_id: str) -> bool:
        """Delete a memory item."""
```

**Parameters:**
- `content` (str): The content to store
- `tags` (List[str], optional): Tags for categorization
- `memory_id` (str): Unique identifier for the memory
- `limit` (int): Maximum number of items to return

**Returns:**
- `MemoryItem`: Individual memory item
- `List[MemoryItem]`: List of memory items
- `bool`: Success/failure status

---

### InMemoryMemoryStore

#### `InMemoryMemoryStore()`
Basic in-memory storage implementation.

```python
from ai.memory.in_memory_store import InMemoryMemoryStore

store = InMemoryMemoryStore()
```

**Features:**
- Zero external dependencies
- Fast access for development/testing
- Ephemeral storage (lost on restart)

**Methods:**
```python
def write(self, content: str, tags: List[str] = None) -> MemoryItem:
    """Store content with automatic ID generation."""
    
def read(self, memory_id: str) -> Optional[MemoryItem]:
    """Retrieve by memory ID."""
    
def query(self, tags: List[str] = None, limit: int = 10) -> List[MemoryItem]:
    """Query with tag filtering and limit."""
    
def clear(self) -> None:
    """Clear all memories."""
```

---

### IntelligentMemoryStore

#### `IntelligentMemoryStore()`
Advanced memory store with auto-classification and semantic search.

```python
from ai.memory.intelligent_store import IntelligentMemoryStore

store = IntelligentMemoryStore()
```

**Enhanced Methods:**
```python
def write(self, content: str, tags: List[str] = None) -> EnhancedMemoryItem:
    """Store with automatic classification and importance scoring."""
    
def search_by_keywords(self, keywords: List[str], limit: int = 10) -> List[EnhancedMemoryItem]:
    """Semantic keyword search with relevance ranking."""
    
def search_by_type(self, memory_type: MemoryType, limit: int = 10) -> List[EnhancedMemoryItem]:
    """Filter by memory type (goal, task, error, etc.)."""
    
def get_related_memories(self, memory_id: str, limit: int = 10) -> List[EnhancedMemoryItem]:
    """Find memories related by keywords and content."""
    
def get_memory_analytics(self) -> Dict[str, Any]:
    """Get memory statistics and analytics."""
```

**Analytics Response:**
```python
{
    "total_memories": 42,
    "type_distribution": {MemoryType.GOAL: 8, MemoryType.TASK: 15, ...},
    "average_importance": 0.67,
    "top_keywords": {"implementation": 12, "testing": 8, ...},
    "recent_activity": 5,  # memories in last hour
}
```

---

### FirestoreMemoryStore

#### `FirestoreMemoryStore(max_cache_size=100, sync_interval=300)`
Persistent memory store with Firestore backend and local caching.

```python
from ai.memory.firestore_store import FirestoreMemoryStore

# Requires FIREBASE_* environment variables
store = FirestoreMemoryStore(
    max_cache_size=100,    # Local cache limit
    sync_interval=300      # Auto-sync interval (seconds)
)
```

**Parameters:**
- `max_cache_size` (int): Maximum items in local cache
- `sync_interval` (int): Automatic sync interval in seconds

**Enhanced Persistent Methods:**
```python
def search_firestore(self, keywords: List[str], limit: int = 10, 
                    memory_type: MemoryType = None) -> List[EnhancedMemoryItem]:
    """Search directly in Firestore (cross-session)."""
    
def force_sync(self) -> Dict[str, Any]:
    """Force synchronization with Firestore."""
    
def consolidate_memories(self, days_back: int = 7, 
                        min_importance: float = 0.6) -> Dict[str, Any]:
    """Clean up old, low-importance memories."""
    
def get_memory_stats(self) -> Dict[str, Any]:
    """Get comprehensive memory statistics."""
```

**Sync Response:**
```python
{
    "synced_count": 15,
    "failed_count": 0, 
    "total_items": 42,
    "sync_time": "2025-09-01T12:00:00Z"
}
```

**Consolidation Response:**
```python
{
    "deleted_count": 8,
    "updated_count": 23,
    "space_saved": "45%",
    "consolidation_time": "2025-09-01T12:00:00Z"
}
```

---

## Memory Tool APIs

### Basic Memory Tools

#### `WriteMemory`
Basic memory storage tool for agents.

```python
from ai.tools.memory_tools import WriteMemory

tool = WriteMemory(content="Task completed successfully", tags=["task", "completed"])
memory_id = tool.run()  # Returns: "mem-abc123"
```

**Fields:**
- `content` (str, required): Content to store
- `tags` (List[str], optional): Tags for categorization

**Returns:** Memory ID string

---

#### `ReadMemoryContext`  
Basic memory retrieval tool for agents.

```python
from ai.tools.memory_tools import ReadMemoryContext

tool = ReadMemoryContext(limit=5, tags=["authentication"])
context = tool.run()  # Returns formatted string
```

**Fields:**
- `limit` (int, default=10): Maximum memories to return
- `tags` (List[str], optional): Filter by tags

**Returns:** Formatted context string

---

### Enhanced Memory Tools

#### `SmartWriteMemory`
Intelligent memory storage with auto-classification.

```python
from ai.tools.enhanced_memory_tools import SmartWriteMemory

tool = SmartWriteMemory(
    content="Goal: Implement real-time agent communication",
    tags=["goal", "communication"]  
)
result = tool.run()  
# Returns: JSON with intelligence metadata
```

**Fields:**
- `content` (str, required): Content to store with automatic intelligence
- `tags` (List[str], optional): Optional tags (auto-enhanced)

**Returns:** JSON string with metadata:
```json
{
    "id": "mem-xyz789",
    "type": "goal", 
    "importance": 0.85,
    "keywords": ["goal", "implement", "real", "time"],
    "related": 3
}
```

---

#### `SemanticSearchMemory`
Intelligent keyword-based memory search.

```python
from ai.tools.enhanced_memory_tools import SemanticSearchMemory

tool = SemanticSearchMemory(
    keywords=["authentication", "security", "jwt"],
    limit=5
)
results = tool.run()  # Returns formatted results with relevance
```

**Fields:**
- `keywords` (List[str], required): Keywords to search for
- `limit` (int, default=5): Maximum results to return

**Returns:** Formatted search results with metadata

---

#### `GetMemoryByType`
Type-filtered memory retrieval.

```python
from ai.tools.enhanced_memory_tools import GetMemoryByType

tool = GetMemoryByType(memory_type="goal", limit=10)
goals = tool.run()  # Returns formatted goal memories
```

**Fields:**
- `memory_type` (str, required): Memory type (goal, task, error, etc.)
- `limit` (int, default=5): Maximum results to return

**Valid Memory Types:**
- `"goal"` - Strategic objectives and targets
- `"task"` - Specific work items and actions
- `"context"` - Environmental and situational info  
- `"decision"` - Choices made and rationale
- `"progress"` - Status updates and milestones
- `"error"` - Problems and failures encountered
- `"knowledge"` - Lessons learned and insights

**Returns:** Formatted memory list

---

#### `GetRelatedMemories`
Relationship-based memory exploration.

```python
from ai.tools.enhanced_memory_tools import GetRelatedMemories

tool = GetRelatedMemories(memory_id="mem-abc123", limit=5)
related = tool.run()  # Returns connected memories
```

**Fields:**
- `memory_id` (str, required): ID of the memory to find relations for
- `limit` (int, default=5): Maximum related memories to return

**Returns:** Formatted related memories with connection strength

---

### Persistent Memory Tools

#### `PersistentMemorySearch`
Cross-session memory search with advanced filtering.

```python
from ai.tools.persistent_memory_tools import PersistentMemorySearch

tool = PersistentMemorySearch(
    keywords=["authentication", "implementation"],
    limit=10,
    memory_type="decision",  # Optional type filter
    days_back=30            # Optional time limit
)
results = tool.run()  # Returns cross-session search results
```

**Fields:**
- `keywords` (List[str], required): Keywords to search for
- `limit` (int, default=10): Maximum results to return
- `memory_type` (str, optional): Filter by memory type
- `days_back` (int, optional): Limit to last N days

**Returns:** Formatted cross-session search results

---

#### `CrossSessionAnalytics`
Memory pattern analysis across sessions.

```python
from ai.tools.persistent_memory_tools import CrossSessionAnalytics

tool = CrossSessionAnalytics(days_back=30)
analytics = tool.run()  # Returns comprehensive analytics
```

**Fields:**
- `days_back` (int, default=30): Analysis time window

**Returns:** Formatted analytics report with:
- Total memory statistics
- Memory type distribution
- Learning insights and patterns
- Activity trends
- Storage efficiency metrics

---

#### `MemoryLearningPatterns`
Learning evolution and pattern analysis.

```python
from ai.tools.persistent_memory_tools import MemoryLearningPatterns

tool = MemoryLearningPatterns(focus_areas=["security", "testing"])
patterns = tool.run()  # Returns learning pattern analysis
```

**Fields:**
- `focus_areas` (List[str], optional): Specific areas to analyze

**Returns:** Formatted learning analysis with:
- Focus area evolution
- Learning trend analysis  
- Knowledge consolidation opportunities
- Cross-temporal pattern recognition

---

#### `MemoryConsolidation`
Memory cleanup and optimization tools.

```python
from ai.tools.persistent_memory_tools import MemoryConsolidation

tool = MemoryConsolidation(
    days_back=7,
    min_importance=0.6,
    dry_run=True  # Simulate without actual cleanup
)
report = tool.run()  # Returns consolidation report
```

**Fields:**
- `days_back` (int, default=7): Consider memories older than N days
- `min_importance` (float, default=0.6): Minimum importance to keep
- `dry_run` (bool, default=True): Simulate without actual deletion

**Returns:** Consolidation report with cleanup statistics

---

#### `MemorySync`
Force synchronization with persistent storage.

```python
from ai.tools.persistent_memory_tools import MemorySync

tool = MemorySync()
sync_report = tool.run()  # Force sync to Firestore
```

**Returns:** Sync status report with transfer statistics

---

## Enhanced Agent APIs

### Base Enhanced Agent

#### `EnhancedAgent`
Base class for all enhanced agents with memory capabilities.

```python
from ai.agents.enhanced_agents import EnhancedAgent

class CustomEnhancedAgent(EnhancedAgent):
    def __init__(self):
        super().__init__(
            name="CustomAgent",
            description="Custom agent with memory",
            tools=[SmartWriteMemory, SemanticSearchMemory]
        )
```

**Common Methods:**
```python
def consult_memory(self, keywords: List[str]) -> str:
    """Consult memory before taking action."""
    
def store_learning(self, content: str, tags: List[str] = None) -> str:
    """Store insights and learnings."""
    
def analyze_patterns(self, focus_areas: List[str] = None) -> str:
    """Analyze learning patterns."""
```

---

### Specific Enhanced Agents

#### `EnhancedFather`
Strategic planner with cross-session goal tracking.

```python
from ai.agents.enhanced_agents import EnhancedFather

father = EnhancedFather()
```

**Specialized Tools:**
- `SmartWriteMemory` - Store strategic decisions
- `PersistentMemorySearch` - Learn from past experiences  
- `CrossSessionAnalytics` - Development pattern analysis
- `MemoryLearningPatterns` - Strategic pattern recognition

**Memory Strategy:**
- Goal evolution tracking
- Decision outcome learning
- Strategic pattern recognition
- Cross-session context preservation

---

#### `EnhancedArchitect`
Design specialist with architectural pattern memory.

```python
from ai.agents.enhanced_agents import EnhancedArchitect

architect = EnhancedArchitect()
```

**Specialized Tools:**
- `SmartWriteMemory` - Store design decisions and ADRs
- `GetMemoryByType` - Review past architectural decisions
- `PersistentMemorySearch` - Find similar design challenges
- `GetRelatedMemories` - Explore connected design patterns

**Memory Strategy:**
- Design pattern library building
- ADR outcome tracking
- TDD effectiveness learning
- Complexity trade-off analysis

---

#### `EnhancedDeveloper`
Implementation specialist with solution pattern memory.

```python
from ai.agents.enhanced_agents import EnhancedDeveloper

developer = EnhancedDeveloper()
```

**Specialized Tools:**
- `SmartWriteMemory` - Store implementation solutions
- `PersistentMemorySearch` - Find similar past problems
- `SemanticSearchMemory` - Explore implementation approaches
- `GetRelatedMemories` - Connected solutions and techniques

**Memory Strategy:**
- Solution pattern recognition
- Bug learning and prevention
- Refactoring technique tracking
- Library/framework wisdom building

---

#### `EnhancedQA`
Quality specialist with test pattern memory.

```python
from ai.agents.enhanced_agents import EnhancedQA

qa = EnhancedQA()
```

**Specialized Tools:**
- `SmartWriteMemory` - Store test patterns and insights
- `SemanticSearchMemory` - Find similar testing challenges
- `GetMemoryByType` - Review past error patterns
- `GetRelatedMemories` - Explore connected quality approaches

**Memory Strategy:**
- Test pattern library building
- Bug pattern recognition
- Quality metric effectiveness tracking
- Integration failure point mapping

---

### Agent Factory Functions

#### `create_enhanced_agents()`
Create all enhanced agents with memory capabilities.

```python
from ai.agents.enhanced_agents import create_enhanced_agents

agents = create_enhanced_agents()
# Returns: {
#     'Father': EnhancedFather(),
#     'Architect': EnhancedArchitect(),
#     'Developer': EnhancedDeveloper(), 
#     'QA': EnhancedQA()
# }
```

**Returns:** Dictionary mapping agent names to enhanced agent instances

---

#### `get_agent(name, enhanced=True)`
Get agent instance with optional enhancement.

```python
from ai.agents.enhanced_agents import get_agent

# Enhanced agent
enhanced_father = get_agent('Father', enhanced=True)

# Standard agent (backward compatibility)
standard_father = get_agent('Father', enhanced=False)
```

**Parameters:**
- `name` (str): Agent name ('Father', 'Architect', 'Developer', 'QA')
- `enhanced` (bool, default=True): Whether to use enhanced memory capabilities

**Returns:** Agent instance with appropriate memory capabilities

---

## Data Models

### MemoryItem
Base memory item model.

```python
@dataclass
class MemoryItem:
    id: str
    content: str
    tags: List[str]
    created_at: datetime
    updated_at: datetime
```

**Fields:**
- `id` (str): Unique identifier (e.g., "mem-abc123")
- `content` (str): The stored content
- `tags` (List[str]): Associated tags for categorization
- `created_at` (datetime): Creation timestamp  
- `updated_at` (datetime): Last modification timestamp

---

### EnhancedMemoryItem
Enhanced memory item with intelligence metadata.

```python
@dataclass  
class EnhancedMemoryItem(MemoryItem):
    memory_type: MemoryType
    keywords: List[str]
    importance_score: float
    summary: Optional[str]
    related_ids: List[str]
```

**Additional Fields:**
- `memory_type` (MemoryType): Automatically classified type
- `keywords` (List[str]): Extracted keywords for search
- `importance_score` (float): Calculated importance (0.0-1.0)
- `summary` (str, optional): Generated summary for long content
- `related_ids` (List[str]): IDs of related memories

---

### MemoryType
Enumeration of memory types for classification.

```python
from enum import Enum

class MemoryType(Enum):
    GOAL = "goal"
    TASK = "task" 
    CONTEXT = "context"
    DECISION = "decision"
    PROGRESS = "progress"
    ERROR = "error"
    KNOWLEDGE = "knowledge"
```

**Usage:**
```python
memory_type = MemoryType.GOAL
print(memory_type.value)  # "goal"
```

---

## Utility APIs

### Memory Store Factory

#### `get_store(store_type=None)`
Factory function to get appropriate memory store.

```python
from ai.memory.store import get_store

# Automatic selection based on environment
store = get_store()

# Explicit store type
firestore_store = get_store("firestore")
intelligent_store = get_store("intelligent") 
basic_store = get_store("memory")
```

**Parameters:**
- `store_type` (str, optional): Explicit store type selection

**Store Types:**
- `"firestore"` - FirestoreMemoryStore (if available)
- `"intelligent"` - IntelligentMemoryStore
- `"memory"` - InMemoryMemoryStore

**Returns:** Memory store instance

---

### Context Rendering

#### `render_context(limit=10, tags=None)`
Render memory context for agent prompts.

```python
from ai.memory.store import render_context

context = render_context(limit=5, tags=["authentication"])
```

**Parameters:**
- `limit` (int, default=10): Maximum memories to include
- `tags` (List[str], optional): Filter by tags

**Returns:** Formatted context string for agent prompts

---

### Activity Monitoring

#### `record_memory_operation(operation_type)`
Record memory operations for monitoring.

```python
from ai.monitor.activity import record_memory_operation

record_memory_operation("write")  # Track memory write
record_memory_operation("read")   # Track memory read
```

**Parameters:**
- `operation_type` (str): Operation type ("write", "read", "search")

---

## Error Handling

### Common Exceptions

#### `MemoryStoreError`
Base exception for memory store operations.

```python
from ai.memory.store import MemoryStoreError

try:
    result = store.write(content="test")
except MemoryStoreError as e:
    print(f"Memory operation failed: {e}")
```

#### `FirestoreConnectionError`
Firestore-specific connection errors.

```python
from ai.memory.firestore_store import FirestoreConnectionError

try:
    store = FirestoreMemoryStore()
except FirestoreConnectionError as e:
    print(f"Firestore unavailable: {e}")
```

#### `MemoryNotFoundError`
Memory item not found errors.

```python
from ai.memory.store import MemoryNotFoundError

try:
    memory = store.read("invalid-id")
except MemoryNotFoundError as e:
    print(f"Memory not found: {e}")
```

### Error Handling Patterns

#### Graceful Degradation
```python
try:
    # Try Firestore store
    store = FirestoreMemoryStore()
except FirestoreConnectionError:
    # Fallback to intelligent store
    store = IntelligentMemoryStore()
```

#### Tool Error Handling
```python
try:
    result = search_tool.run()
    return result
except Exception as e:
    logger.error(f"Memory search failed: {e}")
    return "Memory search temporarily unavailable"
```

---

## Usage Examples

### Basic Memory Operations
```python
# Get memory store
from ai.memory.store import get_store
store = get_store()

# Write memory
memory = store.write("Goal: Implement authentication", tags=["goal", "auth"])
print(f"Stored: {memory.id}")

# Read memory
retrieved = store.read(memory.id)
print(f"Retrieved: {retrieved.content}")

# Query memories
goals = store.query(tags=["goal"], limit=5)
print(f"Found {len(goals)} goals")
```

### Enhanced Memory Operations
```python
# Intelligent memory store
from ai.memory.intelligent_store import IntelligentMemoryStore
store = IntelligentMemoryStore()

# Smart write with classification
memory = store.write("Error: JWT token expired unexpectedly")
print(f"Type: {memory.memory_type}")  # MemoryType.ERROR
print(f"Keywords: {memory.keywords}")  # ["error", "jwt", "token", "expired"]

# Semantic search
results = store.search_by_keywords(["authentication", "error"])
for result in results:
    print(f"Found: {result.content}")
```

### Agent Memory Integration
```python
# Enhanced agent with memory
from ai.agents.enhanced_agents import EnhancedDeveloper

developer = EnhancedDeveloper()

# Memory-informed implementation
from ai.tools.enhanced_memory_tools import SemanticSearchMemory

# Search for similar implementations
search_tool = SemanticSearchMemory(
    keywords=["authentication", "jwt", "implementation"]
)
similar_work = search_tool.run()

# Store implementation insights
from ai.tools.enhanced_memory_tools import SmartWriteMemory

insight_tool = SmartWriteMemory(
    content="Learned: JWT middleware pattern improves maintainability",
    tags=["knowledge", "jwt", "pattern"]
)
insight_tool.run()
```

### Cross-Session Analytics
```python
# Get cross-session insights
from ai.tools.persistent_memory_tools import CrossSessionAnalytics, MemoryLearningPatterns

# Memory analytics
analytics = CrossSessionAnalytics(days_back=30)
analytics_report = analytics.run()
print(analytics_report)

# Learning patterns
patterns = MemoryLearningPatterns(focus_areas=["security", "testing"])
pattern_report = patterns.run() 
print(pattern_report)
```

---

## Cross-References

### Core Implementation
- [`ai/memory/store.py`](../ai/memory/store.py) - Memory store interfaces and factory
- [`ai/memory/in_memory_store.py`](../ai/memory/in_memory_store.py) - Basic memory implementation
- [`ai/memory/intelligent_store.py`](../ai/memory/intelligent_store.py) - Intelligent memory implementation
- [`ai/memory/firestore_store.py`](../ai/memory/firestore_store.py) - Persistent Firestore implementation

### Tools and Agents
- [`ai/tools/memory_tools.py`](../ai/tools/memory_tools.py) - Basic memory tools
- [`ai/tools/enhanced_memory_tools.py`](../ai/tools/enhanced_memory_tools.py) - Enhanced memory tools
- [`ai/tools/persistent_memory_tools.py`](../ai/tools/persistent_memory_tools.py) - Persistent memory tools
- [`ai/agents/enhanced_agents.py`](../ai/agents/enhanced_agents.py) - Enhanced agent implementations

### Documentation
- [Memory System Architecture](./MEMORY_SYSTEM.md) - System overview and architecture
- [Enhanced Agent Architecture](./ENHANCED_AGENTS.md) - Agent architecture guide
- [Agent Development Guide](./AGENT_DEVELOPMENT.md) - Development best practices  
- [Deployment Guide](./DEPLOYMENT.md) - Operations and deployment

### Testing
- [`tests/test_intelligent_memory.py`](../tests/test_intelligent_memory.py) - Intelligent memory tests
- [`tests/test_firestore_memory.py`](../tests/test_firestore_memory.py) - Firestore memory tests

### Architecture
- [ADR-004: Persistent Agent Memory](../.cursor/rules/ADR-004.md) - Architecture decision record

---

*This API reference provides complete documentation for integrating with the Fresh AI memory system. All APIs support graceful degradation and error handling for robust autonomous agent development.*
