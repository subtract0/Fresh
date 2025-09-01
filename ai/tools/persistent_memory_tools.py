"""
Persistent Memory Tools

Enhanced memory tools that work with FirestoreMemoryStore for persistent
agent memory across sessions and deployments.

Features:
- Persistent memory search across sessions  
- Memory consolidation and cleanup tools
- Cross-session memory analytics
- Learning pattern analysis

Cross-references:
    - ai/memory/firestore_store.py: Firestore memory implementation
    - ai/tools/enhanced_memory_tools.py: Base intelligent memory tools
    - ADR-004: Persistent Agent Memory
"""
from __future__ import annotations
import json
import logging
from datetime import datetime, timezone, timedelta
from typing import List, Optional, Dict, Any

try:
    from agency_swarm.tools import BaseTool
except ImportError:  # Allow running without agency_swarm
    class BaseTool:
        def run(self):
            raise NotImplementedError
from ai.memory.store import get_store
from ai.memory.firestore_store import FirestoreMemoryStore
from ai.memory.intelligent_store import MemoryType
from ai.utils.clock import now as time_now

logger = logging.getLogger(__name__)


class PersistentMemorySearch(BaseTool):
    """Search persistent memory across all sessions and deployments."""
    
    def __init__(self, keywords: List[str], limit: int = 10, 
                 memory_type: Optional[str] = None, days_back: Optional[int] = None):
        """
        Initialize persistent memory search.
        
        Args:
            keywords: Keywords to search for
            limit: Maximum results to return
            memory_type: Filter by memory type (goal, task, error, etc.)
            days_back: Limit search to last N days (None for all time)
        """
        super().__init__()
        self.keywords = keywords
        self.limit = limit
        self.memory_type = MemoryType(memory_type) if memory_type else None
        self.days_back = days_back
        
    def run(self) -> str:
        """Search persistent memory with cross-session capability."""
        try:
            store = get_store()
            
            # Use Firestore search if available, otherwise fallback
            if isinstance(store, FirestoreMemoryStore):
                results = store.search_firestore(
                    keywords=self.keywords,
                    limit=self.limit,
                    memory_type=self.memory_type
                )
                search_source = "Firestore (persistent)"
            else:
                results = store.search_by_keywords(self.keywords, self.limit)
                search_source = "Local cache"
                
            if not results:
                return f"No memories found for keywords: {', '.join(self.keywords)}"
                
            # Filter by date if specified
            if self.days_back:
                cutoff_time = time_now() - (self.days_back * 24 * 3600)
                results = [r for r in results if r.created_at.timestamp() >= cutoff_time]
                
            # Format results with persistent memory metadata
            output = [f"PERSISTENT MEMORY SEARCH ({search_source})"]
            output.append(f"Keywords: {', '.join(self.keywords)}")
            if self.memory_type:
                output.append(f"Type Filter: {self.memory_type.value.upper()}")
            if self.days_back:
                output.append(f"Time Range: Last {self.days_back} days")
            output.append(f"Found: {len(results)} memories")
            output.append("")
            
            for i, result in enumerate(results, 1):
                age_days = (time_now() - result.created_at.timestamp()) / (24 * 3600)
                
                output.append(f"{i}. [{result.memory_type.value.upper()}] {result.content[:100]}...")
                output.append(f"   ID: {result.id}")
                output.append(f"   Age: {age_days:.1f} days")
                output.append(f"   Importance: {result.importance_score:.2f}")
                output.append(f"   Keywords: {', '.join(result.keywords[:5])}")
                if result.tags:
                    output.append(f"   Tags: {', '.join(result.tags)}")
                if result.related_ids:
                    output.append(f"   Related: {len(result.related_ids)} memories")
                output.append("")
                
            return "\n".join(output)
            
        except Exception as e:
            logger.error(f"Persistent memory search failed: {e}")
            return f"Search failed: {e}"


class MemoryConsolidation(BaseTool):
    """Consolidate and clean up persistent memories."""
    
    def __init__(self, days_back: int = 7, min_importance: float = 0.6, 
                 dry_run: bool = True):
        """
        Initialize memory consolidation.
        
        Args:
            days_back: Consider memories older than this many days
            min_importance: Minimum importance score to keep memories
            dry_run: If True, only simulate cleanup without actual deletion
        """
        super().__init__()
        self.days_back = days_back
        self.min_importance = min_importance
        self.dry_run = dry_run
        
    def run(self) -> str:
        """Run memory consolidation and cleanup."""
        try:
            store = get_store()
            
            if not isinstance(store, FirestoreMemoryStore):
                return "Memory consolidation requires FirestoreMemoryStore"
                
            if self.dry_run:
                # Simulate consolidation
                output = [f"MEMORY CONSOLIDATION (DRY RUN)"]
                output.append(f"Criteria: Older than {self.days_back} days, importance < {self.min_importance}")
                output.append("")
                output.append("This would clean up old, low-importance memories from Firestore.")
                output.append("Run with dry_run=False to actually perform cleanup.")
                output.append("")
                
                # Show some stats
                stats = store.get_memory_stats()
                output.append(f"Current local cache: {stats.get('local_cache_size', 0)} memories")
                output.append(f"Firestore connected: {stats.get('firestore_connected', False)}")
                
                return "\n".join(output)
            else:
                # Actually perform consolidation
                result = store.consolidate_memories(
                    days_back=self.days_back,
                    min_importance=self.min_importance
                )
                
                output = [f"MEMORY CONSOLIDATION COMPLETE"]
                output.append(f"Criteria: Older than {self.days_back} days, importance < {self.min_importance}")
                output.append("")
                
                if "error" in result:
                    output.append(f"Error: {result['error']}")
                else:
                    output.append(f"Deleted: {result.get('deleted_count', 0)} low-value memories")
                    output.append(f"Updated: {result.get('updated_count', 0)} access timestamps")
                    output.append("")
                    output.append("Firestore storage optimized for better performance.")
                    
                return "\n".join(output)
                
        except Exception as e:
            logger.error(f"Memory consolidation failed: {e}")
            return f"Consolidation failed: {e}"


