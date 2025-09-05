"""
Integration tests for FirestoreMemoryStore cross-session persistence.
Tests that memory truly persists across different sessions.
"""

import pytest
import uuid
import time
from pathlib import Path
from typing import Optional

from ai.memory.firestore_store import FirestoreMemoryStore
from ai.memory.intelligent_store import MemoryType


class TestFirestoreCrossSession:
    """Test cross-session persistence of Firestore memory."""
    
    @pytest.fixture
    def unique_session_id(self):
        """Generate unique session ID for testing."""
        return f"test_session_{uuid.uuid4().hex[:8]}"
    
    @pytest.fixture
    def firestore_store(self):
        """Create FirestoreMemoryStore instance."""
        # This will use emulator if FIRESTORE_EMULATOR_HOST is set
        return FirestoreMemoryStore()
    
    def test_memory_persists_across_sessions(self, firestore_store, unique_session_id):
        """Test that memory written in one session can be read in another."""
        # Session 1: Write memory
        test_content = f"Test memory from {unique_session_id}"
        test_tags = ["test", "cross-session", unique_session_id]
        
        memory_id = firestore_store.write(
            content=test_content,
            memory_type=MemoryType.KNOWLEDGE,
            tags=test_tags
        )
        
        assert memory_id is not None
        
        # Simulate session end
        del firestore_store
        
        # Session 2: Create new store instance (new session)
        new_store = FirestoreMemoryStore()
        
        # Query for the memory
        results = new_store.query(tags=[unique_session_id])
        
        assert len(results) > 0
        assert results[0].content == test_content
        assert unique_session_id in results[0].tags
        
    def test_learning_patterns_persist(self, firestore_store, unique_session_id):
        """Test that learned patterns are available in future sessions."""
        # Session 1: Record multiple similar successes
        for i in range(3):
            firestore_store.write(
                content=f"Successfully fixed type error by adding type hints",
                memory_type=MemoryType.KNOWLEDGE,
                tags=["pattern", "typescript", "success", unique_session_id],
                metadata={
                    "task": "fix_type_error",
                    "approach": "add_type_hints",
                    "success": True,
                    "iteration": i
                }
            )
        
        # Simulate session end
        del firestore_store
        
        # Session 2: New store should find the pattern
        new_store = FirestoreMemoryStore()
        
        # Query for learned patterns
        patterns = new_store.query(
            memory_type=MemoryType.KNOWLEDGE,
            tags=["pattern", "typescript", unique_session_id]
        )
        
        assert len(patterns) == 3
        for pattern in patterns:
            assert pattern.metadata.get("success") == True
            assert pattern.metadata.get("approach") == "add_type_hints"
    
    def test_agent_memory_accumulation(self, firestore_store, unique_session_id):
        """Test that agent memories accumulate over multiple sessions."""
        agent_id = f"test_agent_{unique_session_id}"
        
        # Session 1: Agent learns something
        firestore_store.write(
            content="Learned: Use async/await for API calls",
            memory_type=MemoryType.KNOWLEDGE,
            tags=["agent", agent_id],
            metadata={"agent_id": agent_id, "session": 1}
        )
        
        # Session 2: Agent learns more
        del firestore_store
        store_session2 = FirestoreMemoryStore()
        store_session2.write(
            content="Learned: Add retry logic for network failures",
            memory_type=MemoryType.KNOWLEDGE,
            tags=["agent", agent_id],
            metadata={"agent_id": agent_id, "session": 2}
        )
        
        # Session 3: Agent recalls all learning
        del store_session2
        store_session3 = FirestoreMemoryStore()
        
        all_learning = store_session3.query(tags=[agent_id])
        
        assert len(all_learning) == 2
        contents = [m.content for m in all_learning]
        assert "async/await" in " ".join(contents)
        assert "retry logic" in " ".join(contents)
    
    def test_memory_search_across_sessions(self, firestore_store, unique_session_id):
        """Test that semantic search works across session boundaries."""
        # Session 1: Write various memories
        memories = [
            ("Python type hints improve code quality", ["python", "types"]),
            ("TypeScript interfaces define contracts", ["typescript", "types"]),
            ("Rust ownership prevents memory bugs", ["rust", "memory"]),
        ]
        
        for content, tags in memories:
            firestore_store.write(
                content=content,
                memory_type=MemoryType.KNOWLEDGE,
                tags=tags + [unique_session_id]
            )
        
        # Session 2: Search for type-related memories
        del firestore_store
        new_store = FirestoreMemoryStore()
        
        # Search by keyword
        type_memories = new_store.query(
            keywords=["type", "types"],
            tags=[unique_session_id]
        )
        
        assert len(type_memories) >= 2
        contents = " ".join([m.content for m in type_memories])
        assert "Python" in contents or "TypeScript" in contents
    
    def test_memory_consolidation_cross_session(self, firestore_store, unique_session_id):
        """Test that memory consolidation works across sessions."""
        # Session 1: Write many similar memories
        for i in range(10):
            firestore_store.write(
                content=f"Fixed bug #{i} in authentication",
                memory_type=MemoryType.TASK,
                tags=["bug", "auth", unique_session_id],
                metadata={"bug_id": i}
            )
        
        # Session 2: Consolidate memories
        del firestore_store
        new_store = FirestoreMemoryStore()
        
        # Get all auth bugs
        auth_bugs = new_store.query(tags=["auth", unique_session_id])
        
        # Should be able to see pattern
        assert len(auth_bugs) == 10
        
        # Consolidate into pattern
        pattern = new_store.write(
            content="Pattern: Authentication bugs are common, need better testing",
            memory_type=MemoryType.KNOWLEDGE,
            tags=["pattern", "auth", unique_session_id],
            metadata={
                "derived_from": len(auth_bugs),
                "consolidated": True
            }
        )
        
        # Session 3: Verify consolidation
        del new_store
        final_store = FirestoreMemoryStore()
        
        patterns = final_store.query(
            memory_type=MemoryType.KNOWLEDGE,
            tags=["pattern", unique_session_id]
        )
        
        assert len(patterns) > 0
        assert patterns[0].metadata.get("consolidated") == True


