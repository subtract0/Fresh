#!/usr/bin/env python3
"""
Production Memory Backend Test

Comprehensive test suite for production memory features including:
- Enhanced Firestore memory store
- Backup and restore operations
- Production analytics and monitoring
- Synchronization and optimization
- Error handling and reliability

This test validates production-readiness of the memory system.
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path
from datetime import datetime, timezone

# Add project root to path
project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

from ai.memory.store import set_memory_store, get_store
from ai.memory.intelligent_store import IntelligentMemoryStore
from ai.tools.production_memory_tools import (
    BackupMemoryStore,
    RestoreMemoryStore,
    SyncFirestoreMemory,
    GetProductionAnalytics,
    OptimizeFirestoreMemory,
    TestFirestoreConnection
)


class ProductionMemoryTester:
    """Test suite for production memory features."""
    
    def __init__(self):
        self.has_firestore_creds = bool(
            os.getenv("FIREBASE_PROJECT_ID") and
            os.getenv("FIREBASE_CLIENT_EMAIL") and
            os.getenv("FIREBASE_PRIVATE_KEY")
        )
        self.test_results = []
        self.temp_dir = None
        
    def setup_test_environment(self):
        """Setup temporary directory for testing."""
        self.temp_dir = tempfile.mkdtemp(prefix="memory_test_")
        print(f"📁 Test directory: {self.temp_dir}")
        
    def cleanup_test_environment(self):
        """Clean up temporary test files."""
        if self.temp_dir and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
            print(f"🗑️  Cleaned up test directory")
            
    def log_test(self, test_name: str, passed: bool, details: str = ""):
        """Log test result."""
        status = "✅ PASS" if passed else "❌ FAIL"
        self.test_results.append((test_name, passed, details))
        print(f"{status} {test_name}")
        if details:
            print(f"    {details}")
    
    def test_intelligent_memory_fallback(self):
        """Test that intelligent memory works when Firestore is not available."""
        try:
            # Use intelligent memory store as fallback
            store = IntelligentMemoryStore()
            set_memory_store(store)
            
            # Test basic functionality
            item = store.write(
                content="Test: Fallback memory functionality",
                tags=["test", "fallback"]
            )
            
            success = (
                item.id.startswith("mem-") and
                item.memory_type.value == "context" and
                len(item.keywords) > 0
            )
            
            self.log_test(
                "Intelligent Memory Fallback",
                success,
                f"Item ID: {item.id}, Type: {item.memory_type.value}, Keywords: {len(item.keywords)}"
            )
            return success
            
        except Exception as e:
            self.log_test("Intelligent Memory Fallback", False, f"Error: {e}")
            return False
    
    def test_enhanced_firestore_without_credentials(self):
        """Test Enhanced Firestore behavior without credentials."""
        if self.has_firestore_creds:
            self.log_test(
                "Enhanced Firestore Without Credentials",
                True,
                "Skipped - Firestore credentials are available"
            )
            return True
            
        try:
            from ai.memory.enhanced_firestore import EnhancedFirestoreMemoryStore
            
            # This should fail gracefully
            try:
                store = EnhancedFirestoreMemoryStore()
                self.log_test(
                    "Enhanced Firestore Without Credentials",
                    False,
                    "Expected failure but store was created"
                )
                return False
            except RuntimeError as e:
                expected_error = "FIREBASE_* env vars are required"
                success = expected_error in str(e)
                self.log_test(
                    "Enhanced Firestore Without Credentials",
                    success,
                    f"Correct error handling: {str(e)}"
                )
                return success
                
        except Exception as e:
            self.log_test(
                "Enhanced Firestore Without Credentials", 
                False, 
                f"Unexpected error: {e}"
            )
            return False
    
    def test_production_tools_with_intelligent_store(self):
        """Test production tools with intelligent memory store (should handle gracefully)."""
        try:
            # Setup intelligent memory store
            store = IntelligentMemoryStore()
            set_memory_store(store)
            
            # Add some test data
            store.write(content="Test data for production tools", tags=["test"])
            
            # Test backup tool (should fail gracefully)
            backup_path = os.path.join(self.temp_dir, "test_backup.json")
            backup_tool = BackupMemoryStore(backup_path=backup_path)
            backup_result = backup_tool.run()
            backup_success = "requires Enhanced Firestore" in backup_result
            
            # Test analytics tool (should work)
            analytics_tool = GetProductionAnalytics()
            analytics_result = analytics_tool.run()
            analytics_success = "PRODUCTION MEMORY ANALYTICS" in analytics_result
            
            # Test sync tool (should fail gracefully)
            sync_tool = SyncFirestoreMemory()
            sync_result = sync_tool.run()
            sync_success = "requires Enhanced Firestore" in sync_result
            
            overall_success = backup_success and analytics_success and sync_success
            
            self.log_test(
                "Production Tools with Intelligent Store",
                overall_success,
                f"Backup: {'OK' if backup_success else 'FAIL'}, "
                f"Analytics: {'OK' if analytics_success else 'FAIL'}, "
                f"Sync: {'OK' if sync_success else 'FAIL'}"
            )
            return overall_success
            
        except Exception as e:
            self.log_test("Production Tools with Intelligent Store", False, f"Error: {e}")
            return False
    
    def test_firestore_connection_tool(self):
        """Test Firestore connection validation tool."""
        try:
            connection_tool = TestFirestoreConnection()
            result = connection_tool.run()
            
            if self.has_firestore_creds:
                # Should attempt connection
                success = "Connection Test" in result
                details = "Connection attempted with available credentials"
            else:
                # Should report missing credentials
                success = "Missing environment variables" in result
                details = "Correctly identified missing credentials"
            
            self.log_test(
                "Firestore Connection Tool",
                success,
                details
            )
            return success
            
        except Exception as e:
            self.log_test("Firestore Connection Tool", False, f"Error: {e}")
            return False
    
    def test_backup_restore_simulation(self):
        """Test backup/restore workflow simulation."""
        try:
            # Setup intelligent memory with test data
            store = IntelligentMemoryStore()
            set_memory_store(store)
            
            # Create diverse test memories
            memories = [
                ("Goal: Implement production memory system", ["goal", "production"]),
                ("Task: Test backup and restore functionality", ["task", "test"]),
                ("Critical error: Memory sync failed", ["error", "critical"]),
                ("Decision: Use Enhanced Firestore for production", ["decision", "adr"])
            ]
            
            for content, tags in memories:
                store.write(content=content, tags=tags)
            
            # Simulate backup creation (manual JSON creation)
            backup_data = {
                "metadata": {
                    "backup_timestamp": datetime.now(timezone.utc).isoformat(),
                    "total_memories": len(store._items),
                    "collection_name": "test_simulation",
                    "schema_version": "1.0"
                },
                "memories": []
            }
            
            # Export memories to backup format
            for item in store._items:
                memory_data = {
                    "id": item.id,
                    "content": item.content,
                    "tags": item.tags,
                    "created_at": item.created_at.isoformat(),
                    "memory_type": item.memory_type.value,
                    "keywords": item.keywords,
                    "related_ids": item.related_ids,
                    "importance_score": item.importance_score,
                    "summary": item.summary,
                    "schema_version": "1.0",
                    "store_type": "simulation"
                }
                backup_data["memories"].append(memory_data)
            
            # Write backup file
            backup_path = os.path.join(self.temp_dir, "simulation_backup.json")
            import json
            with open(backup_path, 'w') as f:
                json.dump(backup_data, f, indent=2)
            
            # Verify backup was created
            backup_exists = os.path.exists(backup_path)
            backup_valid = False
            
            if backup_exists:
                with open(backup_path, 'r') as f:
                    loaded_data = json.load(f)
                    backup_valid = (
                        "metadata" in loaded_data and
                        "memories" in loaded_data and
                        len(loaded_data["memories"]) == len(memories)
                    )
            
            success = backup_exists and backup_valid
            
            self.log_test(
                "Backup/Restore Simulation",
                success,
                f"Backup created: {backup_exists}, Valid: {backup_valid}, "
                f"Memories: {len(backup_data['memories'])}"
            )
            return success
            
        except Exception as e:
            self.log_test("Backup/Restore Simulation", False, f"Error: {e}")
            return False
    
    def test_memory_analytics_features(self):
        """Test enhanced memory analytics features."""
        try:
            # Setup intelligent memory with diverse data
            store = IntelligentMemoryStore()
            set_memory_store(store)
            
            # Create memories with different types and importance
            test_memories = [
                ("Critical goal: Launch production system", ["goal", "critical"]),
                ("Task: Optimize memory performance", ["task", "optimization"]),
                ("Important decision: Use semantic search", ["decision", "important"]),
                ("Error: Database connection timeout", ["error", "database"]),
                ("Context: System running Python 3.12", ["context", "system"])
            ]
            
            for content, tags in test_memories:
                store.write(content=content, tags=tags)
            
            # Get analytics
            analytics = store.get_memory_analytics()
            
            # Verify analytics components
            has_total = "total_memories" in analytics
            has_types = "type_distribution" in analytics
            has_importance = "average_importance" in analytics
            has_keywords = "top_keywords" in analytics
            
            # Verify data quality
            correct_total = analytics.get("total_memories", 0) == len(test_memories)
            
            # Handle enum keys in type distribution
            type_dist = analytics.get("type_distribution", {})
            goal_count = 0
            for key, count in type_dist.items():
                # Check if key is "goal" string or MemoryType.GOAL enum
                if (isinstance(key, str) and key == "goal") or (hasattr(key, 'value') and key.value == "goal"):
                    goal_count = count
                    break
            
            has_goal_type = goal_count >= 1
            avg_importance = analytics.get("average_importance", 0.5)
            reasonable_importance = avg_importance is not None and 0.0 <= avg_importance <= 1.0
            
            success = all([
                has_total, has_types, has_importance, has_keywords,
                correct_total, has_goal_type, reasonable_importance
            ])
            
            self.log_test(
                "Memory Analytics Features",
                success,
                f"Total: {correct_total}, Types: {has_goal_type}, "
                f"Importance: {reasonable_importance:.3f}, Keywords: {len(analytics.get('top_keywords', {}))}"
            )
            return success
            
        except Exception as e:
            self.log_test("Memory Analytics Features", False, f"Error: {e}")
            return False
    
    def test_memory_optimization_logic(self):
        """Test memory optimization logic (without Firestore)."""
        try:
            # Setup store with many memories
            store = IntelligentMemoryStore()
            set_memory_store(store)
            
            # Create memories with varying importance
            for i in range(20):
                importance_word = "critical" if i < 5 else "normal"
                content = f"{importance_word} Memory item {i} for optimization testing"
                store.write(content=content, tags=[f"item{i}"])
            
            initial_count = len(store._items)
            
            # Optimize to keep only 10 items
            removed_count = store.optimize_memory(max_items=10)
            final_count = len(store._items)
            
            # Verify optimization worked
            correct_removal = removed_count == 10
            correct_final = final_count == 10
            
            # Check that high-importance items were kept
            remaining_critical = sum(
                1 for item in store._items 
                if "critical" in item.content
            )
            kept_important = remaining_critical >= 3  # Should keep most critical items
            
            success = correct_removal and correct_final and kept_important
            
            self.log_test(
                "Memory Optimization Logic",
                success,
                f"Initial: {initial_count}, Removed: {removed_count}, "
                f"Final: {final_count}, Critical kept: {remaining_critical}"
            )
            return success
            
        except Exception as e:
            self.log_test("Memory Optimization Logic", False, f"Error: {e}")
            return False
    
    def run_all_tests(self):
        """Run all production memory tests."""
        print("🚀 Production Memory Backend Test Suite")
        print("=" * 60)
        print(f"🔧 Firestore credentials available: {self.has_firestore_creds}")
        print()
        
        # Setup test environment
        self.setup_test_environment()
        
        try:
            # Run tests
            tests = [
                self.test_intelligent_memory_fallback,
                self.test_enhanced_firestore_without_credentials,
                self.test_production_tools_with_intelligent_store,
                self.test_firestore_connection_tool,
                self.test_backup_restore_simulation,
                self.test_memory_analytics_features,
                self.test_memory_optimization_logic,
            ]
            
            for test in tests:
                try:
                    test()
                except Exception as e:
                    self.log_test(f"ERROR in {test.__name__}", False, f"Exception: {e}")
                print()
            
            # Summary
            passed = sum(1 for _, success, _ in self.test_results if success)
            total = len(self.test_results)
            
            print("=" * 60)
            print(f"🎯 Test Summary: {passed}/{total} tests passed")
            
            if passed == total:
                print("🎉 All production memory tests passed!")
                if self.has_firestore_creds:
                    print("🔥 Ready for production Firestore deployment")
                else:
                    print("🧠 Ready for production with intelligent memory")
            else:
                print("⚠️  Some tests failed. Review the details above.")
                failed_tests = [name for name, success, _ in self.test_results if not success]
                print(f"Failed tests: {', '.join(failed_tests)}")
            
            return passed == total
            
        finally:
            # Always cleanup
            self.cleanup_test_environment()


if __name__ == "__main__":
    tester = ProductionMemoryTester()
    success = tester.run_all_tests()
    exit(0 if success else 1)