class CrossSessionAnalytics(BaseTool):
    """Analyze memory patterns across sessions and time."""
    
    def __init__(self, days_back: int = 30):
        """
        Initialize cross-session analytics.
        
        Args:
            days_back: Analyze memories from last N days
        """
        super().__init__()
        self.days_back = days_back
        
    def run(self) -> str:
        """Analyze memory patterns across sessions."""
        try:
            store = get_store()
            
            # Get comprehensive stats
            if isinstance(store, FirestoreMemoryStore):
                stats = store.get_memory_stats()
                has_firestore = True
            else:
                stats = store.get_memory_analytics()
                has_firestore = False
                
            output = [f"CROSS-SESSION MEMORY ANALYTICS"]
            output.append(f"Time Range: Last {self.days_back} days")
            output.append(f"Storage: {'Firestore (persistent)' if has_firestore else 'Local cache only'}")
            output.append("")
            
            # Basic statistics
            output.append(f"Total Memories: {stats.get('total_memories', 0)}")
            
            if has_firestore:
                output.append(f"Local Cache: {stats.get('local_cache_size', 0)}")
                output.append(f"Cache Limit: {stats.get('max_cache_size', 100)}")
                output.append(f"Last Sync: {datetime.fromtimestamp(stats.get('last_sync', 0), timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}")
                output.append("")
            
            # Memory type distribution
            if 'type_distribution' in stats:
                output.append("Memory Types:")
                for mem_type, count in stats['type_distribution'].items():
                    if hasattr(mem_type, 'value'):
                        type_name = mem_type.value.upper()
                    else:
                        type_name = str(mem_type).upper()
                    output.append(f"  {type_name}: {count}")
                output.append("")
            
            # Importance and activity patterns
            avg_importance = stats.get('average_importance', 0)
            output.append(f"Average Importance: {avg_importance:.3f}")
            
            recent_activity = stats.get('recent_activity', 0)
            if recent_activity > 0:
                output.append(f"Recent Activity: {recent_activity} memories in last hour")
            
            # Top keywords (learning patterns)
            if 'top_keywords' in stats:
                output.append("")
                output.append("Top Keywords (Learning Focus Areas):")
                for keyword, count in list(stats['top_keywords'].items())[:10]:
                    output.append(f"  {keyword}: {count}")
                    
            # Learning insights
            output.append("")
            output.append("Learning Insights:")
            
            # Analyze memory distribution
            if 'type_distribution' in stats:
                total = sum(stats['type_distribution'].values())
                if total > 0:
                    goal_ratio = stats['type_distribution'].get(MemoryType.GOAL, 0) / total
                    error_ratio = stats['type_distribution'].get(MemoryType.ERROR, 0) / total
                    
                    if goal_ratio > 0.2:
                        output.append("  ✓ High goal-setting activity - good strategic thinking")
                    if error_ratio > 0.1:
                        output.append("  ⚠ Significant error memories - learning from failures")
                    if avg_importance > 0.7:
                        output.append("  ✓ High-importance memories - focusing on key insights")
                        
            # Storage efficiency
            if has_firestore:
                cache_ratio = stats.get('local_cache_size', 0) / stats.get('max_cache_size', 100)
                if cache_ratio > 0.8:
                    output.append("  ℹ Local cache nearly full - consolidation recommended")
            
            return "\n".join(output)
            
        except Exception as e:
            logger.error(f"Cross-session analytics failed: {e}")
            return f"Analytics failed: {e}"


