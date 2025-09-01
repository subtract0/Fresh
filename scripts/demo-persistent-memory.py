#!/usr/bin/env python3
"""
Persistent Memory Demo

Demonstrates the persistent memory capabilities of the agent system,
showing how agents can learn and remember across sessions.

This demo shows:
- Intelligent memory classification and storage
- Persistent storage with Firestore (if available) 
- Cross-session memory search and analytics
- Learning pattern analysis
- Memory consolidation and optimization

Usage:
    python scripts/demo-persistent-memory.py [--use-firestore] [--project-id PROJECT]
"""
import argparse
import sys
import time
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from ai.memory.store import set_memory_store, get_store
from ai.memory.intelligent_store import IntelligentMemoryStore
from ai.memory.firestore_store import create_firestore_memory_store, FIRESTORE_AVAILABLE
from ai.tools.persistent_memory_tools import (
    PersistentMemorySearch,
    MemoryConsolidation, 
    CrossSessionAnalytics,
    MemoryLearningPatterns,
    MemorySync
)
from ai.tools.enhanced_memory_tools import SmartWriteMemory


def print_section(title: str):
    """Print a formatted section header."""
    print(f"\n{'='*60}")
    print(f" {title}")
    print(f"{'='*60}")


def simulate_agent_activity(store_type: str = "intelligent"):
    """Simulate diverse agent activity to populate memory."""
    print(f"Simulating agent learning activity with {store_type} memory store...")
    
    # Simulate various agent activities
    activities = [
        # Goals and planning
        ("Goal: Implement intelligent agent memory system", ["goal", "memory"]),
        ("Goal: Create self-learning agent capabilities", ["goal", "learning"]),
        ("Goal: Deploy agent monitoring dashboard", ["goal", "monitoring"]),
        
        # Task execution
        ("Task: Fix memory synchronization bug in Firestore store", ["task", "bug", "firestore"]),
        ("Task: Implement semantic search for memory queries", ["task", "search", "semantic"]),
        ("Task: Add bidirectional relationship updates", ["task", "relationships"]),
        
        # Decisions and architecture
        ("ADR-004: Adopt Firestore for persistent agent memory", ["adr", "decision", "firestore"]),
        ("ADR-005: Implement adaptive monitoring with Rich UI", ["adr", "decision", "monitoring"]),
        ("Decision: Use keyword-based semantic search over full-text", ["decision", "search"]),
        
        # Errors and learning
        ("Error: Firestore connection timeout after 30 seconds", ["error", "firestore", "timeout"]),
        ("Error: Memory search returned 0 results for valid keywords", ["error", "search", "bug"]),
        ("Bug: Related memory detection not working for first item", ["error", "bug", "relationships"]),
        
        # Knowledge and insights
        ("Learned: Bidirectional relationship updates improve memory connectivity", ["knowledge", "relationships"]),
        ("Learned: Importance scoring needs critical content boost for accuracy", ["knowledge", "importance"]),
        ("Discovered: Local cache management prevents memory bloat", ["knowledge", "performance"]),
        
        # Progress updates
        ("Completed: All intelligent memory tests are now passing", ["progress", "done", "testing"]),
        ("Progress: Firestore integration 80% complete, testing remaining", ["progress", "firestore"]),
        ("Finished: Memory consolidation and cleanup functionality", ["progress", "done", "cleanup"]),
        
        # Context and observations
        ("System uses Python 3.12 with pytest for testing framework", ["context", "python"]),
        ("Agent monitoring system shows 4.2 second test suite runtime", ["context", "monitoring", "performance"]),
        ("Rich UI provides excellent terminal interface for agent status", ["context", "ui", "rich"]),
    ]
    
    print(f"Adding {len(activities)} memory items...")
    
    # Get the current memory store
    memory_store = get_store()
    
    for i, (content, tags) in enumerate(activities):
        # Use memory store directly instead of tool
        item = memory_store.write(content=content, tags=tags)
        print(f"  {i+1:2d}. Added: {content[:50]}...")
        
        # Small delay to simulate real activity
        time.sleep(0.1)
    
    print(f"Agent activity simulation complete!")


def demonstrate_search_capabilities():
    """Demonstrate various search and query capabilities."""
    print_section("MEMORY SEARCH CAPABILITIES")
    
    # Search by different keywords
    search_terms = [
        (["memory", "agent"], "Memory and Agent Systems"),
        (["error", "bug"], "Error Tracking and Debugging"),
        (["goal"], "Strategic Goals and Objectives"),
        (["firestore"], "Firestore Integration"),
        (["monitoring"], "Monitoring and Observability")
    ]
    
    for keywords, description in search_terms:
        print(f"\n--- {description} ---")
        search_tool = PersistentMemorySearch(keywords=keywords, limit=5)
        result = search_tool.run()
        print(result)


def demonstrate_analytics():
    """Demonstrate memory analytics and learning patterns."""
    print_section("MEMORY ANALYTICS & LEARNING PATTERNS")
    
    # Cross-session analytics
    print("--- Cross-Session Analytics ---")
    analytics_tool = CrossSessionAnalytics(days_back=30)
    result = analytics_tool.run()
    print(result)
    
    # Learning pattern analysis
    print("\n--- Learning Pattern Analysis ---")
    learning_tool = MemoryLearningPatterns(focus_areas=["memory", "firestore", "monitoring"])
    result = learning_tool.run()
    print(result)


