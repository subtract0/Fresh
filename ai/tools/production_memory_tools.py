"""
Production Memory Tools

Advanced memory management tools for production environments including
backup/restore, Firestore synchronization, and enhanced analytics.

These tools extend the basic memory capabilities with production-grade
features for data protection, monitoring, and optimization.
"""
from __future__ import annotations
import os
from datetime import datetime
from typing import Any, Dict
from pydantic import BaseModel, Field

from agency_swarm import BaseTool
from ai.memory.store import get_store
from ai.memory.enhanced_firestore import EnhancedFirestoreMemoryStore


class BackupMemoryStore(BaseTool):
    """
    Backup all memories to a JSON file for data protection.
    
    Creates a complete backup of the memory store including metadata,
    memory content, classifications, and relationships.
    """
    
    backup_path: str = Field(
        description="Path where backup file should be saved (e.g., 'backup/memory-2024-01-01.json')"
    )
    
    def run(self) -> str:
        """Execute memory backup operation."""
        try:
            store = get_store()
            
            if not isinstance(store, EnhancedFirestoreMemoryStore):
                return "❌ Backup requires Enhanced Firestore Memory Store"
            
            # Ensure backup directory exists
            os.makedirs(os.path.dirname(self.backup_path), exist_ok=True)
            
            # Perform backup
            backup_metadata = store.backup_memories(self.backup_path)
            
            result = f"""✅ Memory Backup Complete

📁 Backup File: {self.backup_path}
📊 Backup Statistics:
   • Total Memories: {backup_metadata['total_memories']}
   • Backup Timestamp: {backup_metadata['backup_timestamp']}
   • Collection: {backup_metadata['collection_name']}
   • Schema Version: {backup_metadata['schema_version']}

💡 Use RestoreMemoryStore to restore from this backup."""
            
            return result
            
        except Exception as e:
            return f"❌ Backup failed: {str(e)}"


class RestoreMemoryStore(BaseTool):
    """
    Restore memories from a backup file.
    
    Restores memory data from a JSON backup file, optionally clearing
    existing memories first.
    """
    
    backup_path: str = Field(
        description="Path to backup file to restore from"
    )
    clear_existing: bool = Field(
        default=False,
        description="Whether to clear existing memories before restoring (default: False)"
    )
    
    def run(self) -> str:
        """Execute memory restore operation."""
        try:
            store = get_store()
            
            if not isinstance(store, EnhancedFirestoreMemoryStore):
                return "❌ Restore requires Enhanced Firestore Memory Store"
            
            if not os.path.exists(self.backup_path):
                return f"❌ Backup file not found: {self.backup_path}"
            
            # Perform restore
            restore_metadata = store.restore_memories(
                backup_path=self.backup_path,
                clear_existing=self.clear_existing
            )
            
            result = f"""✅ Memory Restore Complete

📁 Backup File: {restore_metadata['backup_file']}  
📊 Restore Statistics:
   • Restored: {restore_metadata['restored_count']} memories
   • Failed: {restore_metadata['failed_count']} memories
   • Total Memories: {restore_metadata['total_memories']}
   • Restore Timestamp: {restore_metadata['restore_timestamp']}
   • Clear Existing: {'Yes' if self.clear_existing else 'No'}

{'⚠️  Some memories failed to restore - check logs' if restore_metadata['failed_count'] > 0 else '🎉 All memories restored successfully'}"""
            
            return result
            
        except Exception as e:
            return f"❌ Restore failed: {str(e)}"


class SyncFirestoreMemory(BaseTool):
    """
    Synchronize local memory with Firestore backend.
    
    Ensures consistency between local memory cache and Firestore
    by syncing missing memories in both directions.
    """
    
    def run(self) -> str:
        """Execute Firestore synchronization."""
        try:
            store = get_store()
            
            if not isinstance(store, EnhancedFirestoreMemoryStore):
                return "❌ Sync requires Enhanced Firestore Memory Store"
            
            # Perform synchronization
            sync_stats = store.sync_with_firestore()
            
            if "error" in sync_stats:
                return f"❌ Sync failed: {sync_stats['error']}"
            
            result = f"""✅ Firestore Sync Complete

📊 Sync Statistics:
   • Local Memories: {sync_stats['local_count']}
   • Firestore Memories: {sync_stats['firestore_count']}
   • Missing in Local: {sync_stats['missing_in_local']}
   • Missing in Firestore: {sync_stats['missing_in_firestore']}
   • Successfully Synced: {sync_stats['synced']}
   • Failed: {sync_stats['failed']}

{'🎯 Memory stores are now in sync' if sync_stats['synced'] > 0 else '✅ Memory stores were already in sync'}
{'⚠️  Some sync operations failed - check logs' if sync_stats['failed'] > 0 else ''}"""
            
            return result
            
        except Exception as e:
            return f"❌ Sync failed: {str(e)}"


