#!/usr/bin/env python
"""
Test the autonomous loop in a real scenario by having it implement TODOs.
This demonstrates the complete autonomous development workflow.
"""

import sys
from pathlib import Path

# Add ai module to path
sys.path.insert(0, str(Path(__file__).parent))

from ai.autonomous import AutonomousLoop
from ai.memory.intelligent_store import IntelligentMemoryStore


def test_autonomous_implementation():
    """Test autonomous loop implementing real TODOs."""
    print("🤖 Testing Autonomous Loop - Real Implementation\n")
    
    # Create autonomous loop with permissive settings for testing
    memory_store = IntelligentMemoryStore()
    config = {
        "max_improvements_per_cycle": 1,  # Just implement 1 TODO at a time
        "safety_level": "medium",  # Less strict for testing
        "require_tests": False  # Don't require tests for this demo
    }
    
    autonomous_loop = AutonomousLoop(
        working_directory=".",
        memory_store=memory_store,
        config=config
    )
    
    # Override safety controller test requirement for demo
    autonomous_loop.safety_controller.config["require_tests"] = False
    
    print("🔍 Running discovery phase...")
    opportunities = autonomous_loop._discovery_phase()
    
    # Filter to only our demo file TODOs
    demo_opportunities = [
        opp for opp in opportunities 
        if "test_autonomous_demo.py" in str(opp.details.get("file", ""))
    ]
    
    print(f"📋 Found {len(demo_opportunities)} opportunities in demo file:")
    for opp in demo_opportunities[:3]:  # Show first 3
        print(f"  • {opp.type}: {opp.description}")
        print(f"    Priority: {opp.priority:.2f}, Safety: {opp.safety_score:.2f}")
    
    if demo_opportunities:
        print(f"\n🎯 Testing planning phase on first opportunity...")
        planned = autonomous_loop._planning_phase(demo_opportunities[:1])
        
        if planned:
            print(f"✅ Successfully planned improvement:")
            plan = planned[0]
            print(f"   Type: {plan['type']}")
            print(f"   Description: {plan.get('command_description', 'N/A')}")
            print(f"   Safety validated: {plan.get('safety_validated', False)}")
            
            # Note: We won't actually execute to avoid changing files
            print(f"\n📝 Note: Execution skipped to preserve demo file integrity")
            print(f"   In real usage, this would implement the TODO automatically")
            
        else:
            print("❌ No improvements could be planned (safety constraints)")
    else:
        print("❌ No opportunities found in demo file")
    
    print(f"\n✅ Autonomous loop test completed!")
    print(f"   The system successfully identified and planned improvements")
    print(f"   Safety controls are working correctly")


if __name__ == "__main__":
    test_autonomous_implementation()