class MemoryLearningPatterns(BaseTool):
    """Analyze learning patterns and knowledge evolution."""
    
    def __init__(self, focus_areas: Optional[List[str]] = None):
        """
        Initialize learning pattern analysis.
        
        Args:
            focus_areas: Specific keywords/areas to analyze (None for all)
        """
        super().__init__()
        self.focus_areas = focus_areas or []
        
    def run(self) -> str:
        """Analyze learning patterns in persistent memory."""
        try:
            store = get_store()
            
            output = [f"LEARNING PATTERN ANALYSIS"]
            if self.focus_areas:
                output.append(f"Focus Areas: {', '.join(self.focus_areas)}")
            output.append("")
            
            # Get all memories for analysis
            all_memories = store.query(limit=1000)  # Get a large sample
            
            if not all_memories:
                return "No memories available for learning analysis"
                
            # Time-based learning analysis
            now = time_now()
            recent_memories = [m for m in all_memories if now - m.created_at.timestamp() < 7*24*3600]  # Last week
            old_memories = [m for m in all_memories if now - m.created_at.timestamp() >= 7*24*3600]
            
            output.append(f"Memory Timeline:")
            output.append(f"  Recent (last 7 days): {len(recent_memories)} memories")
            output.append(f"  Older: {len(old_memories)} memories")
            output.append("")
            
            # Knowledge evolution by focus areas
            if self.focus_areas:
                for area in self.focus_areas:
                    area_memories = [m for m in all_memories 
                                   if area.lower() in ' '.join(m.keywords + [m.content.lower()])]
                    
                    if area_memories:
                        output.append(f"Focus Area: {area.upper()}")
                        output.append(f"  Related memories: {len(area_memories)}")
                        
                        # Recent vs old for this area
                        area_recent = [m for m in area_memories if now - m.created_at.timestamp() < 7*24*3600]
                        area_old = [m for m in area_memories if now - m.created_at.timestamp() >= 7*24*3600]
                        
                        if area_recent and area_old:
                            recent_importance = sum(m.importance_score for m in area_recent) / len(area_recent)
                            old_importance = sum(m.importance_score for m in area_old) / len(area_old)
                            
                            if recent_importance > old_importance:
                                output.append(f"  ✓ Increasing focus - importance up {((recent_importance/old_importance - 1)*100):+.1f}%")
                            else:
                                output.append(f"  ↓ Decreasing focus - importance down {((1 - recent_importance/old_importance)*100):.1f}%")
                        
                        # Memory types for this area
                        area_types = {}
                        for memory in area_memories:
                            mem_type = memory.memory_type
                            area_types[mem_type] = area_types.get(mem_type, 0) + 1
                            
                        output.append(f"  Memory types: {', '.join(f'{t.value}:{c}' for t, c in area_types.items())}")
                        output.append("")
            
            # Overall learning insights
            output.append("Learning Insights:")
            
            # Error-to-knowledge conversion
            errors = [m for m in all_memories if m.memory_type == MemoryType.ERROR]
            knowledge = [m for m in all_memories if m.memory_type == MemoryType.KNOWLEDGE]
            
            if errors and knowledge:
                output.append(f"  Error-to-Knowledge ratio: {len(errors)}:{len(knowledge)}")
                if len(knowledge) >= len(errors) * 0.5:
                    output.append("  ✓ Good learning from failures - converting errors to knowledge")
                else:
                    output.append("  ⚠ Consider documenting more learnings from error experiences")
            
            # Goal achievement tracking
            goals = [m for m in all_memories if m.memory_type == MemoryType.GOAL]
            progress = [m for m in all_memories if m.memory_type == MemoryType.PROGRESS]
            
            if goals:
                output.append(f"  Active goals: {len(goals)}")
                if progress:
                    output.append(f"  Progress updates: {len(progress)}")
                    if len(progress) >= len(goals) * 0.3:
                        output.append("  ✓ Good goal tracking - regular progress updates")
                        
            # Knowledge consolidation opportunities
            high_importance = [m for m in all_memories if m.importance_score > 0.8]
            if len(high_importance) > 10:
                output.append(f"  High-value memories: {len(high_importance)}")
                output.append("  💡 Consider creating knowledge summaries from high-value memories")
                
            return "\n".join(output)
            
        except Exception as e:
            logger.error(f"Learning pattern analysis failed: {e}")
            return f"Learning analysis failed: {e}"


class MemorySync(BaseTool):
    """Force synchronization of local memory to persistent storage."""
    
    def __init__(self):
        """Initialize memory sync tool."""
        super().__init__()
        
    def run(self) -> str:
        """Force sync local memories to Firestore."""
        try:
            store = get_store()
            
            if not isinstance(store, FirestoreMemoryStore):
                return "Memory sync requires FirestoreMemoryStore (Firestore not available)"
                
            result = store.force_sync()
            
            output = [f"MEMORY SYNC TO FIRESTORE"]
            output.append("")
            
            if "error" in result:
                output.append(f"Sync failed: {result['error']}")
            else:
                output.append(f"Successfully synced: {result.get('synced_count', 0)} memories")
                output.append(f"Failed to sync: {result.get('failed_count', 0)} memories")
                output.append(f"Total local memories: {result.get('total_items', 0)}")
                output.append("")
                output.append("All local memories are now persistent in Firestore.")
                
            return "\n".join(output)
            
        except Exception as e:
            logger.error(f"Memory sync failed: {e}")
            return f"Sync failed: {e}"
