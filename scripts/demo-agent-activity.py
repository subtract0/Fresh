#!/usr/bin/env python3
"""
Agent Activity Simulation Demo

Simulates realistic agent interactions to validate the adaptive monitoring system.
This works without requiring OPENAI_API_KEY by simulating agent behaviors.
"""
from __future__ import annotations
import time
import random
from typing import List

from ai.monitor.activity import (
    get_activity_detector, 
    record_memory_operation, 
    record_agent_activity, 
    record_flow_activity
)
from ai.tools.memory_tools import WriteMemory, ReadMemoryContext


class AgentActivitySimulator:
    """Simulates realistic agent activity patterns for monitoring validation."""
    
    def __init__(self):
        self.agents = ["Father", "Architect", "Developer", "QA", "Reviewer"]
        self.detector = get_activity_detector()
        self.running = True
        
    def simulate_agent_thinking(self, agent_name: str, duration: float = 1.0):
        """Simulate an agent thinking/processing."""
        print(f"🤖 {agent_name}: Starting analysis...")
        record_agent_activity("start", agent_name)
        
        # Simulate reading context
        time.sleep(duration * 0.3)
        record_memory_operation("read", agent_name)
        
        # Simulate more thinking
        time.sleep(duration * 0.7)
        record_agent_activity("complete", agent_name)
        print(f"✅ {agent_name}: Analysis complete")
        
    def simulate_memory_operations(self, agent_name: str, operations: List[str]):
        """Simulate memory read/write operations."""
        for op in operations:
            if op == "write":
                print(f"💾 {agent_name}: Writing to memory...")
                # Simulate WriteMemory tool usage
                try:
                    tool = WriteMemory(
                        content=f"Task progress from {agent_name} at {time.time():.1f}",
                        tags=[agent_name.lower(), "demo"]
                    )
                    memory_id = tool.run()
                    print(f"📝 {agent_name}: Saved memory {memory_id}")
                except Exception as e:
                    print(f"⚠️  Memory write simulation: {e}")
                    record_memory_operation("write", agent_name)
                    
            elif op == "read":
                print(f"📖 {agent_name}: Reading context...")
                # Simulate ReadMemoryContext tool usage
                try:
                    tool = ReadMemoryContext(limit=3)
                    context = tool.run()
                    print(f"📚 {agent_name}: Read {len(context)} chars of context")
                except Exception as e:
                    print(f"⚠️  Memory read simulation: {e}")
                    record_memory_operation("read", agent_name)
                    
            time.sleep(random.uniform(0.5, 1.5))
            
    def simulate_agent_flow(self, from_agent: str, to_agent: str, task: str):
        """Simulate work flowing from one agent to another."""
        print(f"🔄 Flow: {from_agent} → {to_agent} ({task})")
        record_flow_activity("start", from_agent, to_agent)
        
        # From agent prepares work
        self.simulate_agent_thinking(from_agent, 1.5)
        self.simulate_memory_operations(from_agent, ["read", "write"])
        
        # Handoff simulation
        time.sleep(0.5)
        print(f"📤 {from_agent}: Delegating '{task}' to {to_agent}")
        
        # To agent receives and works
        self.simulate_agent_thinking(to_agent, 2.0)
        self.simulate_memory_operations(to_agent, ["read", "read", "write"])
        
        record_flow_activity("complete", from_agent, to_agent)
        print(f"✅ Flow complete: {task}")
        
    def run_development_cycle_demo(self):
        """Simulate a realistic development cycle through the agent chain."""
        print("🚀 Starting Development Cycle Demo")
        print("=" * 60)
        
        # Phase 1: Father initiates planning
        print("\\n📋 Phase 1: Strategic Planning")
        self.simulate_agent_thinking("Father", 2.0)
        self.simulate_memory_operations("Father", ["read", "write"])
        
        # Phase 2: Father → Architect (TDD Planning)
        print("\\n🏗️  Phase 2: Architecture & TDD Planning")
        self.simulate_agent_flow("Father", "Architect", "Design TDD approach for user authentication")
        
        # Phase 3: Architect → Developer (Implementation)  
        print("\\n💻 Phase 3: Implementation")
        self.simulate_agent_flow("Architect", "Developer", "Implement authentication tests and minimal code")
        
        # Phase 4: Developer → QA (Testing)
        print("\\n🔍 Phase 4: Quality Assurance")
        self.simulate_agent_flow("Developer", "QA", "Expand test coverage and edge cases")
        
        # Phase 5: QA → Reviewer (Final Review)
        print("\\n👥 Phase 5: Code Review")
        self.simulate_agent_flow("QA", "Reviewer", "Security review and simplicity check")
        
        # Phase 6: Reviewer → Father (Completion)
        print("\\n📊 Phase 6: Completion Report")
        self.simulate_agent_flow("Reviewer", "Father", "Development cycle complete - ready for deployment")
        
        print("\\n🎉 Development Cycle Demo Complete!")
        
    def show_activity_summary(self):
        """Display current activity levels and recent events."""
        print("\\n📊 Activity Summary")
        print("=" * 40)
        
        current_level = self.detector.compute_activity_level()
        refresh_interval = self.detector.get_refresh_interval()
        recent_events = self.detector.get_recent_events(10)
        
        print(f"🎯 Current Activity Level: {current_level.value.upper()}")
        print(f"⏱️  Recommended Refresh: {refresh_interval}s")
        print(f"📝 Recent Events: {len(recent_events)}")
        
        if recent_events:
            print("\\n🔍 Last 5 Events:")
            for i, event in enumerate(recent_events[-5:]):
                age = time.time() - event.timestamp
                print(f"  {i+1}. {event.event_type} ({event.agent_name}) - {age:.1f}s ago")


def main():
    """Run the agent activity simulation demo."""
    print("🎛️  Agent Activity Simulation Demo")
    print("Validating adaptive monitoring system...")
    print("=" * 60)
    
    simulator = AgentActivitySimulator()
    
    try:
        # Show initial state
        simulator.show_activity_summary()
        
        # Run the development cycle simulation
        simulator.run_development_cycle_demo()
        
        # Show final state
        simulator.show_activity_summary()
        
        print("\\n💡 Now run the adaptive monitoring to see the results:")
        print("   PYTHONPATH=/Users/am/Code/Fresh poetry run python scripts/watch-agents-adaptive.py")
        
    except KeyboardInterrupt:
        print("\\n🛑 Demo interrupted by user")
    except Exception as e:
        print(f"\\n❌ Demo error: {e}")
        raise


if __name__ == "__main__":
    main()
