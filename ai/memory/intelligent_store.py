"""
Intelligent Memory Store

Enhanced memory system with semantic search, auto-tagging, and context intelligence.
Extends the basic memory store with AI-powered features for better agent coordination.

Cross-references:
    - Base implementation: ai/memory/store.py
    - Memory tools: ai/tools/memory_tools.py
    - ADR-008: Intelligent Memory System (to be created)
"""
from __future__ import annotations
import re
import hashlib
from collections import defaultdict, Counter
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List, Optional, Dict, Set, Tuple, Any
from enum import Enum

from ai.memory.store import MemoryStore, MemoryItem
from ai.utils.clock import now as time_now


class MemoryType(Enum):
    """Classification of memory content types."""
    GOAL = "goal"           # Strategic goals and objectives
    TASK = "task"           # Specific tasks and actions
    CONTEXT = "context"     # Background information and state
    DECISION = "decision"   # ADRs and architectural decisions
    PROGRESS = "progress"   # Status updates and completion notes
    ERROR = "error"         # Failures and lessons learned
    KNOWLEDGE = "knowledge" # Facts and learned information


@dataclass(frozen=False)  # Changed to mutable for metadata updates
class EnhancedMemoryItem(MemoryItem):
    """Enhanced memory item with intelligent metadata."""
    memory_type: MemoryType = field(default=MemoryType.CONTEXT)
    keywords: List[str] = field(default_factory=list)
    related_ids: List[str] = field(default_factory=list)
    importance_score: float = field(default=0.5)  # 0.0-1.0
    summary: Optional[str] = field(default=None)
    metadata: Dict[str, Any] = field(default_factory=dict)  # Additional metadata


