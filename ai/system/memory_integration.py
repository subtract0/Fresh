"""
Memory Integration System

Integrates persistent memory capabilities into agent workflows, providing
seamless initialization and configuration of the intelligent memory system.

This module handles:
- Memory store initialization and configuration
- Environment-based store selection (Firestore vs local)
- Agent workflow integration points
- Memory system health monitoring

Cross-references:
    - ADR-004: Persistent Agent Memory
    - ai/memory/firestore_store.py: Firestore implementation
    - ai/memory/intelligent_store.py: Intelligent memory features
"""
from __future__ import annotations
import os
import logging
from typing import Optional, Dict, Any

from ai.memory.store import set_memory_store, get_store
from ai.memory.intelligent_store import IntelligentMemoryStore
from ai.memory.firestore_store import create_firestore_memory_store, FIRESTORE_AVAILABLE

logger = logging.getLogger(__name__)


class MemoryIntegrationConfig:
    """Configuration for memory system integration."""
    
    def __init__(self,
                 use_firestore: bool = None,
                 project_id: Optional[str] = None,
                 collection_name: str = "agent_memories",
                 max_local_cache: int = 100,
                 sync_on_write: bool = True,
                 fallback_to_intelligent: bool = True):
        """
        Initialize memory integration configuration.
        
        Args:
            use_firestore: Whether to use Firestore (None = auto-detect from env)
            project_id: Google Cloud project ID for Firestore
            collection_name: Firestore collection name
            max_local_cache: Maximum items in local cache
            sync_on_write: Whether to sync to Firestore on every write
            fallback_to_intelligent: Whether to fallback to IntelligentMemoryStore
        """
        self.use_firestore = use_firestore
        self.project_id = project_id
        self.collection_name = collection_name
        self.max_local_cache = max_local_cache
        self.sync_on_write = sync_on_write
        self.fallback_to_intelligent = fallback_to_intelligent
        
        # Auto-detect Firestore usage from environment
        if self.use_firestore is None:
            self.use_firestore = self._should_use_firestore()
            
        # Auto-detect project ID from environment
        if self.project_id is None:
            self.project_id = self._get_project_id()
    
    def _should_use_firestore(self) -> bool:
        """Determine if Firestore should be used based on environment."""
        # Use Firestore if explicitly enabled
        if os.getenv("FRESH_USE_FIRESTORE", "").lower() in ("true", "1", "yes"):
            return True
            
        # Use Firestore if project ID is configured
        if os.getenv("GOOGLE_CLOUD_PROJECT") or os.getenv("GCLOUD_PROJECT"):
            return True
            
        # Use Firestore if credentials are available
        if os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
            return True
            
        # Default to local-only for development
        return False
    
    def _get_project_id(self) -> Optional[str]:
        """Get Google Cloud project ID from environment."""
        return (
            os.getenv("FRESH_FIRESTORE_PROJECT") or 
            os.getenv("GOOGLE_CLOUD_PROJECT") or
            os.getenv("GCLOUD_PROJECT")
        )


