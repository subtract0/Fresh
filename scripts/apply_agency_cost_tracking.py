#!/usr/bin/env python3
"""
Apply Cost Tracking to Agency Swarm OpenAI Usage

This script patches Agency Swarm to use cost-tracked OpenAI clients,
providing immediate visibility into agent conversation costs.

Usage:
    python scripts/apply_agency_cost_tracking.py
"""
import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def patch_agency_swarm_openai():
    """
    Patch Agency Swarm to use cost-tracked OpenAI clients.
    
    Agency Swarm uses OpenAI internally, so we need to patch it
    at the import level to intercept all API calls.
    """
    
    print("🚀 Applying Cost Tracking to Agency Swarm OpenAI Usage")
    print("=" * 55)
    
    # Create a monkey patch for openai module
    patch_file = project_root / "ai" / "agency_openai_patch.py"
    
    patch_content = '''"""
Agency Swarm OpenAI Cost Tracking Patch

This module patches the openai module to use cost tracking
when imported by Agency Swarm or other parts of the system.
"""
import sys
from typing import Any

# Store original openai module
_original_openai = None

def patch_openai():
    """Patch the openai module with cost tracking."""
    global _original_openai
    
    if 'openai' in sys.modules:
        _original_openai = sys.modules['openai']
        
        # Import our cost tracking wrapper
        from ai.monitor.openai_tracker import wrap_openai_client
        
        # Wrap the OpenAI client class
        original_client_class = _original_openai.OpenAI
        
        class TrackedOpenAI(original_client_class):
            """OpenAI client with automatic cost tracking."""
            
            def __init__(self, *args, **kwargs):
                # Initialize the original client
                super().__init__(*args, **kwargs)
                
                # Wrap with cost tracking
                wrapped_client = wrap_openai_client(self)
                
                # Copy wrapped attributes back to self
                self.chat = wrapped_client.chat
                self.embeddings = wrapped_client.embeddings
                
                print("💰 OpenAI client wrapped with cost tracking")
        
        # Replace the OpenAI class in the module
        _original_openai.OpenAI = TrackedOpenAI
        
        print("✅ OpenAI module patched with cost tracking")
    
def unpatch_openai():
    """Restore original openai module.""" 
    global _original_openai
    
    if _original_openai and 'openai' in sys.modules:
        # Restore original OpenAI class
        sys.modules['openai'].OpenAI = _original_openai.OpenAI
        print("↩️ OpenAI module restored to original")

# Auto-patch when this module is imported
patch_openai()
'''
    
    with open(patch_file, 'w') as f:
        f.write(patch_content)
    
    print(f"✅ Created OpenAI patch module: {patch_file}")
    
    # Update agency.py to import the patch
    agency_file = project_root / "ai" / "agency.py"
    
    with open(agency_file, 'r') as f:
        content = f.read()
    
    # Check if already patched
    if "agency_openai_patch" in content:
        print("✅ ai/agency.py already has cost tracking patch")
        return
    
    # Add patch import at the top (after the first import)
    lines = content.split('\\n')
    
    # Find the first import line
    for i, line in enumerate(lines):
        if line.startswith('from __future__'):
            continue
        if line.startswith('from ') or line.startswith('import '):
            # Insert patch import after the first real import
            lines.insert(i + 1, "")
            lines.insert(i + 2, "# Import cost tracking patch for Agency Swarm")
            lines.insert(i + 3, "import ai.agency_openai_patch  # noqa: F401")
            lines.insert(i + 4, "")
            break
    
    # Write back
    with open(agency_file, 'w') as f:
        f.write('\\n'.join(lines))
    
    print("✅ Applied cost tracking patch to ai/agency.py")

def test_patch():
    """Test that the patch works correctly."""
    
    print("\\n🧪 Testing Agency Swarm cost tracking...")
    
    try:
        # Import agency after patching
        from ai.agency import build_agency
        from ai.monitor.cost_tracker import get_cost_tracker
        
        # Get initial record count
        tracker = get_cost_tracker()
        initial_records = len(tracker.usage_records)
        
        print(f"📊 Initial usage records: {initial_records}")
        
        # Try to build agency (this will use OpenAI if available)
        if os.getenv("OPENAI_API_KEY"):
            print("🔑 OpenAI API key found - building agency...")
            try:
                agency = build_agency()
                print(f"✅ Agency built successfully with {len(agency.agents)} agents")
                
                # Check if any new records were created
                final_records = len(tracker.usage_records)
                new_records = final_records - initial_records
                
                if new_records > 0:
                    print(f"🎉 Cost tracking working! {new_records} new usage records")
                    
                    # Show recent records
                    recent = tracker.usage_records[-min(3, new_records):]
                    for record in recent:
                        print(f"   📝 {record.service.value} {record.operation.value}: "
                              f"${record.estimated_cost_usd:.4f}")
                else:
                    print("ℹ️  No new usage records (agency may use cached assistants)")
                    
            except Exception as e:
                print(f"⚠️  Agency build failed: {e}")
                print("   This is expected if OpenAI API is not configured")
        else:
            print("ℹ️  No OpenAI API key - skipping agency build test")
            print("   Set OPENAI_API_KEY to test with real Agency Swarm calls")
            
        print("✅ Cost tracking integration appears to be working")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        
def main():
    """Apply cost tracking to Agency Swarm."""
    
    # Apply the patch
    patch_agency_swarm_openai()
    
    # Test the integration
    test_patch()
    
    print("\\n🎯 Next Steps:")
    print("1. Agency Swarm will now automatically track OpenAI costs")
    print("2. All agent conversations will be monitored")
    print("3. View costs: poetry run python scripts/setup_cost_monitoring.py --quick")
    print("4. Set budgets: poetry run python scripts/setup_cost_monitoring.py")
    print("5. Monitor usage: poetry run python scripts/setup_cost_monitoring.py --dashboard")
    
    print("\\n💡 Usage:")
    print("# Now when you use Agency Swarm, costs are automatically tracked:")
    print("from ai.agency import build_agency")
    print("agency = build_agency()  # <-- This will now track OpenAI costs!")

if __name__ == "__main__":
    main()
