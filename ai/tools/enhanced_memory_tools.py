"""
Enhanced Memory Tools

Intelligent memory tools that leverage semantic search, auto-classification,
and contextual understanding for better agent coordination.

Cross-references:
    - Base tools: ai/tools/memory_tools.py
    - Intelligent store: ai/memory/intelligent_store.py
    - Memory system: docs/MEMORY_SYSTEM.md
"""
from __future__ import annotations
from typing import List, Optional, Dict, Any

try:
    from agency_swarm.tools import BaseTool
    from pydantic import Field
    PYDANTIC_AVAILABLE = True
except Exception:  # pragma: no cover - allow running tests without agency_swarm
    class BaseTool:  # type: ignore
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)
        def run(self):
            raise NotImplementedError

    def Field(default=None, **kwargs):  # type: ignore
        return default
    PYDANTIC_AVAILABLE = False

from ai.memory.store import get_store
from ai.memory.intelligent_store import IntelligentMemoryStore, MemoryType, EnhancedMemoryItem
from ai.monitor.activity import record_memory_operation


class SmartWriteMemory(BaseTool):
    """Store knowledge with automatic classification and importance scoring.
    
    SmartWriteMemory automatically analyzes content to classify type, extract keywords,
    calculate importance, and find related memories. This enables better agent coordination
    through intelligent memory organization.
    
    Cross-references:
        - Basic version: ai/tools/memory_tools.py#WriteMemory
        - Intelligence: ai/memory/intelligent_store.py
        - Usage patterns: docs/AGENT_DEVELOPMENT.md#smart-memory
        
    Examples:
        Strategic goals:
            SmartWriteMemory(content="Goal: Implement real-time agent communication", tags=["goal", "communication"])
            → Auto-classified as GOAL type, high importance score
            
        Task documentation:
            SmartWriteMemory(content="Task: Add semantic search to memory system", tags=["task", "memory"])
            → Auto-classified as TASK type, finds related memories
            
        Learning capture:
            SmartWriteMemory(content="Learned: Activity detection needs 60s sliding window for accuracy")
            → Auto-classified as KNOWLEDGE type, extracts technical keywords
            
    Returns:
        str: JSON string with memory ID and intelligence metadata
    """
    
    if PYDANTIC_AVAILABLE:
        content: str = Field(..., description="Content to remember with automatic intelligence")
        tags: List[str] = Field(default_factory=list, description="Optional tags (auto-enhanced)")
    
    def __init__(self, content: str = None, tags: List[str] = None, **kwargs):
        if PYDANTIC_AVAILABLE:
            kwargs['content'] = content or kwargs.get('content', '')
            kwargs['tags'] = tags if tags is not None else kwargs.get('tags', [])
            super().__init__(**kwargs)
        else:
            super().__init__(content=content or '', tags=tags or [], **kwargs)

    def run(self) -> str:  # type: ignore[override]
        store = get_store()
        
        # Use intelligent store if available
        if isinstance(store, IntelligentMemoryStore):
            item = store.write(content=self.content, tags=self.tags)
            record_memory_operation("write")
            
            # Return enhanced metadata
            if isinstance(item, EnhancedMemoryItem):
                return f"{{\"id\": \"{item.id}\", \"type\": \"{item.memory_type.value}\", \"importance\": {item.importance_score:.2f}, \"keywords\": {item.keywords}, \"related\": {len(item.related_ids)}}}"
        else:
            # Fallback to basic store
            item = store.write(content=self.content, tags=self.tags)
            record_memory_operation("write")
            
        return item.id


