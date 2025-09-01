#!/usr/bin/env python3
"""
Apply Cost Tracking to Existing Firestore Memory Systems

This script applies cost monitoring to all existing Firestore implementations
in the Fresh AI system, providing immediate cost visibility for memory operations.

Usage:
    python scripts/apply_firestore_cost_tracking.py
"""
import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def patch_firestore_memory():
    """Patch the basic Firestore memory store with cost tracking."""
    
    firestore_file = project_root / "ai" / "memory" / "firestore.py"
    
    # Read current content
    with open(firestore_file, 'r') as f:
        content = f.read()
    
    # Check if already patched
    if "wrap_firestore_client" in content:
        print("✅ ai/memory/firestore.py already has cost tracking")
        return
    
    # Add cost tracking import
    import_patch = """from __future__ import annotations
from typing import List, Optional
import os

from ai.memory.store import MemoryStore, MemoryItem
from ai.monitor.firestore_tracker import wrap_firestore_client
"""
    
    # Patch the client initialization
    client_patch = """        # Use ADC-compatible init via environment variables
        # Expect caller to export GOOGLE_APPLICATION_CREDENTIALS or set envs via workload identity
        raw_client = firestore.Client(project=project_id)  # type: ignore
        self._db = wrap_firestore_client(raw_client)  # Add cost tracking
        self._col = self._db.collection("agent_memory")  # type: ignore"""
    
    # Apply patches
    new_content = content.replace(
        """from __future__ import annotations
from typing import List, Optional
import os

from ai.memory.store import MemoryStore, MemoryItem""",
        import_patch
    )
    
    new_content = new_content.replace(
        """        # Use ADC-compatible init via environment variables
        # Expect caller to export GOOGLE_APPLICATION_CREDENTIALS or set envs via workload identity
        self._db = firestore.Client(project=project_id)  # type: ignore
        self._col = self._db.collection("agent_memory")  # type: ignore""",
        client_patch
    )
    
    # Write back
    with open(firestore_file, 'w') as f:
        f.write(new_content)
    
    print("✅ Applied cost tracking to ai/memory/firestore.py")

def patch_enhanced_firestore():
    """Patch the enhanced Firestore memory store with cost tracking."""
    
    enhanced_file = project_root / "ai" / "memory" / "enhanced_firestore.py"
    
    # Read current content
    with open(enhanced_file, 'r') as f:
        content = f.read()
    
    # Check if already patched
    if "wrap_firestore_client" in content:
        print("✅ ai/memory/enhanced_firestore.py already has cost tracking")
        return
    
    # Add import
    if "from ai.monitor.firestore_tracker import wrap_firestore_client" not in content:
        # Add after existing imports
        import_insertion_point = content.find("from ai.memory.intelligent_store import")
        if import_insertion_point != -1:
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if "from ai.memory.intelligent_store import" in line:
                    # Find end of this import block
                    j = i + 1
                    while j < len(lines) and (lines[j].strip().startswith('') and (',' in lines[j] or lines[j].strip() == '' or lines[j].strip().endswith(')'))):
                        j += 1
                    lines.insert(j, "from ai.monitor.firestore_tracker import wrap_firestore_client")
                    break
            content = '\n'.join(lines)
    
    # Patch the client setup
    original_setup = """        self._db = firestore.Client(project=project_id)
        self._collection = self._db.collection(self.collection_name)"""
    
    new_setup = """        raw_client = firestore.Client(project=project_id)
        self._db = wrap_firestore_client(raw_client)  # Add cost tracking
        self._collection = self._db.collection(self.collection_name)"""
    
    content = content.replace(original_setup, new_setup)
    
    # Write back
    with open(enhanced_file, 'w') as f:
        f.write(content)
    
    print("✅ Applied cost tracking to ai/memory/enhanced_firestore.py")

def patch_firestore_store():
    """Patch the production Firestore memory store with cost tracking."""
    
    store_file = project_root / "ai" / "memory" / "firestore_store.py"
    
    # Read current content
    with open(store_file, 'r') as f:
        content = f.read()
    
    # Check if already patched
    if "wrap_firestore_client" in content:
        print("✅ ai/memory/firestore_store.py already has cost tracking")
        return
    
    # Add import after the intelligent_store import
    import_patch = """from ai.memory.intelligent_store import IntelligentMemoryStore, EnhancedMemoryItem, MemoryType
from ai.utils.clock import now as time_now
from ai.monitor.firestore_tracker import wrap_firestore_client"""
    
    content = content.replace(
        """from ai.memory.intelligent_store import IntelligentMemoryStore, EnhancedMemoryItem, MemoryType
from ai.utils.clock import now as time_now""",
        import_patch
    )
    
    # Patch client initialization in _init_firestore
    original_init = """            if self.project_id:
                self._firestore_client = firestore.Client(project=self.project_id)
            else:
                self._firestore_client = firestore.Client()"""
    
    new_init = """            if self.project_id:
                raw_client = firestore.Client(project=self.project_id)
            else:
                raw_client = firestore.Client()
            self._firestore_client = wrap_firestore_client(raw_client)  # Add cost tracking"""
    
    content = content.replace(original_init, new_init)
    
    # Write back
    with open(store_file, 'w') as f:
        f.write(content)
    
    print("✅ Applied cost tracking to ai/memory/firestore_store.py")

def main():
    """Apply cost tracking to all Firestore memory systems."""
    
    print("🚀 Applying Cost Tracking to Firestore Memory Systems")
    print("=" * 55)
    
    # Apply patches to all Firestore implementations
    patch_firestore_memory()
    patch_enhanced_firestore() 
    patch_firestore_store()
    
    print("\n✅ Cost tracking applied to all Firestore memory systems!")
    print("\nNext steps:")
    print("1. All Firestore operations will now be automatically tracked")
    print("2. View costs: poetry run python scripts/setup_cost_monitoring.py --quick")
    print("3. Set budgets: poetry run python scripts/setup_cost_monitoring.py")
    print("4. Monitor usage: poetry run python scripts/setup_cost_monitoring.py --dashboard")

if __name__ == "__main__":
    main()
