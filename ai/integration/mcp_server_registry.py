"""
Enhanced MCP Server Registry

Provides comprehensive management and access to MCP servers including specific
server instances and capabilities for autonomous development agents.

Includes support for:
- Server ID: 688cf28d-e69c-4624-b7cb-0725f36f9518 (Reference server)
- Server ID: 613c9e91-4c54-43e9-b7c7-387c78d44459 (Analysis server) 
- Server ID: a62d40d5-264a-4e05-bab3-b9da886ff14d (Research server)
"""
from __future__ import annotations
import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, field
from pathlib import Path

from ai.integration.mcp_discovery import MCPServerInfo, MCPServerCapability, MCPDiscoverySystem
from ai.tools.enhanced_mcp import EnhancedMCPTool, MCPResult
from ai.memory.intelligent_store import IntelligentMemoryStore

logger = logging.getLogger(__name__)


@dataclass
class KnownMCPServer:
    """Configuration for a known MCP server."""
    server_id: str
    name: str
    description: str
    capabilities: List[str]
    priority: int = 1  # 1=highest, 5=lowest
    connection_config: Dict[str, Any] = field(default_factory=dict)
    expected_endpoints: List[str] = field(default_factory=list)
    health_check_url: Optional[str] = None


class EnhancedMCPRegistry:
    """Enhanced registry for managing known and discovered MCP servers."""
    
    def __init__(self, memory_store: Optional[IntelligentMemoryStore] = None):
        self.memory_store = memory_store or IntelligentMemoryStore()
        self.known_servers: Dict[str, KnownMCPServer] = {}
        self.active_servers: Dict[str, MCPServerInfo] = {}
        self.server_tools: Dict[str, EnhancedMCPTool] = {}
        self.discovery_system: Optional[MCPDiscoverySystem] = None
        
        # Initialize known servers
        self._initialize_known_servers()
        
    def _initialize_known_servers(self):
        """Initialize the registry with known MCP servers."""
        
        # Server 1: Reference server (688cf28d-e69c-4624-b7cb-0725f36f9518)
        self.known_servers["688cf28d-e69c-4624-b7cb-0725f36f9518"] = KnownMCPServer(
            server_id="688cf28d-e69c-4624-b7cb-0725f36f9518",
            name="Reference MCP Server",
            description="Primary reference server for documentation, examples, and standard MCP operations",
            capabilities=[
                "documentation", "reference_lookup", "example_generation", 
                "code_templates", "best_practices", "standard_operations"
            ],
            priority=1,
            connection_config={
                "type": "reference",
                "supports_batch": True,
                "max_concurrent": 10
            },
            expected_endpoints=[
                "tools/list", "tools/call", "resources/list", 
                "resources/read", "prompts/list", "prompts/get"
            ]
        )
        
        # Server 2: Analysis server (613c9e91-4c54-43e9-b7c7-387c78d44459)
        self.known_servers["613c9e91-4c54-43e9-b7c7-387c78d44459"] = KnownMCPServer(
            server_id="613c9e91-4c54-43e9-b7c7-387c78d44459",
            name="Analysis MCP Server", 
            description="Advanced analysis server for code review, performance analysis, and system diagnostics",
            capabilities=[
                "code_analysis", "performance_review", "security_audit",
                "dependency_analysis", "architecture_review", "quality_metrics",
                "static_analysis", "complexity_analysis"
            ],
            priority=1,
            connection_config={
                "type": "analysis",
                "supports_streaming": True,
                "max_analysis_size": "100MB",
                "timeout": 300
            },
            expected_endpoints=[
                "analyze/code", "analyze/performance", "analyze/security",
                "analyze/dependencies", "analyze/architecture", "metrics/quality"
            ]
        )
        
        # Server 3: Research server (a62d40d5-264a-4e05-bab3-b9da886ff14d)
        self.known_servers["a62d40d5-264a-4e05-bab3-b9da886ff14d"] = KnownMCPServer(
            server_id="a62d40d5-264a-4e05-bab3-b9da886ff14d",
            name="Research MCP Server",
            description="Comprehensive research server for web search, data collection, and competitive analysis",
            capabilities=[
                "web_search", "data_extraction", "competitive_analysis",
                "market_research", "technology_trends", "documentation_search",
                "api_discovery", "library_research", "benchmarking"
            ],
            priority=1,
            connection_config={
                "type": "research", 
                "rate_limit": 100,  # requests per minute
                "supports_caching": True,
                "cache_ttl": 3600
            },
            expected_endpoints=[
                "search/web", "search/docs", "research/competitive",
                "research/market", "research/tech", "extract/data"
            ]
        )
        
        logger.info(f"🎯 Initialized registry with {len(self.known_servers)} known MCP servers")
    
    async def initialize_servers(self) -> Dict[str, bool]:
        """Initialize and connect to all known MCP servers."""
        results = {}
        
        logger.info("🔌 Initializing connection to known MCP servers...")
        
        # Initialize discovery system
        from ai.integration.mcp_discovery import get_mcp_discovery
        self.discovery_system = get_mcp_discovery()
        
        for server_id, known_server in self.known_servers.items():
            try:
                logger.info(f"🔄 Connecting to {known_server.name} ({server_id[:8]}...)")
                
                # Create enhanced MCP tool for this server
                server_tool = EnhancedMCPTool()
                await server_tool.initialize()
                
                # Test server capabilities
                server_info = await self._probe_server_capabilities(server_id, known_server, server_tool)
                
                if server_info:
                    self.active_servers[server_id] = server_info
                    self.server_tools[server_id] = server_tool
                    results[server_id] = True
                    logger.info(f"✅ {known_server.name} connected successfully")
                else:
                    results[server_id] = False
                    logger.warning(f"⚠️ {known_server.name} connection failed")
                    
            except Exception as e:
                results[server_id] = False
                logger.error(f"❌ Failed to connect to {known_server.name}: {e}")
        
        # Store server status in memory
        await self._store_server_status(results)
        
        active_count = sum(1 for success in results.values() if success)
        logger.info(f"🎉 MCP Server initialization complete: {active_count}/{len(self.known_servers)} servers active")
        
        return results
    
    async def _probe_server_capabilities(
        self, 
        server_id: str, 
        known_server: KnownMCPServer,
        server_tool: EnhancedMCPTool
    ) -> Optional[MCPServerInfo]:
        """Probe a server to verify its capabilities."""
        
        try:
            # Create server info object
            server_info = MCPServerInfo(
                server_id=server_id,
                name=known_server.name,
                status="probing",
                discovery_method="registry",
                metadata={
                    "description": known_server.description,
                    "priority": known_server.priority,
                    "expected_capabilities": known_server.capabilities
                }
            )
            
            # Test basic connectivity with a simple capability request
            test_result = await self._test_server_connectivity(server_tool, known_server)
            
            if test_result:
                # Add capabilities based on known configuration
                capabilities = []
                for cap_name in known_server.capabilities:
                    capability = MCPServerCapability(
                        name=cap_name,
                        description=f"{cap_name} capability on {known_server.name}",
                        parameters={},
                        category=self._categorize_capability(cap_name),
                        confidence_score=0.9  # High confidence for known servers
                    )
                    capabilities.append(capability)
                
                server_info.capabilities = capabilities
                server_info.status = "healthy"
                server_info.uptime_start = datetime.now()
                
                return server_info
            else:
                server_info.status = "failed"
                return None
                
        except Exception as e:
            logger.error(f"Error probing server {server_id}: {e}")
            return None
    
    async def _test_server_connectivity(self, server_tool: EnhancedMCPTool, known_server: KnownMCPServer) -> bool:
        """Test basic connectivity to a server."""
        try:
            # Try a simple operation based on server type
            if "research" in known_server.capabilities:
                result = await server_tool.research_query("test connectivity", max_results=1, timeout=10)
                return result.success
            elif "analysis" in known_server.capabilities:
                # Test with a simple analysis request
                result = await server_tool.analyze_document("/dev/null")  # Safe test
                return result.success or "not found" in str(result.error).lower()  # Expected for /dev/null
            elif "documentation" in known_server.capabilities:
                result = await server_tool.generate_documentation("test", include_examples=False)
                return result.success
            else:
                # Generic connectivity test
                return True  # Assume success if no specific test
                
        except asyncio.TimeoutError:
            logger.warning(f"Server connectivity test timed out for {known_server.name}")
            return False
        except Exception as e:
            logger.warning(f"Server connectivity test failed for {known_server.name}: {e}")
            return False
    
    def _categorize_capability(self, capability_name: str) -> str:
        """Categorize a capability into a standard category."""
        
        research_caps = {"web_search", "data_extraction", "competitive_analysis", "market_research", 
                        "technology_trends", "documentation_search", "api_discovery", "library_research", 
                        "benchmarking"}
        analysis_caps = {"code_analysis", "performance_review", "security_audit", "dependency_analysis",
                        "architecture_review", "quality_metrics", "static_analysis", "complexity_analysis"}
        documentation_caps = {"documentation", "reference_lookup", "example_generation", "code_templates", 
                             "best_practices", "standard_operations"}
        
        if capability_name in research_caps:
            return "research"
        elif capability_name in analysis_caps:
            return "analysis" 
        elif capability_name in documentation_caps:
            return "documentation"
        else:
            return "general"
    
    async def _store_server_status(self, results: Dict[str, bool]):
        """Store server status information in memory."""
        try:
            status_info = {
                "servers": [],
                "summary": {
                    "total_servers": len(results),
                    "active_servers": sum(1 for success in results.values() if success),
                    "failed_servers": sum(1 for success in results.values() if not success),
                    "last_check": datetime.now().isoformat()
                }
            }
            
            for server_id, success in results.items():
                known_server = self.known_servers[server_id]
                server_info = {
                    "server_id": server_id,
                    "name": known_server.name,
                    "status": "active" if success else "failed",
                    "capabilities": known_server.capabilities,
                    "priority": known_server.priority
                }
                status_info["servers"].append(server_info)
            
            await self.memory_store.store_memory(
                "mcp_server_status",
                "system",
                status_info,
                metadata={"type": "mcp_registry", "source": "enhanced_registry"}
            )
            
        except Exception as e:
            logger.warning(f"Failed to store server status in memory: {e}")
    
    async def get_server_for_capability(self, capability: str) -> Optional[EnhancedMCPTool]:
        """Get the best available server for a specific capability."""
        
        best_server = None
        best_priority = 10  # Lower is better
        
        for server_id, server_info in self.active_servers.items():
            # Check if server has the requested capability
            has_capability = any(
                cap.name == capability or cap.category == capability 
                for cap in server_info.capabilities
            )
            
            if has_capability:
                known_server = self.known_servers.get(server_id)
                if known_server and known_server.priority < best_priority:
                    best_priority = known_server.priority
                    best_server = self.server_tools.get(server_id)
        
        return best_server
    
    async def execute_research_query(self, query: str, **kwargs) -> MCPResult:
        """Execute a research query on the best available research server."""
        server_tool = await self.get_server_for_capability("research")
        
        if server_tool:
            logger.info(f"🔍 Executing research query via MCP server: {query[:100]}...")
            result = await server_tool.research_query(query, **kwargs)
            
            # Log usage for analytics
            await self._log_server_usage("research", query, result.success)
            return result
        else:
            logger.warning("⚠️ No research-capable MCP server available")
            return MCPResult(
                success=False, 
                error="No research server available",
                capability_used="research"
            )
    
    async def execute_code_analysis(self, code_path: str, **kwargs) -> MCPResult:
        """Execute code analysis on the best available analysis server."""
        server_tool = await self.get_server_for_capability("analysis")
        
        if server_tool:
            logger.info(f"🔍 Executing code analysis via MCP server: {code_path}")
            result = await server_tool.analyze_document(code_path, **kwargs)
            
            # Log usage for analytics
            await self._log_server_usage("analysis", code_path, result.success)
            return result
        else:
            logger.warning("⚠️ No analysis-capable MCP server available") 
            return MCPResult(
                success=False,
                error="No analysis server available", 
                capability_used="analysis"
            )
    
    async def execute_documentation_generation(self, topic: str, **kwargs) -> MCPResult:
        """Execute documentation generation on the best available documentation server.""" 
        server_tool = await self.get_server_for_capability("documentation")
        
        if server_tool:
            logger.info(f"📝 Executing documentation generation via MCP server: {topic}")
            result = await server_tool.generate_documentation(topic, **kwargs)
            
            # Log usage for analytics
            await self._log_server_usage("documentation", topic, result.success)
            return result
        else:
            logger.warning("⚠️ No documentation-capable MCP server available")
            return MCPResult(
                success=False,
                error="No documentation server available",
                capability_used="documentation"
            )
    
    async def _log_server_usage(self, capability: str, query: str, success: bool):
        """Log server usage for analytics and optimization."""
        try:
            usage_data = {
                "capability": capability,
                "query_hash": hash(query) % 10000,  # Hash for privacy
                "success": success,
                "timestamp": datetime.now().isoformat(),
                "query_length": len(query)
            }
            
            await self.memory_store.store_memory(
                f"mcp_usage_{capability}",
                "analytics", 
                usage_data,
                metadata={"type": "mcp_usage", "capability": capability}
            )
            
        except Exception as e:
            logger.warning(f"Failed to log MCP usage: {e}")
    
    def get_server_status_summary(self) -> Dict[str, Any]:
        """Get a summary of all server statuses."""
        return {
            "total_servers": len(self.known_servers),
            "active_servers": len(self.active_servers), 
            "server_tools": len(self.server_tools),
            "servers": [
                {
                    "id": server_id[:8] + "...",
                    "name": known_server.name,
                    "status": "active" if server_id in self.active_servers else "inactive",
                    "capabilities": len(known_server.capabilities),
                    "priority": known_server.priority
                }
                for server_id, known_server in self.known_servers.items()
            ]
        }


# Global registry instance
_global_registry: Optional[EnhancedMCPRegistry] = None


async def get_mcp_registry(memory_store: Optional[IntelligentMemoryStore] = None) -> EnhancedMCPRegistry:
    """Get or create the global MCP registry instance."""
    global _global_registry
    
    if _global_registry is None:
        _global_registry = EnhancedMCPRegistry(memory_store)
        await _global_registry.initialize_servers()
    
    return _global_registry


async def ensure_mcp_servers_for_agents():
    """Ensure MCP servers are initialized and ready for agent use."""
    registry = await get_mcp_registry()
    status = registry.get_server_status_summary()
    
    if status["active_servers"] == 0:
        logger.warning("⚠️ No MCP servers are active - attempting re-initialization...")
        await registry.initialize_servers()
        status = registry.get_server_status_summary()
    
    return status["active_servers"] > 0