class IntelligentMemoryStore(MemoryStore):
    """Enhanced memory store with semantic search and auto-classification."""
    
    def __init__(self):
        self._items: List[EnhancedMemoryItem] = []
        self._id_counter = 0
        self._keyword_index: Dict[str, Set[str]] = defaultdict(set)
        self._type_index: Dict[MemoryType, List[str]] = defaultdict(list)
        
    def _generate_id(self) -> str:
        """Generate unique memory ID."""
        self._id_counter += 1
        return f"mem-{self._id_counter:04d}"
        
    def _extract_keywords(self, content: str) -> List[str]:
        """Extract relevant keywords from content."""
        # Simple keyword extraction - can be enhanced with NLP
        words = re.findall(r'\b\w+\b', content.lower())
        
        # Filter out common words and focus on meaningful terms
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'is', 'was', 'are', 'were', 'be', 'been', 'have',
            'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should',
            'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they',
            'needs', 'after'  # Additional stop words
        }
        
        keywords = [w for w in words if len(w) > 2 and w not in stop_words]
        
        # Return most frequent keywords
        keyword_counts = Counter(keywords)
        return [k for k, v in keyword_counts.most_common(10)]
        
    def _classify_content(self, content: str, tags: List[str]) -> MemoryType:
        """Auto-classify memory content type."""
        content_lower = content.lower()
        tags_lower = [t.lower() for t in tags]
        
        # Goal indicators
        if any(word in content_lower for word in ['goal', 'objective', 'mission', 'target', 'aim']):
            return MemoryType.GOAL
        if any(tag in tags_lower for tag in ['goal', 'objective', 'mission']):
            return MemoryType.GOAL
            
        # Task indicators  
        if any(word in content_lower for word in ['task', 'todo', 'implement', 'create', 'build', 'fix']):
            return MemoryType.TASK
        if any(tag in tags_lower for tag in ['task', 'todo', 'action']):
            return MemoryType.TASK
            
        # Decision indicators
        if any(word in content_lower for word in ['adr', 'decision', 'architecture', 'design']):
            return MemoryType.DECISION  
        if any(tag in tags_lower for tag in ['adr', 'decision', 'architecture']):
            return MemoryType.DECISION
            
        # Progress indicators
        if any(word in content_lower for word in ['completed', 'done', 'finished', 'progress', 'status']):
            return MemoryType.PROGRESS
        if any(tag in tags_lower for tag in ['done', 'completed', 'progress']):
            return MemoryType.PROGRESS
            
        # Error indicators
        if any(word in content_lower for word in ['error', 'failed', 'bug', 'issue', 'problem']):
            return MemoryType.ERROR
        if any(tag in tags_lower for tag in ['error', 'bug', 'failed']):
            return MemoryType.ERROR
            
        # Knowledge indicators
        if any(word in content_lower for word in ['learned', 'discovered', 'found', 'research']):
            return MemoryType.KNOWLEDGE
        if any(tag in tags_lower for tag in ['knowledge', 'research', 'learning']):
            return MemoryType.KNOWLEDGE
            
        return MemoryType.CONTEXT  # Default
        
    def _calculate_importance(self, content: str, memory_type: MemoryType) -> float:
        """Calculate importance score for memory item."""
        score = 0.5  # Base score
        
        # Type-based scoring
        type_scores = {
            MemoryType.GOAL: 0.9,
            MemoryType.DECISION: 0.8, 
            MemoryType.ERROR: 0.7,
            MemoryType.TASK: 0.6,
            MemoryType.PROGRESS: 0.5,
            MemoryType.KNOWLEDGE: 0.6,
            MemoryType.CONTEXT: 0.4
        }
        score = type_scores.get(memory_type, 0.5)
        
        # Content-based scoring
        high_value_words = ['critical', 'important', 'urgent', 'blocker', 'milestone']
        if any(word in content.lower() for word in high_value_words):
            score = max(score, 0.8)  # Ensure critical content gets high score
            
        # Length-based scoring (longer content often more important)
        if len(content) > 200:
            score += 0.1
        elif len(content) < 50:
            score -= 0.1
            
        return min(1.0, max(0.0, score))
        
    def _generate_summary(self, content: str) -> Optional[str]:
        """Generate a summary for long content."""
        if len(content) <= 100:
            return None
            
        # Simple summary: first sentence or first 100 chars
        sentences = re.split(r'[.!?]+', content)
        if sentences and len(sentences[0]) <= 100:
            return sentences[0].strip()
        else:
            return content[:97] + "..."
            
    def _find_related_items(self, keywords: List[str], exclude_id: str) -> List[str]:
        """Find related memory items based on keyword overlap."""
        related = []
        
        for item in self._items:
            if item.id == exclude_id:
                continue
                
            # Calculate keyword overlap
            common_keywords = set(keywords) & set(item.keywords)
            if len(common_keywords) >= 1:  # At least 1 common keyword
                related.append(item.id)
                
        return related[:5]  # Limit to 5 most related
        
    def _update_indexes(self, item: EnhancedMemoryItem) -> None:
        """Update internal indexes for fast lookup."""
        # Update keyword index
        for keyword in item.keywords:
            self._keyword_index[keyword].add(item.id)
            
        # Update type index
        self._type_index[item.memory_type].append(item.id)
        
    def write(self, *, content: str, tags: Optional[List[str]] = None, memory_type: Optional[MemoryType] = None, metadata: Optional[Dict[str, Any]] = None) -> MemoryItem:
        """Write enhanced memory item with automatic intelligence."""
        tags = tags or []
        item_id = self._generate_id()
        
        # Extract intelligence
        keywords = self._extract_keywords(content)
        # Use provided memory_type or auto-classify
        if memory_type is None:
            memory_type = self._classify_content(content, tags)
        importance = self._calculate_importance(content, memory_type)
        summary = self._generate_summary(content)
        
        # Create enhanced item
        item = EnhancedMemoryItem(
            id=item_id,
            content=content,
            tags=tags,
            created_at=datetime.fromtimestamp(time_now(), timezone.utc),
            memory_type=memory_type,
            keywords=keywords,
            related_ids=[],  # Will be populated after storage
            importance_score=importance,
            summary=summary,
            metadata=metadata or {}
        )
        
        # Store item
        self._items.append(item)
        self._update_indexes(item)
        
        # Update related items (after storage so item exists in search)
        related_ids = self._find_related_items(keywords, item_id)
        if related_ids:
            # Update the stored item with related IDs
            updated_item = EnhancedMemoryItem(
                id=item.id,
                content=item.content,
                tags=item.tags,
                created_at=item.created_at,
                memory_type=item.memory_type,
                keywords=item.keywords,
                related_ids=related_ids,
                importance_score=item.importance_score,
                summary=item.summary,
                metadata=item.metadata
            )
            self._items[-1] = updated_item  # Replace the last added item
            
            # Update existing related items to include this item
            for i, existing_item in enumerate(self._items[:-1]):  # Exclude the current item
                if existing_item.id in related_ids:
                    # Add bidirectional relationship
                    if item_id not in existing_item.related_ids:
                        updated_existing = EnhancedMemoryItem(
                            id=existing_item.id,
                            content=existing_item.content,
                            tags=existing_item.tags,
                            created_at=existing_item.created_at,
                            memory_type=existing_item.memory_type,
                            keywords=existing_item.keywords,
                            related_ids=existing_item.related_ids + [item_id],
                            importance_score=existing_item.importance_score,
                            summary=existing_item.summary,
                            metadata=existing_item.metadata
                        )
                        self._items[i] = updated_existing
            
        return self._items[-1]
        
    def query(self, *, limit: int = 5, tags: Optional[List[str]] = None, keywords: Optional[List[str]] = None, memory_type: Optional[MemoryType] = None) -> List[MemoryItem]:
        """Enhanced query with intelligent filtering."""
        items = self._items
        
        # Filter by memory type if provided
        if memory_type is not None:
            items = [i for i in items if i.memory_type == memory_type]
            
        # Filter by tags if provided
        if tags:
            tagset = set(tags)
            items = [i for i in items if tagset.intersection(i.tags)]
            
        # Filter by keywords if provided
        if keywords:
            keyword_set = set(k.lower() for k in keywords)
            filtered_items = []
            for item in items:
                item_keywords = set(item.keywords)
                if keyword_set & item_keywords:  # If any keywords match
                    filtered_items.append(item)
            items = filtered_items
            
        # Sort by importance and recency
        items = sorted(items, key=lambda i: (i.importance_score, i.created_at.timestamp()), reverse=True)
        
        return items[:max(0, limit)]
        
    def search_by_keywords(self, keywords: List[str], limit: int = 10) -> List[EnhancedMemoryItem]:
        """Search memories by keywords."""
        keyword_set = set(k.lower() for k in keywords)
        results = []
        
        for item in self._items:
            item_keywords = set(item.keywords)
            overlap = len(keyword_set & item_keywords)
            if overlap > 0:
                # Score based on keyword overlap and importance
                relevance_score = (overlap / len(keyword_set)) * item.importance_score
                results.append((relevance_score, item))
                
        # Sort by relevance
        results.sort(key=lambda x: x[0], reverse=True)
        return [item for _, item in results[:limit]]
        
    def search_by_type(self, memory_type: MemoryType, limit: int = 10) -> List[EnhancedMemoryItem]:
        """Search memories by type."""
        items = [item for item in self._items if item.memory_type == memory_type]
        items = sorted(items, key=lambda i: (i.importance_score, i.created_at.timestamp()), reverse=True)
        return items[:limit]
        
    def get_related_memories(self, memory_id: str, limit: int = 5) -> List[EnhancedMemoryItem]:
        """Get memories related to a specific memory."""
        item = self.get_by_id(memory_id)
        if not item:
            return []
            
        related_items = []
        for related_id in item.related_ids:
            related_item = self.get_by_id(related_id)
            if related_item:
                related_items.append(related_item)
                
        return related_items[:limit]
        
    def get_by_id(self, memory_id: str) -> Optional[EnhancedMemoryItem]:
        """Get memory by ID."""
        for item in self._items:
            if item.id == memory_id:
                return item
        return None
        
    def get_memory_analytics(self) -> Dict[str, any]:
        """Get analytics about memory usage."""
        if not self._items:
            return {"total_memories": 0}
            
        type_counts = Counter(item.memory_type for item in self._items)
        avg_importance = sum(item.importance_score for item in self._items) / len(self._items)
        top_keywords = Counter()
        
        for item in self._items:
            top_keywords.update(item.keywords)
            
        return {
            "total_memories": len(self._items),
            "type_distribution": dict(type_counts),
            "average_importance": avg_importance,
            "top_keywords": dict(top_keywords.most_common(10)),
            "recent_activity": len([i for i in self._items if time_now() - i.created_at.timestamp() < 3600])  # Last hour
        }
        
    def optimize_memory(self, max_items: int = 1000) -> int:
        """Optimize memory by removing low-importance old items."""
        if len(self._items) <= max_items:
            return 0
            
        # Sort by importance and age (keep important and recent)
        self._items.sort(key=lambda i: (i.importance_score, i.created_at.timestamp()), reverse=True)
        
        # Keep only the top items
        removed_count = len(self._items) - max_items
        self._items = self._items[:max_items]
        
        # Rebuild indexes
        self._keyword_index.clear()
        self._type_index.clear()
        for item in self._items:
            self._update_indexes(item)
            
        return removed_count