@pytest.mark.docker
class TestFirestoreWithDocker:
    """Tests that require Docker Firestore emulator."""
    
    @pytest.fixture(scope="class")
    def docker_firestore(self):
        """Ensure Docker Firestore emulator is running."""
        import subprocess
        import os
        
        # Check if emulator is already running
        try:
            # This will be set by docker-compose
            if "FIRESTORE_EMULATOR_HOST" in os.environ:
                yield
                return
        except:
            pass
        
        # Start emulator with docker-compose
        compose_file = Path(__file__).parent.parent.parent / "docker-compose.yml"
        if not compose_file.exists():
            pytest.skip("docker-compose.yml not found")
        
        try:
            subprocess.run(
                ["docker-compose", "up", "-d", "firestore"],
                cwd=compose_file.parent,
                check=True
            )
            
            # Wait for emulator to be ready
            time.sleep(3)
            
            # Set environment variable
            os.environ["FIRESTORE_EMULATOR_HOST"] = "localhost:8080"
            
            yield
            
        finally:
            # Stop emulator
            subprocess.run(
                ["docker-compose", "down"],
                cwd=compose_file.parent,
                check=False
            )
    
    def test_firestore_emulator_connection(self, docker_firestore):
        """Test that we can connect to Firestore emulator."""
        store = FirestoreMemoryStore()
        
        # Should be able to write and read
        memory_id = store.write(
            content="Test emulator connection",
            memory_type=MemoryType.CONTEXT
        )
        
        assert memory_id is not None
        
        # Should be able to query
        results = store.query()
        assert len(results) > 0
