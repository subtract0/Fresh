from __future__ import annotations
import pytest

# Test that will drive MCP client tool implementation
def test_mcp_client_tool_discovery():
    """Test that agents can discover available MCP servers."""
    from ai.tools.mcp_client import DiscoverMCPServers
    
    tool = DiscoverMCPServers()  # type: ignore
    servers = tool.run()
    
    assert isinstance(servers, list)
    # Should find at least the browser and research servers mentioned in rules
    assert any("browser" in str(s).lower() for s in servers)


def test_mcp_client_tool_call():
    """Test that agents can call MCP tools safely."""
    from ai.tools.mcp_client import CallMCPTool
    
    # Safe test: call a read-only tool
    tool = CallMCPTool(server="browser", tool="browser_snapshot", args={})  # type: ignore
    result = tool.run()
    
    assert isinstance(result, dict)
    assert "success" in result or "error" in result