class MemoryIntegrationManager:
    """Manages memory system integration for agent workflows."""
    
    def __init__(self, config: Optional[MemoryIntegrationConfig] = None):
        """
        Initialize memory integration manager.
        
        Args:
            config: Memory integration configuration (auto-created if None)
        """
        self.config = config or MemoryIntegrationConfig()
        self._memory_store = None
        self._integration_status = {}
        
    def initialize_memory_system(self) -> Dict[str, Any]:
        """
        Initialize the memory system based on configuration.
        
        Returns:
            dict: Status information about the initialized memory system
        """
        try:
            status = {
                "firestore_requested": self.config.use_firestore,
                "firestore_available": FIRESTORE_AVAILABLE,
                "firestore_connected": False,
                "store_type": None,
                "project_id": self.config.project_id,
                "collection": self.config.collection_name,
                "error": None
            }
            
            if self.config.use_firestore and FIRESTORE_AVAILABLE:
                # Attempt Firestore initialization
                try:
                    logger.info("Initializing Firestore memory store...")
                    memory_store = create_firestore_memory_store(
                        project_id=self.config.project_id,
                        collection_name=self.config.collection_name,
                        max_local_cache=self.config.max_local_cache,
                        sync_on_write=self.config.sync_on_write
                    )
                    
                    # Check if Firestore actually connected
                    if hasattr(memory_store, '_firestore_client') and memory_store._firestore_client:
                        status["firestore_connected"] = True
                        status["store_type"] = "firestore"
                        status["project_id"] = memory_store._firestore_client.project
                        logger.info(f"✅ Firestore memory store initialized successfully!")
                        logger.info(f"   Project: {status['project_id']}")
                        logger.info(f"   Collection: {self.config.collection_name}")
                    else:
                        # Firestore creation succeeded but client not connected
                        status["store_type"] = "intelligent"
                        logger.warning("⚠️  Firestore store created but not connected - using intelligent store")
                        
                    self._memory_store = memory_store
                    
                except Exception as e:
                    status["error"] = str(e)
                    logger.error(f"❌ Firestore initialization failed: {e}")
                    
                    if self.config.fallback_to_intelligent:
                        logger.info("   Falling back to intelligent memory store")
                        self._memory_store = IntelligentMemoryStore()
                        status["store_type"] = "intelligent"
                    else:
                        raise
                        
            else:
                # Use intelligent memory store
                if self.config.use_firestore and not FIRESTORE_AVAILABLE:
                    logger.warning("⚠️  Firestore requested but dependencies not available")
                
                logger.info("Using intelligent memory store (local only)")
                self._memory_store = IntelligentMemoryStore()
                status["store_type"] = "intelligent"
            
            # Set the global memory store
            set_memory_store(self._memory_store)
            
            # Update integration status
            self._integration_status = status
            
            logger.info(f"Memory system initialized: {status['store_type']}")
            return status
            
        except Exception as e:
            logger.error(f"Memory system initialization failed: {e}")
            status["error"] = str(e)
            self._integration_status = status
            raise
    
    def get_memory_store(self):
        """Get the current memory store instance."""
        if self._memory_store is None:
            self.initialize_memory_system()
        return self._memory_store
    
    def get_integration_status(self) -> Dict[str, Any]:
        """Get current integration status."""
        return self._integration_status.copy()
    
    def health_check(self) -> Dict[str, Any]:
        """
        Perform health check on the memory system.
        
        Returns:
            dict: Health status including connectivity and performance metrics
        """
        try:
            store = self.get_memory_store()
            health = {
                "status": "healthy",
                "store_type": type(store).__name__,
                "error": None
            }
            
            # Test basic functionality
            test_item = store.write(content="Health check test", tags=["health_check"])
            retrieved_items = store.query(limit=1, tags=["health_check"])
            
            if retrieved_items and retrieved_items[0].id == test_item.id:
                health["basic_functionality"] = "working"
            else:
                health["basic_functionality"] = "failed"
                health["status"] = "degraded"
            
            # Get store-specific stats
            if hasattr(store, 'get_memory_stats'):
                # Firestore or enhanced store
                stats = store.get_memory_stats()
                health.update({
                    "total_memories": stats.get("total_memories", 0),
                    "firestore_connected": stats.get("firestore_connected", False),
                    "local_cache_size": stats.get("local_cache_size", 0)
                })
            elif hasattr(store, 'get_memory_analytics'):
                # Intelligent store
                stats = store.get_memory_analytics()
                health.update({
                    "total_memories": stats.get("total_memories", 0),
                    "average_importance": stats.get("average_importance", 0)
                })
            
            return health
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "store_type": type(self._memory_store).__name__ if self._memory_store else "none"
            }


# Global memory integration manager
_global_manager: Optional[MemoryIntegrationManager] = None


def get_memory_integration_manager(config: Optional[MemoryIntegrationConfig] = None) -> MemoryIntegrationManager:
    """
    Get the global memory integration manager.
    
    Args:
        config: Configuration for new manager (ignored if manager exists)
        
    Returns:
        MemoryIntegrationManager instance
    """
    global _global_manager
    
    if _global_manager is None:
        _global_manager = MemoryIntegrationManager(config)
    
    return _global_manager


def initialize_agent_memory_system(config: Optional[MemoryIntegrationConfig] = None) -> Dict[str, Any]:
    """
    Initialize the memory system for agent workflows.
    
    This is the main entry point for integrating persistent memory into
    agent workflows. It handles environment detection, store selection,
    and graceful fallback.
    
    Args:
        config: Memory integration configuration
        
    Returns:
        dict: Status information about initialization
        
    Examples:
        Basic initialization:
            status = initialize_agent_memory_system()
            
        With explicit configuration:
            config = MemoryIntegrationConfig(
                use_firestore=True,
                project_id="my-project",
                max_local_cache=200
            )
            status = initialize_agent_memory_system(config)
    """
    manager = get_memory_integration_manager(config)
    return manager.initialize_memory_system()


def get_memory_system_status() -> Dict[str, Any]:
    """Get current memory system status and health information."""
    manager = get_memory_integration_manager()
    
    status = manager.get_integration_status()
    health = manager.health_check()
    
    return {
        "integration": status,
        "health": health
    }


def ensure_memory_system_ready() -> bool:
    """
    Ensure the memory system is initialized and ready for use.
    
    Returns:
        bool: True if memory system is ready, False otherwise
    """
    try:
        manager = get_memory_integration_manager()
        store = manager.get_memory_store()
        
        # Test basic functionality
        test_write = store.write(content="System readiness test", tags=["system_test"])
        test_read = store.query(limit=1, tags=["system_test"])
        
        return len(test_read) > 0 and test_read[0].id == test_write.id
        
    except Exception as e:
        logger.error(f"Memory system readiness check failed: {e}")
        return False
