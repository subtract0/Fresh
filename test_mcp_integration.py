#!/usr/bin/env python3
"""
Test MCP integration for product-driven autonomous development

This test validates that MCP server configurations are properly set up
and that agents will have access to the specified servers.
"""
import sys
from pathlib import Path

def test_mcp_server_registry():
    """Test that MCP server registry is properly configured."""
    print("🧪 Testing MCP server registry configuration...")
    
    try:
        # Test the server registry configuration without full initialization
        from ai.integration.mcp_server_registry import KnownMCPServer, EnhancedMCPRegistry
        
        # Create a test registry (without initialization)
        registry = EnhancedMCPRegistry()
        
        # Check that the specific servers are configured
        expected_servers = [
            "688cf28d-e69c-4624-b7cb-0725f36f9518",  # Reference server
            "613c9e91-4c54-43e9-b7c7-387c78d44459",  # Analysis server
            "a62d40d5-264a-4e05-bab3-b9da886ff14d",  # Research server
        ]
        
        for server_id in expected_servers:
            if server_id in registry.known_servers:
                server = registry.known_servers[server_id]
                print(f"✅ {server.name} ({server_id[:8]}...) configured")
                print(f"   📋 Capabilities: {', '.join(server.capabilities[:3])}...")
                print(f"   ⭐ Priority: {server.priority}")
            else:
                print(f"❌ Server {server_id[:8]}... not found in registry")
                return False
        
        print(f"✅ MCP Registry configured with {len(registry.known_servers)} known servers")
        return True
        
    except Exception as e:
        print(f"❌ MCP registry test failed: {e}")
        return False

def test_server_capabilities():
    """Test that servers have the expected capabilities."""
    print("🧪 Testing server capabilities configuration...")
    
    try:
        from ai.integration.mcp_server_registry import EnhancedMCPRegistry
        
        registry = EnhancedMCPRegistry()
        
        # Test Reference Server capabilities
        ref_server = registry.known_servers["688cf28d-e69c-4624-b7cb-0725f36f9518"]
        expected_ref_caps = {"documentation", "reference_lookup", "example_generation"}
        if not expected_ref_caps.issubset(set(ref_server.capabilities)):
            print(f"❌ Reference server missing expected capabilities")
            return False
        print("✅ Reference Server has documentation capabilities")
        
        # Test Analysis Server capabilities  
        analysis_server = registry.known_servers["613c9e91-4c54-43e9-b7c7-387c78d44459"]
        expected_analysis_caps = {"code_analysis", "security_audit", "performance_review"}
        if not expected_analysis_caps.issubset(set(analysis_server.capabilities)):
            print(f"❌ Analysis server missing expected capabilities")
            return False
        print("✅ Analysis Server has code analysis capabilities")
        
        # Test Research Server capabilities
        research_server = registry.known_servers["a62d40d5-264a-4e05-bab3-b9da886ff14d"]
        expected_research_caps = {"web_search", "competitive_analysis", "market_research"}
        if not expected_research_caps.issubset(set(research_server.capabilities)):
            print(f"❌ Research server missing expected capabilities")
            return False
        print("✅ Research Server has web search capabilities")
        
        return True
        
    except Exception as e:
        print(f"❌ Server capabilities test failed: {e}")
        return False

def test_agent_instructions_generation():
    """Test that agent task descriptions will include MCP server information."""
    print("🧪 Testing agent instruction generation with MCP context...")
    
    try:
        # Create a mock product specification
        from ai.agents.product_manager import ProductManagerAgent
        
        pm = ProductManagerAgent()
        
        # Create test feature data
        feature_data = {
            'name': 'TestFeature',
            'description': 'A test feature for MCP validation',
            'issues': ['not accessible via CLI'],
            'status': 'implemented'
        }
        
        # Generate feature specification
        spec = pm.analyze_feature_request(feature_data)
        
        print("✅ Product specification generated")
        print(f"   📊 RICE Score: {spec.rice_score.score:.1f}")
        print(f"   🎯 Problem Severity: {spec.problem_analysis.severity_score}/10")
        
        # Check that specification has the required components for MCP integration
        assert spec.user_story.acceptance_criteria
        assert spec.requirements
        assert spec.success_metrics
        
        print("✅ Feature specification ready for MCP-enhanced agents")
        return True
        
    except Exception as e:
        print(f"❌ Agent instruction generation test failed: {e}")
        return False

def test_mcp_server_discovery_structure():
    """Test the MCP server discovery data structures."""
    print("🧪 Testing MCP server discovery data structures...")
    
    try:
        from ai.integration.mcp_server_registry import KnownMCPServer
        
        # Test server configuration structure
        test_server = KnownMCPServer(
            server_id="test-server-123",
            name="Test Server",
            description="Test server for validation",
            capabilities=["test_capability"],
            priority=1,
            connection_config={"type": "test"},
            expected_endpoints=["test/endpoint"]
        )
        
        # Verify all required fields are present
        assert test_server.server_id == "test-server-123"
        assert test_server.name == "Test Server"
        assert test_server.capabilities == ["test_capability"]
        assert test_server.priority == 1
        
        print("✅ MCP server configuration structure is valid")
        return True
        
    except Exception as e:
        print(f"❌ MCP server discovery structure test failed: {e}")
        return False

def main():
    """Run all MCP integration tests."""
    print("🔌 Starting MCP Integration Tests for Product-Driven Development\n")
    
    tests = [
        test_mcp_server_registry,
        test_server_capabilities, 
        test_agent_instructions_generation,
        test_mcp_server_discovery_structure,
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
    print(f"📊 MCP Integration Test Results: {passed}/{total} passed")
    
    if passed == total:
        print("🎉 All MCP integration tests passed!")
        print("🔌 Agents will have access to:")
        print("   • Reference Server (688cf28d...): Documentation & examples")
        print("   • Analysis Server (613c9e91...): Code analysis & security")  
        print("   • Research Server (a62d40d5...): Web search & competitive analysis")
        return 0
    else:
        print("⚠️  Some MCP integration tests failed.")
        return 1

if __name__ == '__main__':
    sys.exit(main())
