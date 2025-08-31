#!/usr/bin/env python3
"""
Monitoring Validation Test

Validates the adaptive monitoring system by running agent simulations
and monitoring simultaneously to demonstrate all activity levels.
"""
from __future__ import annotations
import sys
import time
import threading
from typing import Optional

from ai.monitor.activity import (
    get_activity_detector, 
    record_memory_operation, 
    record_agent_activity, 
    record_flow_activity,
    ActivityLevel
)
from ai.monitor.adaptive_ui import AdaptiveMonitorUI, RefreshController
from ai.monitor.status import get_status


class MonitoringValidator:
    """Validates the adaptive monitoring system through controlled testing."""
    
    def __init__(self):
        self.detector = get_activity_detector()
        self.controller = RefreshController()
        self.ui = AdaptiveMonitorUI()
        self.test_results = {}
        
    def clear_activity(self):
        """Clear existing activity to start fresh."""
        self.detector.events.clear()
        print("🧹 Activity cleared - starting fresh")
        
    def test_idle_level(self) -> bool:
        """Test IDLE activity level (no events)."""
        print("\\n🔵 Testing IDLE Level")
        self.clear_activity()
        
        level = self.detector.compute_activity_level()
        interval = self.controller.get_current_interval()
        
        success = level == ActivityLevel.IDLE and interval == 10.0
        print(f"  Result: {level.value} -> {interval}s ({'✅' if success else '❌'})")
        return success
        
    def test_low_level(self) -> bool:
        """Test LOW activity level (single agent, few operations)."""
        print("\\n🟡 Testing LOW Level")
        self.clear_activity()
        
        # Generate minimal activity
        record_memory_operation("read", "Father")
        record_agent_activity("start", "Father")
        
        level = self.detector.compute_activity_level()
        interval = self.controller.get_current_interval()
        
        success = level == ActivityLevel.LOW and interval == 5.0
        print(f"  Result: {level.value} -> {interval}s ({'✅' if success else '❌'})")
        return success
        
    def test_medium_level(self) -> bool:
        """Test MEDIUM activity level (multiple agents)."""
        print("\\n🔵 Testing MEDIUM Level") 
        self.clear_activity()
        
        # Generate medium activity - multiple agents
        for agent in ["Father", "Architect", "Developer"]:
            record_memory_operation("read", agent)
            record_agent_activity("start", agent)
            
        level = self.detector.compute_activity_level()
        interval = self.controller.get_current_interval()
        
        success = level == ActivityLevel.MEDIUM and interval == 2.0
        print(f"  Result: {level.value} -> {interval}s ({'✅' if success else '❌'})")
        return success
        
    def test_high_level(self) -> bool:
        """Test HIGH activity level (active flows)."""
        print("\\n🔴 Testing HIGH Level")
        self.clear_activity()
        
        # Generate high activity - flows
        record_flow_activity("start", "Father", "Architect")
        record_memory_operation("write", "Father")
        record_memory_operation("write", "Architect")
        
        level = self.detector.compute_activity_level()
        interval = self.controller.get_current_interval()
        
        success = level == ActivityLevel.HIGH and interval == 1.0
        print(f"  Result: {level.value} -> {interval}s ({'✅' if success else '❌'})")
        return success
        
    def test_ui_rendering(self) -> bool:
        """Test UI components render without errors."""
        print("\\n🎨 Testing UI Rendering")
        
        try:
            # Test with mock status
            mock_status = {
                "agents": ["Father", "Architect", "Developer"],
                "flows": [["Father", "Architect"]],
                "memory_context": "Test context",
                "next_steps": ["Step 1", "Step 2"],
                "release_notes": "# Test Release\\nDemo notes"
            }
            
            # Test table generation
            table = self.ui._generate_agent_table(mock_status)
            panel = self.ui._generate_info_panel(mock_status)
            
            # Test display update (should not crash)
            self.ui.update_display(mock_status)
            
            print("  ✅ All UI components render successfully")
            return True
            
        except Exception as e:
            print(f"  ❌ UI rendering failed: {e}")
            return False
            
    def test_monitoring_integration(self) -> bool:
        """Test full monitoring integration."""
        print("\\n🔄 Testing Monitoring Integration")
        
        try:
            # Generate activity
            record_flow_activity("start", "Father", "Architect")
            record_memory_operation("write", "Father")
            
            # Get status (should include recent activity)
            status = get_status(limit=5)
            
            # Verify structure
            required_keys = ["agents", "flows", "memory_context", "next_steps", "release_notes"]
            has_all_keys = all(key in status for key in required_keys)
            has_agents = len(status["agents"]) == 5
            
            success = has_all_keys and has_agents
            print(f"  Status structure: {'✅' if has_all_keys else '❌'}")
            print(f"  Agent count: {len(status['agents'])} ({'✅' if has_agents else '❌'})")
            
            return success
            
        except Exception as e:
            print(f"  ❌ Integration test failed: {e}")
            return False
            
    def run_stress_test(self, duration: float = 10.0) -> bool:
        """Run a stress test with continuous activity."""
        print(f"\\n⚡ Running Stress Test ({duration}s)")
        
        start_time = time.time()
        operations = 0
        
        try:
            agents = ["Father", "Architect", "Developer", "QA", "Reviewer"]
            
            while time.time() - start_time < duration:
                # Simulate random agent activity
                import random
                agent = random.choice(agents)
                
                if operations % 3 == 0:
                    record_flow_activity("start", agent, random.choice(agents))
                elif operations % 3 == 1:
                    record_memory_operation("write", agent)
                else:
                    record_agent_activity("start", agent)
                    
                operations += 1
                time.sleep(0.1)  # 10 operations per second
                
            level = self.detector.compute_activity_level()
            interval = self.controller.get_current_interval()
            events_count = len(self.detector.events)
            
            print(f"  Operations: {operations}")
            print(f"  Final level: {level.value} -> {interval}s")
            print(f"  Events tracked: {events_count}")
            
            # Should be HIGH activity after stress test
            success = level == ActivityLevel.HIGH and events_count > 0
            print(f"  Result: {'✅' if success else '❌'}")
            
            return success
            
        except Exception as e:
            print(f"  ❌ Stress test failed: {e}")
            return False
            
    def run_all_tests(self) -> dict:
        """Run complete validation suite."""
        print("🧪 Starting Adaptive Monitoring Validation Suite")
        print("=" * 60)
        
        tests = [
            ("Idle Level", self.test_idle_level),
            ("Low Level", self.test_low_level), 
            ("Medium Level", self.test_medium_level),
            ("High Level", self.test_high_level),
            ("UI Rendering", self.test_ui_rendering),
            ("Integration", self.test_monitoring_integration),
            ("Stress Test", self.run_stress_test),
        ]
        
        results = {}
        passed = 0
        
        for test_name, test_func in tests:
            try:
                results[test_name] = test_func()
                if results[test_name]:
                    passed += 1
            except Exception as e:
                print(f"\\n❌ {test_name} failed with exception: {e}")
                results[test_name] = False
                
        # Summary
        total = len(tests)
        print(f"\\n📊 Validation Results: {passed}/{total} tests passed")
        print("=" * 60)
        
        for test_name, result in results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"  {test_name:<20} {status}")
            
        overall_success = passed == total
        print(f"\\n🎯 Overall Result: {'✅ ALL TESTS PASSED' if overall_success else f'❌ {total-passed} TESTS FAILED'}")
        
        return results


def main():
    """Run the monitoring validation suite."""
    validator = MonitoringValidator()
    
    try:
        results = validator.run_all_tests()
        
        # Exit with appropriate code
        all_passed = all(results.values())
        sys.exit(0 if all_passed else 1)
        
    except KeyboardInterrupt:
        print("\\n🛑 Validation interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\\n❌ Validation suite failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
