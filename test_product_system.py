#!/usr/bin/env python3
"""
Simple test script for the Product-Driven Autonomous Development System
"""
import sys
import traceback
from pathlib import Path

def test_product_manager_import():
    """Test that ProductManager can be imported and initialized."""
    print("🧪 Testing ProductManager import...")
    try:
        from ai.agents.product_manager import ProductManagerAgent
        pm = ProductManagerAgent()
        print(f"✅ ProductManager initialized: {pm.name} v{pm.version}")
        return True
    except Exception as e:
        print(f"❌ Failed to import ProductManager: {e}")
        traceback.print_exc()
        return False

def test_product_analysis():
    """Test basic product analysis functionality."""
    print("🧪 Testing product analysis...")
    try:
        from ai.agents.product_manager import ProductManagerAgent
        
        pm = ProductManagerAgent()
        
        # Test feature data
        feature_data = {
            'name': 'TestFeature',
            'description': 'A test feature for validation',
            'issues': ['not accessible via CLI'],
            'status': 'implemented'
        }
        
        # Run analysis
        spec = pm.analyze_feature_request(feature_data)
        
        print(f"✅ Feature analyzed: {spec.feature_name}")
        print(f"   RICE Score: {spec.rice_score.score:.1f}")
        print(f"   Problem Severity: {spec.problem_analysis.severity_score}/10")
        print(f"   Requirements: {len(spec.requirements)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Product analysis failed: {e}")
        traceback.print_exc()
        return False

def test_orchestrator_import():
    """Test that ProductAutonomousOrchestrator can be imported."""
    print("🧪 Testing ProductAutonomousOrchestrator import...")
    try:
        from ai.orchestration.product_autonomous_orchestrator import ProductAutonomousOrchestrator
        from ai.memory.intelligent_store import IntelligentMemoryStore
        
        memory_store = IntelligentMemoryStore()
        orchestrator = ProductAutonomousOrchestrator(memory_store)
        
        print(f"✅ ProductAutonomousOrchestrator initialized")
        print(f"   Min RICE Score: {orchestrator.min_rice_score}")
        print(f"   Auto-approve quick wins: {orchestrator.auto_approve_quick_wins}")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to import ProductAutonomousOrchestrator: {e}")
        traceback.print_exc()
        return False

def test_cli_integration():
    """Test that CLI integration works."""
    print("🧪 Testing CLI integration...")
    try:
        from ai.cli.product_commands import scan_repository_for_features
        
        # Test scanning
        result = scan_repository_for_features(".")
        
        print(f"✅ CLI integration working")
        print(f"   Features found: {result.get('total_count', 0)}")
        
        return True
        
    except Exception as e:
        print(f"❌ CLI integration failed: {e}")
        traceback.print_exc()
        return False

def test_rice_score_calculation():
    """Test RICE score calculation."""
    print("🧪 Testing RICE score calculation...")
    try:
        from ai.agents.product_manager import RICEScore
        
        # Test known calculation
        rice = RICEScore(reach=100, impact=2.0, confidence=0.8, effort=0.5)
        expected = (100 * 2.0 * 0.8) / 0.5  # = 320
        
        if rice.score == expected:
            print(f"✅ RICE calculation correct: {rice.score}")
            return True
        else:
            print(f"❌ RICE calculation wrong: {rice.score} != {expected}")
            return False
            
    except Exception as e:
        print(f"❌ RICE calculation failed: {e}")
        traceback.print_exc()
        return False

def test_prd_generation():
    """Test PRD generation."""
    print("🧪 Testing PRD generation...")
    try:
        from ai.agents.product_manager import ProductManagerAgent
        
        pm = ProductManagerAgent()
        
        feature_data = {
            'name': 'PRDTestFeature',
            'description': 'Feature for testing PRD generation',
            'issues': ['not accessible via CLI'],
            'status': 'implemented'
        }
        
        spec = pm.analyze_feature_request(feature_data)
        prd = pm.create_prd_document(spec)
        
        # Check PRD contains expected sections
        required_sections = [
            "Product Requirements Document",
            "Problem Analysis", 
            "RICE Score",
            "User Story",
            "Requirements"
        ]
        
        for section in required_sections:
            if section not in prd:
                print(f"❌ PRD missing section: {section}")
                return False
        
        print(f"✅ PRD generated successfully ({len(prd)} characters)")
        return True
        
    except Exception as e:
        print(f"❌ PRD generation failed: {e}")
        traceback.print_exc()
        return False

def main():
    """Run all tests."""
    print("🚀 Starting Product-Driven Autonomous Development System Tests\n")
    
    tests = [
        test_product_manager_import,
        test_rice_score_calculation,
        test_product_analysis,
        test_prd_generation,
        test_orchestrator_import,
        test_cli_integration,
    ]
    
    results = []
    
    for test in tests:
        try:
            result = test()
            results.append(result)
            print()
        except Exception as e:
            print(f"❌ Test {test.__name__} crashed: {e}")
            results.append(False)
            print()
    
    # Summary
    passed = sum(results)
    total = len(results)
    
    print("=" * 60)
    print(f"📊 Test Results: {passed}/{total} passed")
    
    if passed == total:
        print("🎉 All tests passed! Product system is ready.")
        return 0
    else:
        print("⚠️  Some tests failed. Check implementation.")
        return 1

if __name__ == '__main__':
    sys.exit(main())