def demonstrate_consolidation():
    """Demonstrate memory consolidation (dry run only)."""
    print_section("MEMORY CONSOLIDATION")
    
    # Dry run consolidation
    consolidation_tool = MemoryConsolidation(days_back=7, min_importance=0.6, dry_run=True)
    result = consolidation_tool.run()
    print(result)


def demonstrate_sync(has_firestore: bool):
    """Demonstrate memory synchronization if Firestore is available."""
    if not has_firestore:
        print_section("MEMORY SYNC (FIRESTORE NOT AVAILABLE)")
        print("Firestore sync demonstration skipped - no Firestore connection")
        return
        
    print_section("MEMORY SYNC TO FIRESTORE")
    
    sync_tool = MemorySync()
    result = sync_tool.run()
    print(result)


def main():
    """Run the persistent memory demonstration."""
    parser = argparse.ArgumentParser(description="Demonstrate persistent memory capabilities")
    parser.add_argument("--use-firestore", action="store_true", 
                       help="Try to use Firestore for persistent storage")
    parser.add_argument("--project-id", type=str, 
                       help="Google Cloud project ID for Firestore")
    
    args = parser.parse_args()
    
    print("🧠 PERSISTENT MEMORY DEMONSTRATION")
    print("="*60)
    
    # Initialize memory store
    if args.use_firestore and FIRESTORE_AVAILABLE:
        print("Attempting to initialize Firestore memory store...")
        try:
            memory_store = create_firestore_memory_store(
                project_id=args.project_id,
                max_local_cache=50,
                sync_on_write=True
            )
            store_type = "firestore"
            has_firestore = hasattr(memory_store, '_firestore_client') and memory_store._firestore_client is not None
            
            if has_firestore:
                print("✅ Firestore memory store initialized successfully!")
                print(f"   Project: {memory_store._firestore_client.project}")
                print(f"   Collection: {memory_store.collection_name}")
            else:
                print("⚠️  Firestore unavailable - falling back to intelligent memory store")
                store_type = "intelligent (firestore fallback)"
                
        except Exception as e:
            print(f"❌ Firestore initialization failed: {e}")
            print("   Falling back to intelligent memory store")
            memory_store = IntelligentMemoryStore()
            store_type = "intelligent (firestore failed)"
            has_firestore = False
    else:
        print("Using intelligent memory store (local only)...")
        memory_store = IntelligentMemoryStore()
        store_type = "intelligent"
        has_firestore = False
        
        if args.use_firestore and not FIRESTORE_AVAILABLE:
            print("⚠️  Firestore dependencies not available")
    
    # Set the global memory store
    set_memory_store(memory_store)
    
    print(f"Memory store type: {store_type}")
    print(f"Firestore available: {has_firestore}")
    
    try:
        # 1. Simulate agent activity to populate memory
        print_section("AGENT ACTIVITY SIMULATION")
        simulate_agent_activity(store_type)
        
        # 2. Demonstrate search capabilities
        demonstrate_search_capabilities()
        
        # 3. Demonstrate analytics and learning patterns
        demonstrate_analytics()
        
        # 4. Demonstrate memory consolidation
        demonstrate_consolidation()
        
        # 5. Demonstrate sync (if Firestore available)
        demonstrate_sync(has_firestore)
        
        # Summary
        print_section("DEMONSTRATION SUMMARY")
        
        # Get final stats
        if hasattr(memory_store, 'get_memory_stats'):
            stats = memory_store.get_memory_stats()
        else:
            stats = memory_store.get_memory_analytics()
            
        print("Final Memory Statistics:")
        print(f"  Total memories: {stats.get('total_memories', 0)}")
        print(f"  Average importance: {stats.get('average_importance', 0):.3f}")
        
        if 'type_distribution' in stats:
            print("  Memory types:")
            for mem_type, count in stats['type_distribution'].items():
                type_name = mem_type.value.upper() if hasattr(mem_type, 'value') else str(mem_type).upper()
                print(f"    {type_name}: {count}")
        
        if has_firestore:
            print(f"  Firestore connected: {stats.get('firestore_connected', False)}")
            print(f"  Local cache size: {stats.get('local_cache_size', 0)}")
            
        print("\n🎉 Persistent memory demonstration complete!")
        print("\nKey capabilities demonstrated:")
        print("  ✓ Intelligent memory classification and storage")
        print("  ✓ Semantic keyword-based search")
        print("  ✓ Cross-session analytics and insights")
        print("  ✓ Learning pattern analysis") 
        print("  ✓ Memory consolidation and optimization")
        if has_firestore:
            print("  ✓ Persistent storage with Firestore")
            print("  ✓ Cross-session memory persistence")
        else:
            print("  - Persistent storage (requires Firestore)")
            
        print("\nThis demonstrates core mother-agent capabilities:")
        print("  • Agents can learn from past experiences")
        print("  • Knowledge persists across sessions")
        print("  • Memory patterns reveal learning focus")
        print("  • Intelligent consolidation prevents bloat")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
