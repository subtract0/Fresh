#!/usr/bin/env python3
"""
Enhanced Agent System Launcher

Launches the Fresh agent system with persistent memory capabilities,
enabling agents to learn and remember across sessions.

This launcher:
- Initializes the persistent memory system (Firestore or local)
- Sets up enhanced agents with intelligent memory tools
- Provides system health monitoring and status reporting
- Handles graceful fallback for different environments

Usage:
    python launch_enhanced_agent_system.py [options]

Options:
    --use-firestore          Force Firestore usage
    --no-firestore          Force local-only memory
    --project-id PROJECT     Google Cloud project ID
    --collection NAME        Firestore collection name
    --cache-size N           Local cache size (default: 100)
    --check-health          Check memory system health
    --demo                  Run a brief demonstration

Environment Variables:
    FRESH_USE_FIRESTORE=true        Enable Firestore
    GOOGLE_CLOUD_PROJECT=project    Set project ID
    FRESH_FIRESTORE_PROJECT=proj    Override project ID
    GOOGLE_APPLICATION_CREDENTIALS  Path to service account key

Examples:
    # Auto-detect environment (recommended)
    python launch_enhanced_agent_system.py
    
    # Force Firestore with specific project
    python launch_enhanced_agent_system.py --use-firestore --project-id my-project
    
    # Local-only development mode
    python launch_enhanced_agent_system.py --no-firestore
    
    # Check system health
    python launch_enhanced_agent_system.py --check-health
"""
import argparse
import sys
import logging
import os
import threading
import time
from pathlib import Path
from typing import Dict, Any

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from ai.system.memory_integration import (
    MemoryIntegrationConfig,
    initialize_agent_memory_system,
    get_memory_system_status,
    ensure_memory_system_ready
)
from ai.agents.enhanced_agents import create_enhanced_agents, get_agent

logger = logging.getLogger(__name__)


def setup_logging(level: str = "INFO"):
    """Set up logging configuration."""
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('agent_system.log')
        ]
    )


def print_system_status(status: Dict[str, Any]):
    """Print formatted system status information."""
    print("\n🧠 AGENT MEMORY SYSTEM STATUS")
    print("=" * 50)
    
    integration = status.get("integration", {})
    health = status.get("health", {})
    
    # Integration status
    print(f"Store Type: {integration.get('store_type', 'unknown').title()}")
    print(f"Firestore Requested: {integration.get('firestore_requested', False)}")
    print(f"Firestore Available: {integration.get('firestore_available', False)}")
    print(f"Firestore Connected: {integration.get('firestore_connected', False)}")
    
    if integration.get('project_id'):
        print(f"Project ID: {integration['project_id']}")
    if integration.get('collection'):
        print(f"Collection: {integration['collection']}")
    
    # Health status
    print(f"\nHealth Status: {health.get('status', 'unknown').upper()}")
    print(f"Basic Functionality: {health.get('basic_functionality', 'unknown')}")
    
    if 'total_memories' in health:
        print(f"Total Memories: {health['total_memories']}")
    if 'local_cache_size' in health:
        print(f"Local Cache Size: {health['local_cache_size']}")
    if 'average_importance' in health:
        print(f"Average Importance: {health['average_importance']:.3f}")
    
    # Error reporting
    if integration.get('error'):
        print(f"\n❌ Integration Error: {integration['error']}")
    if health.get('error'):
        print(f"❌ Health Error: {health['error']}")


