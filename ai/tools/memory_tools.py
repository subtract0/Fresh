"""Memory management tools for persistent agent context and knowledge sharing.

This module provides the core memory interface for agents to store and retrieve
context across sessions and agent handoffs. Memory enables coordination between
specialized agents in the Fresh ecosystem.

Cross-references:
    - Memory System Guide: docs/MEMORY_SYSTEM.md for patterns and best practices
    - Agent Development: docs/AGENT_DEVELOPMENT.md#memory-context for usage
    - Tool Reference: docs/TOOLS.md#memory-context-tools for complete API
    
Related:
    - ai.memory.store: Memory storage abstraction and implementations
    - ai.agency: Memory store initialization for agent swarms
"""
from __future__ import annotations
from typing import List, Optional

try:
    from agency_swarm.tools import BaseTool
    from pydantic import Field
except Exception:  # pragma: no cover - allow running tests without agency_swarm
    class BaseTool:  # type: ignore
        def run(self):
            raise NotImplementedError

    def Field(*args, **kwargs):  # type: ignore
        return None

from ai.memory.store import get_store
from ai.monitor.activity import record_memory_operation


class WriteMemory(BaseTool):
    """Store knowledge, context, and state for cross-agent sharing.
    
    WriteMemory enables agents to persist information that other agents can
    retrieve later. This is essential for coordination in multi-agent workflows.
    
    Cross-references:
        - Usage patterns: docs/AGENT_DEVELOPMENT.md#memory-context
        - Implementation details: ai/memory/store.py
        - Tool documentation: docs/TOOLS.md#writememory
        
    Examples:
        Goal setting:
            WriteMemory(content="Goal: Add MCP integration", tags=["feature"])
            
        Progress tracking:
            WriteMemory(content="Completed: API design", tags=["done", "api"])
            
        Context sharing:
            WriteMemory(content="Using pytest for testing", tags=["context"])
            
    Returns:
        str: Unique ID of the stored memory entry for reference
    """

    content: str = Field(..., description="Content to remember")
    tags: List[str] = Field(default_factory=list, description="Optional tags for filtering")

    def run(self) -> str:  # type: ignore[override]
        item = get_store().write(content=self.content, tags=self.tags)
        record_memory_operation("write")
        return item.id


class ReadMemoryContext(BaseTool):
    """Retrieve relevant stored context for current task.
    
    ReadMemoryContext enables agents to access previously stored knowledge
    and context, essential for maintaining state across agent handoffs.
    
    Cross-references:
        - Usage patterns: docs/AGENT_DEVELOPMENT.md#memory-context  
        - Memory system: ai/memory/store.py#render_context
        - Tool documentation: docs/TOOLS.md#readmemorycontext
        
    Examples:
        Get recent context:
            ReadMemoryContext(limit=10)
            
        Filter by tags:
            ReadMemoryContext(tags=["feature", "mcp"], limit=5)
            
        All context for planning:
            ReadMemoryContext(limit=50)
            
    Returns:
        str: Formatted context string with recent memory entries
    """

    limit: int = Field(default=5, description="Max number of recent items to include")
    tags: Optional[List[str]] = Field(default=None, description="Optional tags filter")

    def run(self) -> str:  # type: ignore[override]
        from ai.memory.store import render_context
        result = render_context(limit=self.limit, tags=self.tags)
        record_memory_operation("read")
        return result