class SemanticSearchMemory(BaseTool):
    """Search memories by keywords with intelligent ranking.
    
    SemanticSearchMemory finds relevant memories using keyword matching,
    importance scoring, and relevance ranking. More intelligent than basic tag filtering.
    
    Cross-references:
        - Basic search: ai/tools/memory_tools.py#ReadMemoryContext
        - Search algorithm: ai/memory/intelligent_store.py#search_by_keywords
        
    Examples:
        Find architecture decisions:
            SemanticSearchMemory(keywords=["architecture", "decision", "adr"])
            
        Research communication patterns:
            SemanticSearchMemory(keywords=["agent", "communication", "flow"])
            
        Debug issues:
            SemanticSearchMemory(keywords=["error", "failed", "bug"])
            
    Returns:
        str: Formatted search results with relevance scores
    """
    
    if PYDANTIC_AVAILABLE:
        keywords: List[str] = Field(..., description="Keywords to search for")
        limit: int = Field(default=5, description="Maximum results to return")
    
    def __init__(self, keywords: List[str] = None, limit: int = 5, **kwargs):
        if PYDANTIC_AVAILABLE:
            kwargs['keywords'] = keywords or kwargs.get('keywords', [])
            kwargs['limit'] = limit if limit != 5 else kwargs.get('limit', 5)
            super().__init__(**kwargs)
        else:
            super().__init__(keywords=keywords or [], limit=limit, **kwargs)

    def run(self) -> str:  # type: ignore[override]
        store = get_store()
        record_memory_operation("read")
        
        if isinstance(store, IntelligentMemoryStore):
            results = store.search_by_keywords(self.keywords, self.limit)
            
            if not results:
                return "No memories found matching keywords."
                
            lines = []
            for i, item in enumerate(results, 1):
                summary = item.summary if item.summary else item.content[:100]
                lines.append(f"{i}. [{item.memory_type.value.upper()}] {summary}")
                lines.append(f"   Keywords: {', '.join(item.keywords[:5])}")
                lines.append(f"   Importance: {item.importance_score:.2f}")
                if item.related_ids:
                    lines.append(f"   Related: {len(item.related_ids)} memories")
                lines.append("")
                
            return "\n".join(lines)
        else:
            # Fallback to basic search
            from ai.memory.store import render_context
            return render_context(limit=self.limit)


class GetMemoryByType(BaseTool):
    """Retrieve memories by classification type.
    
    GetMemoryByType retrieves memories of specific types (goals, tasks, decisions, etc.)
    sorted by importance and recency. Useful for focused context retrieval.
    
    Examples:
        Get current goals:
            GetMemoryByType(memory_type="goal")
            
        Review recent decisions:
            GetMemoryByType(memory_type="decision", limit=3)
            
        Find past errors:
            GetMemoryByType(memory_type="error")
            
    Returns:
        str: Formatted list of memories of specified type
    """
    
    if PYDANTIC_AVAILABLE:
        memory_type: str = Field(..., description="Type: goal, task, context, decision, progress, error, knowledge")
        limit: int = Field(default=5, description="Maximum results to return")
    
    def __init__(self, memory_type: str = None, limit: int = 5, **kwargs):
        if PYDANTIC_AVAILABLE:
            kwargs['memory_type'] = memory_type or kwargs.get('memory_type', '')
            kwargs['limit'] = limit if limit != 5 else kwargs.get('limit', 5)
            super().__init__(**kwargs)
        else:
            super().__init__(memory_type=memory_type or '', limit=limit, **kwargs)

    def run(self) -> str:  # type: ignore[override]
        store = get_store()
        record_memory_operation("read")
        
        if isinstance(store, IntelligentMemoryStore):
            try:
                mem_type = MemoryType(self.memory_type.lower())
                results = store.search_by_type(mem_type, self.limit)
                
                if not results:
                    return f"No {self.memory_type} memories found."
                    
                lines = [f"📋 {self.memory_type.upper()} MEMORIES:"]
                for i, item in enumerate(results, 1):
                    summary = item.summary if item.summary else item.content
                    lines.append(f"\n{i}. [{item.created_at.strftime('%Y-%m-%d')}] {summary}")
                    lines.append(f"   Importance: {item.importance_score:.2f}")
                    if item.related_ids:
                        lines.append(f"   Related: {len(item.related_ids)} memories")
                        
                return "\n".join(lines)
            except ValueError:
                return f"Invalid memory type: {self.memory_type}. Use: goal, task, context, decision, progress, error, knowledge"
        else:
            # Fallback to basic search with tag filtering
            from ai.memory.store import render_context
            return render_context(limit=self.limit, tags=[self.memory_type])