class GetProductionAnalytics(BaseTool):
    """
    Get comprehensive production analytics for memory usage.
    
    Provides detailed insights into memory usage, Firestore sync status,
    and production metrics for monitoring and optimization.
    """
    
    def run(self) -> str:
        """Get production memory analytics."""
        try:
            store = get_store()
            
            if isinstance(store, EnhancedFirestoreMemoryStore):
                analytics = store.get_production_analytics()
            else:
                # Fallback to basic analytics for non-production stores
                analytics = store.get_memory_analytics()
            
            # Format the analytics report
            result = f"""📊 PRODUCTION MEMORY ANALYTICS
========================================

📈 Basic Metrics:
   • Total Memories: {analytics.get('total_memories', 0)}
   • Average Importance: {analytics.get('average_importance', 0):.3f}

🏷️  Memory Types:
"""
            
            type_dist = analytics.get('type_distribution', {})
            for memory_type, count in type_dist.items():
                # Handle both string and enum types
                type_name = memory_type.upper() if isinstance(memory_type, str) else str(memory_type).upper()
                result += f"   • {type_name}: {count}\\n"
            
            result += f"""
🔍 Top Keywords:
"""
            top_keywords = analytics.get('top_keywords', {})
            for keyword, count in list(top_keywords.items())[:10]:
                result += f"   • {keyword}: {count}\\n"
            
            # Add production metrics if available
            if 'production_metrics' in analytics:
                prod_metrics = analytics['production_metrics']
                if 'error' not in prod_metrics:
                    result += f"""
🔥 Firestore Metrics:
   • Firestore Count: {prod_metrics.get('firestore_memory_count', 0)}
   • Local Count: {prod_metrics.get('local_memory_count', 0)}
   • Sync Status: {prod_metrics.get('sync_status', 'unknown').upper()}
   • Collection: {prod_metrics.get('collection_name', 'unknown')}
   • Last Check: {prod_metrics.get('last_check', 'unknown')}
"""
                else:
                    result += f"""
⚠️  Firestore Metrics: {prod_metrics['error']}
"""
            
            result += f"""
⏰ Recent Activity: {analytics.get('recent_activity', 0)} memories in last hour

💡 Recommendations:
{'   • Consider memory optimization if total > 1000' if analytics.get('total_memories', 0) > 1000 else '   • Memory usage is within optimal range'}
{'   • Sync required - counts do not match' if analytics.get('production_metrics', {}).get('sync_status') == 'out_of_sync' else '   • Memory stores are in sync'}"""
            
            return result
            
        except Exception as e:
            return f"❌ Analytics failed: {str(e)}"


class OptimizeFirestoreMemory(BaseTool):
    """
    Optimize Firestore memory by removing low-importance items.
    
    Removes old, low-importance memories from both local cache and
    Firestore to maintain optimal performance.
    """
    
    max_items: int = Field(
        default=1000,
        description="Maximum number of memories to keep after optimization"
    )
    
    def run(self) -> str:
        """Execute Firestore memory optimization."""
        try:
            store = get_store()
            
            if not isinstance(store, EnhancedFirestoreMemoryStore):
                return "❌ Optimization requires Enhanced Firestore Memory Store"
            
            # Perform optimization
            opt_stats = store.optimize_firestore_memory(max_items=self.max_items)
            
            result = f"""✅ Firestore Memory Optimization Complete

🧹 Optimization Statistics:
   • Target Max Items: {self.max_items}
   • Items Removed: {opt_stats['removed']}
   • Items Kept: {opt_stats['kept']}
   • Failed Deletions: {opt_stats['failed']}
   • Total Processed: {opt_stats['total_processed']}

{'🎯 Optimization successful - memory usage optimized' if opt_stats['removed'] > 0 else '✅ No optimization needed - memory usage already optimal'}
{'⚠️  Some deletions failed - check logs' if opt_stats['failed'] > 0 else ''}

💡 Low-importance and old memories have been removed to improve performance."""
            
            return result
            
        except Exception as e:
            return f"❌ Optimization failed: {str(e)}"


class TestFirestoreConnection(BaseTool):
    """
    Test connection to Enhanced Firestore Memory Store.
    
    Validates that Firestore credentials and connection are working properly
    for production memory operations.
    """
    
    def run(self) -> str:
        """Test Firestore connection and setup."""
        try:
            # Check environment variables
            required_vars = ["FIREBASE_PROJECT_ID", "FIREBASE_CLIENT_EMAIL", "FIREBASE_PRIVATE_KEY"]
            missing_vars = [var for var in required_vars if not os.getenv(var)]
            
            if missing_vars:
                return f"""❌ Firestore Connection Test Failed

Missing environment variables:
{chr(10).join(f'   • {var}' for var in missing_vars)}

Please set these environment variables for Firestore integration."""
            
            # Try to create Enhanced Firestore store
            try:
                from ai.memory.enhanced_firestore import EnhancedFirestoreMemoryStore
                test_store = EnhancedFirestoreMemoryStore("connection_test")
                
                # Test write operation
                test_item = test_store.write(
                    content="Connection test: Enhanced Firestore working correctly",
                    tags=["test", "connection"]
                )
                
                # Test read operation
                analytics = test_store.get_production_analytics()
                
                # Cleanup test item
                test_store.optimize_firestore_memory(max_items=0)
                
                return f"""✅ Firestore Connection Test Successful

🔥 Connection Details:
   • Project ID: {os.getenv('FIREBASE_PROJECT_ID')}
   • Collection: {test_store.collection_name}
   • Test Write: ✅ Success
   • Test Read: ✅ Success  
   • Test Analytics: ✅ Success

🎉 Enhanced Firestore Memory Store is ready for production use!"""
                
            except Exception as e:
                return f"""❌ Firestore Connection Test Failed

🔥 Connection Error: {str(e)}

Please check:
   • Firebase credentials are valid
   • Project has Firestore enabled
   • Network connectivity to Google Cloud"""
            
        except Exception as e:
            return f"❌ Connection test failed: {str(e)}"