def run_memory_demo():
    """Run a brief demonstration of memory capabilities."""
    print("\n🎯 MEMORY SYSTEM DEMONSTRATION")
    print("=" * 40)
    
    try:
        from ai.memory.store import get_store
        from ai.memory.intelligent_store import IntelligentMemoryStore
        from ai.memory.firestore_store import FirestoreMemoryStore
        
        store = get_store()
        store_type = type(store).__name__
        
        print(f"Using: {store_type}")
        
        # Write some test memories
        print("\n📝 Writing test memories...")
        memories = [
            ("Goal: Demonstrate persistent memory capabilities", ["goal", "demo"]),
            ("Task: Show intelligent memory classification", ["task", "demo"]),
            ("Learned: Enhanced agents can remember across sessions", ["knowledge", "demo"]),
            ("Progress: Memory integration completed successfully", ["progress", "demo"])
        ]
        
        for content, tags in memories:
            item = store.write(content=content, tags=tags)
            print(f"  ✓ {item.id}: {content[:50]}...")
        
        # Search and retrieve
        print("\n🔍 Testing memory retrieval...")
        recent_memories = store.query(limit=5, tags=["demo"])
        print(f"Retrieved {len(recent_memories)} demo memories")
        
        # Show intelligence features if available
        if isinstance(store, (IntelligentMemoryStore, FirestoreMemoryStore)):
            print("\n🧠 Intelligent features detected:")
            
            # Show analytics
            if hasattr(store, 'get_memory_analytics'):
                stats = store.get_memory_analytics()
                print(f"  Total memories: {stats.get('total_memories', 0)}")
                print(f"  Memory types: {len(stats.get('type_distribution', {}))}")
                
            # Show enhanced memory item features
            if recent_memories:
                sample = recent_memories[0]
                if hasattr(sample, 'memory_type'):
                    print(f"  Sample classification: {sample.memory_type.value}")
                if hasattr(sample, 'importance_score'):
                    print(f"  Sample importance: {sample.importance_score:.3f}")
                if hasattr(sample, 'keywords'):
                    print(f"  Sample keywords: {sample.keywords[:3]}")
        
        print("\n✅ Memory demonstration completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()


def initialize_enhanced_agents():
    """Initialize enhanced agents with memory capabilities."""
    print("\n👥 INITIALIZING ENHANCED AGENTS")
    print("=" * 35)
    
    try:
        agents = create_enhanced_agents()
        
        for name, agent in agents.items():
            tool_count = len(agent.tools) if hasattr(agent, 'tools') else 0
            print(f"  ✓ {name}: {tool_count} tools (including memory)")
        
        print(f"\n✅ {len(agents)} enhanced agents initialized!")
        return agents
        
    except Exception as e:
        print(f"\n❌ Agent initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return None


def main():
    """Main launcher function."""
    parser = argparse.ArgumentParser(
        description="Launch Enhanced Agent System with Persistent Memory",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__.split('Examples:')[1] if 'Examples:' in __doc__ else ""
    )
    
    parser.add_argument("--use-firestore", action="store_true",
                       help="Force Firestore usage")
    parser.add_argument("--no-firestore", action="store_true", 
                       help="Force local-only memory")
    parser.add_argument("--project-id", type=str,
                       help="Google Cloud project ID")
    parser.add_argument("--collection", type=str, default="agent_memories",
                       help="Firestore collection name")
    parser.add_argument("--cache-size", type=int, default=100,
                       help="Local cache size")
    parser.add_argument("--check-health", action="store_true",
                       help="Check memory system health")
    parser.add_argument("--demo", action="store_true",
                       help="Run memory system demonstration")
    parser.add_argument("--log-level", choices=["DEBUG", "INFO", "WARNING", "ERROR"],
                       default="INFO", help="Logging level")
    
    args = parser.parse_args()
    
    # Set up logging
    setup_logging(args.log_level)
    
    print("🚀 ENHANCED AGENT SYSTEM LAUNCHER")
    print("=" * 50)
    
    try:
        # Create memory integration configuration
        config = MemoryIntegrationConfig(
            use_firestore=args.use_firestore if not args.no_firestore else False,
            project_id=args.project_id,
            collection_name=args.collection,
            max_local_cache=args.cache_size,
            sync_on_write=True,
            fallback_to_intelligent=True
        )
        
        # Initialize memory system
        print("\n🧠 Initializing Memory System...")
        init_status = initialize_agent_memory_system(config)
        
        # Get comprehensive status
        system_status = get_memory_system_status()
        print_system_status(system_status)
        
        # Handle specific operations
        if args.check_health:
            print("\n🏥 HEALTH CHECK")
            print("=" * 20)
            
            if ensure_memory_system_ready():
                print("✅ Memory system is healthy and ready")
            else:
                print("❌ Memory system health check failed")
                sys.exit(1)
            return
        
        if args.demo:
            run_memory_demo()
            return
        
        # Initialize enhanced agents
        agents = initialize_enhanced_agents()
        if not agents:
            print("❌ Failed to initialize agents")
            sys.exit(1)

        # Optionally start background documentation alignment loop (parallel)
        def _docs_alignment_loop(interval_sec: int):
            try:
                from ai.tools.docs_tools import DocsAlignmentCheck
                from ai.tools.enhanced_memory_tools import SmartWriteMemory
            except Exception as e:
                print(f"⚠️ Docs alignment tools unavailable: {e}")
                return
            last_status = None
            while True:
                try:
                    result = DocsAlignmentCheck(strict=False).run()
                    status = "FAILED" if "FAILED" in result.upper() else "PASSED"
                    if status == "FAILED":
                        # Store only failures to avoid noise
                        SmartWriteMemory(
                            content=f"Docs Alignment: {status}. Summary: {result[:500]}",
                            tags=["documentation", "alignment", "issue"]
                        ).run()
                    elif last_status == "FAILED":
                        # Store first recovery after failure
                        SmartWriteMemory(
                            content="Docs Alignment: PASSED after previous failure.",
                            tags=["documentation", "alignment", "recovered"]
                        ).run()
                    last_status = status
                except Exception as e:
                    try:
                        from ai.tools.enhanced_memory_tools import SmartWriteMemory
                        SmartWriteMemory(
                            content=f"Docs Alignment loop error: {e}",
                            tags=["documentation", "alignment", "error"]
                        ).run()
                    except Exception:
                        pass
                time.sleep(interval_sec)

        docs_enabled = os.getenv("DOCS_CHECK_ENABLED", "true").lower() not in ("0", "false", "no")
        if docs_enabled:
            try:
                interval = int(os.getenv("DOCS_CHECK_INTERVAL_SEC", "600"))
            except ValueError:
                interval = 600
            t = threading.Thread(target=_docs_alignment_loop, args=(interval,), daemon=True)
            t.start()
            print(f"📝 Documentation alignment loop started (every {interval}s)")
        
        # System ready
        print("\n🎉 SYSTEM READY")
        print("=" * 20)
        print("Enhanced agents initialized with persistent memory capabilities!")
        print("\nKey Features Available:")
        print("  🧠 Intelligent memory classification")
        print("  💾 Persistent storage across sessions")
        print("  🔍 Semantic memory search")
        print("  📊 Learning pattern analysis")
        print("  🧹 Automatic memory consolidation")
        
        if system_status["integration"].get("firestore_connected"):
            print("  ☁️  Firestore persistence enabled")
        else:
            print("  💻 Local memory store active")
        
        print("\nThe agent system is now ready for development work.")
        print("Agents will learn and remember across all sessions!")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Startup interrupted by user")
        sys.exit(1)
        
    except Exception as e:
        print(f"\n❌ System initialization failed: {e}")
        logger.exception("System initialization failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