class GetRelatedMemories(BaseTool):
    """Find memories related to a specific memory.
    
    GetRelatedMemories finds memories that share keywords or themes with a given memory,
    enabling agents to explore connected context and knowledge.
    
    Examples:
        Explore related context:
            GetRelatedMemories(memory_id="mem-0042")
            
        Find connected knowledge:
            GetRelatedMemories(memory_id="mem-0123", limit=3)
            
    Returns:
        str: Formatted list of related memories
    """
    
    if PYDANTIC_AVAILABLE:
        memory_id: str = Field(..., description="ID of memory to find relations for")
        limit: int = Field(default=5, description="Maximum related memories to return")
    
    def __init__(self, memory_id: str, limit: int = 5, **kwargs):
        if PYDANTIC_AVAILABLE:
            super().__init__(**kwargs)
        else:
            super().__init__(memory_id=memory_id, limit=limit, **kwargs)

    def run(self) -> str:  # type: ignore[override]
        store = get_store()
        record_memory_operation("read")
        
        if isinstance(store, IntelligentMemoryStore):
            related = store.get_related_memories(self.memory_id, self.limit)
            
            if not related:
                return f"No related memories found for {self.memory_id}."
                
            # Get the original memory for context
            original = store.get_by_id(self.memory_id)
            lines = []
            
            if original:
                lines.append(f"🔗 MEMORIES RELATED TO: {original.summary or original.content[:50]}...")
                
            for i, item in enumerate(related, 1):
                summary = item.summary if item.summary else item.content[:100]
                lines.append(f"\n{i}. [{item.memory_type.value.upper()}] {summary}")
                lines.append(f"   Created: {item.created_at.strftime('%Y-%m-%d %H:%M')}")
                
                # Show shared keywords
                if original and item.keywords:
                    shared = set(original.keywords) & set(item.keywords)
                    if shared:
                        lines.append(f"   Shared: {', '.join(list(shared)[:3])}")
                        
            return "\n".join(lines)
        else:
            return f"Related memory search requires intelligent memory store. Memory ID: {self.memory_id}"


class AnalyzeMemoryUsage(BaseTool):
    """Get analytics and insights about memory usage patterns.
    
    AnalyzeMemoryUsage provides insights into how memory is being used,
    what types of information are stored, and usage patterns over time.
    
    Returns:
        str: Formatted analytics report
    """
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def run(self) -> str:  # type: ignore[override]
        store = get_store()
        record_memory_operation("read")
        
        if isinstance(store, IntelligentMemoryStore):
            analytics = store.get_memory_analytics()
            
            lines = ["📊 MEMORY USAGE ANALYTICS"]
            lines.append("=" * 40)
            lines.append(f"Total Memories: {analytics.get('total_memories', 0)}")
            lines.append(f"Average Importance: {analytics.get('average_importance', 0):.2f}")
            lines.append(f"Recent Activity: {analytics.get('recent_activity', 0)} in last hour")
            
            # Type distribution
            type_dist = analytics.get('type_distribution', {})
            if type_dist:
                lines.append("\n📂 Memory Types:")
                for mem_type, count in type_dist.items():
                    type_name = mem_type.value.upper() if hasattr(mem_type, 'value') else str(mem_type).upper()
                    lines.append(f"   {type_name}: {count}")
                    
            # Top keywords
            keywords = analytics.get('top_keywords', {})
            if keywords:
                lines.append("\n🔤 Top Keywords:")
                for keyword, count in list(keywords.items())[:5]:
                    lines.append(f"   {keyword}: {count}")
                    
            return "\n".join(lines)
        else:
            # Basic analytics for simple store
            if hasattr(store, '_items'):
                return f"📊 Basic Memory Stats:\nTotal Memories: {len(store._items)}"
            return "📊 Memory analytics unavailable for current store type."


class OptimizeMemoryStore(BaseTool):
    """Optimize memory store by removing low-importance old items.
    
    OptimizeMemoryStore cleans up the memory store by removing less important
    old memories to maintain performance and focus on relevant information.
    
    Examples:
        Regular cleanup:
            OptimizeMemoryStore(max_items=500)
            
        Aggressive cleanup:
            OptimizeMemoryStore(max_items=100)
            
    Returns:
        str: Optimization report
    """
    
    if PYDANTIC_AVAILABLE:
        max_items: int = Field(default=1000, description="Maximum items to keep")
    
    def __init__(self, max_items: int = 1000, **kwargs):
        if PYDANTIC_AVAILABLE:
            kwargs['max_items'] = max_items if max_items != 1000 else kwargs.get('max_items', 1000)
            super().__init__(**kwargs)
        else:
            super().__init__(max_items=max_items, **kwargs)

    def run(self) -> str:  # type: ignore[override]
        store = get_store()
        
        if isinstance(store, IntelligentMemoryStore):
            removed = store.optimize_memory(self.max_items)
            
            if removed > 0:
                return f"🧹 Memory optimized: Removed {removed} low-importance items, kept {self.max_items} most valuable memories."
            else:
                return f"✅ Memory already optimized: {len(store._items)} items (under {self.max_items} limit)."
        else:
            return "Memory optimization requires intelligent memory store."
