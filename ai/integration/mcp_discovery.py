"""Advanced MCP Server Discovery and Integration System.

This module provides intelligent discovery, capability mapping, and enhanced
integration with MCP servers for research and documentation tasks. It includes
automatic server discovery, health monitoring, and dynamic capability routing.

Cross-references:
    - MCP Client: ai/tools/mcp_client.py for core MCP functionality
    - Agent Spawner: ai/interface/agent_spawner.py for tool assignment
    - Performance Analytics: ai/analytics/performance.py for server metrics
    - Memory System: ai/memory/README.md for capability caching

Related:
    - Dynamic server discovery and health monitoring
    - Intelligent capability mapping and routing
    - Enhanced error handling and retry mechanisms
    - Automated server performance optimization
"""
from __future__ import annotations
import asyncio
import json
import logging
import subprocess
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Set, Tuple, Union
from dataclasses import dataclass, field
from pathlib import Path
from urllib.parse import urlparse
import aiohttp
import socket

from ai.memory.store import get_store
from ai.tools.memory_tools import WriteMemory, ReadMemoryContext

logger = logging.getLogger(__name__)


@dataclass
class MCPServerCapability:
    """Represents a specific capability of an MCP server."""
    name: str
    description: str
    parameters: Dict[str, Any]
    category: str  # research, documentation, analysis, etc.
    confidence_score: float = 1.0
    usage_count: int = 0
    success_rate: float = 1.0
    avg_response_time: float = 0.0
    last_used: Optional[datetime] = None


@dataclass
class MCPServerInfo:
    """Information about a discovered MCP server."""
    server_id: str
    name: str
    url: Optional[str] = None
    process_info: Optional[Dict[str, Any]] = None
    capabilities: List[MCPServerCapability] = field(default_factory=list)
    status: str = "unknown"  # unknown, healthy, degraded, failed
    last_health_check: Optional[datetime] = None
    discovery_method: str = "unknown"  # process, network, configuration
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Performance metrics
    uptime_start: Optional[datetime] = None
    total_requests: int = 0
    successful_requests: int = 0
    avg_response_time: float = 0.0
    error_rate: float = 0.0


@dataclass
class CapabilityRequest:
    """Request for a specific capability from MCP servers."""
    request_id: str
    capability_category: str
    task_description: str
    parameters: Dict[str, Any]
    priority: int = 1  # 1=low, 5=critical
    timeout_seconds: int = 30
    retry_attempts: int = 3
    preferred_servers: List[str] = field(default_factory=list)


class MCPDiscoverySystem:
    """Advanced MCP server discovery and integration system."""
    
    def __init__(self):
        self.discovered_servers: Dict[str, MCPServerInfo] = {}
        self.capability_index: Dict[str, List[str]] = {}  # category -> server_ids
        self.server_cache: Dict[str, Dict[str, Any]] = {}
        self.health_check_interval = 60  # seconds
        self.discovery_interval = 300  # seconds
        
        # Performance tracking
        self.request_history: List[Dict[str, Any]] = []
        self.server_performance: Dict[str, List[float]] = {}
        
        # Background tasks
        self._health_monitor_task: Optional[asyncio.Task] = None
        self._discovery_task: Optional[asyncio.Task] = None
        self._shutdown_event = asyncio.Event()
        
    async def start_discovery(self):
        """Start the MCP discovery and monitoring system."""
        logger.info("Starting MCP discovery system...")
        
        # Initial discovery
        await self.discover_servers()
        
        # Start background tasks
        self._health_monitor_task = asyncio.create_task(self._health_monitoring_loop())
        self._discovery_task = asyncio.create_task(self._discovery_loop())
        
        logger.info(f"MCP discovery system started with {len(self.discovered_servers)} servers")
        
    async def stop_discovery(self):
        """Stop the MCP discovery system."""
        logger.info("Stopping MCP discovery system...")
        
        self._shutdown_event.set()
        
        # Cancel background tasks
        for task in [self._health_monitor_task, self._discovery_task]:
            if task and not task.done():
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
                    
        logger.info("MCP discovery system stopped")
        
    async def discover_servers(self) -> List[MCPServerInfo]:
        """Discover available MCP servers using multiple methods."""
        logger.info("Starting comprehensive MCP server discovery...")
        
        discovered = []
        
        # Method 1: Process-based discovery
        process_servers = await self._discover_process_servers()
        discovered.extend(process_servers)
        
        # Method 2: Network-based discovery
        network_servers = await self._discover_network_servers()
        discovered.extend(network_servers)
        
        # Method 3: Configuration-based discovery
        config_servers = await self._discover_config_servers()
        discovered.extend(config_servers)
        
        # Method 4: Well-known server discovery
        wellknown_servers = await self._discover_wellknown_servers()
        discovered.extend(wellknown_servers)
        
        # Update server registry
        for server in discovered:
            self.discovered_servers[server.server_id] = server
            await self._probe_server_capabilities(server)
            
        # Update capability index
        self._update_capability_index()
        
        # Record discovery results
        WriteMemory(
            content=f"MCP server discovery completed: {len(discovered)} servers found",
            tags=["mcp", "discovery", "servers"]
        ).run()
        
        logger.info(f"Discovery completed: {len(discovered)} servers registered")
        return discovered
        
    async def _discover_process_servers(self) -> List[MCPServerInfo]:
        """Discover MCP servers running as local processes."""
        servers = []
        
        try:
            # Look for known MCP server processes
            result = subprocess.run(
                ["ps", "aux"], 
                capture_output=True, 
                text=True, 
                check=True
            )
            
            mcp_processes = []
            for line in result.stdout.split('\n'):
                if any(keyword in line.lower() for keyword in [
                    'mcp-server', 'mcp_server', 'model-context-protocol',
                    'anthropic-mcp', 'claude-mcp', 'openai-mcp'
                ]):
                    mcp_processes.append(line)
                    
            for i, process_line in enumerate(mcp_processes):
                parts = process_line.split()
                if len(parts) >= 11:
                    pid = parts[1]
                    command = ' '.join(parts[10:])
                    
                    server = MCPServerInfo(
                        server_id=f"process_{pid}",
                        name=f"Local MCP Server (PID {pid})",
                        process_info={
                            "pid": pid,
                            "command": command,
                            "user": parts[0],
                            "cpu": parts[2],
                            "memory": parts[3]
                        },
                        discovery_method="process",
                        status="discovered"
                    )
                    servers.append(server)
                    
        except subprocess.CalledProcessError as e:
            logger.warning(f"Failed to discover process-based MCP servers: {e}")
            
        return servers
        
    async def _discover_network_servers(self) -> List[MCPServerInfo]:
        """Discover MCP servers on the local network."""
        servers = []
        
        # Common MCP server ports
        common_ports = [3000, 3001, 8000, 8001, 8080, 8888, 9000, 9001]
        
        # Scan localhost for MCP servers
        for port in common_ports:
            try:
                # Quick connection test
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1.0)
                result = sock.connect_ex(('localhost', port))
                sock.close()
                
                if result == 0:  # Connection successful
                    # Try to identify if it's an MCP server
                    try:
                        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=2)) as session:
                            # Try common MCP endpoints
                            for path in ['/', '/mcp', '/health', '/capabilities']:
                                try:
                                    async with session.get(f"http://localhost:{port}{path}") as response:
                                        if response.status == 200:
                                            text = await response.text()
                                            if any(keyword in text.lower() for keyword in [
                                                'mcp', 'model context protocol', 'anthropic', 'claude'
                                            ]):
                                                server = MCPServerInfo(
                                                    server_id=f"network_localhost_{port}",
                                                    name=f"Network MCP Server (:{port})",
                                                    url=f"http://localhost:{port}",
                                                    discovery_method="network",
                                                    status="discovered",
                                                    metadata={"port": port, "endpoint": path}
                                                )
                                                servers.append(server)
                                                break
                                except:
                                    continue
                    except:
                        pass
                        
            except Exception:
                continue
                
        return servers
        
    async def _discover_config_servers(self) -> List[MCPServerInfo]:
        """Discover MCP servers from configuration files."""
        servers = []
        
        # Look for MCP configuration files
        config_locations = [
            Path.home() / ".mcp" / "servers.json",
            Path.home() / ".config" / "mcp" / "servers.json",
            Path.cwd() / "mcp_servers.json",
            Path.cwd() / ".mcp" / "servers.json",
            Path("/etc/mcp/servers.json")
        ]
        
        for config_path in config_locations:
            if config_path.exists():
                try:
                    with open(config_path, 'r') as f:
                        config = json.load(f)
                        
                    if isinstance(config, dict) and 'servers' in config:
                        for server_id, server_config in config['servers'].items():
                            server = MCPServerInfo(
                                server_id=f"config_{server_id}",
                                name=server_config.get('name', server_id),
                                url=server_config.get('url'),
                                discovery_method="configuration",
                                status="configured",
                                metadata=server_config
                            )
                            servers.append(server)
                            
                except (json.JSONDecodeError, KeyError) as e:
                    logger.warning(f"Invalid MCP config file {config_path}: {e}")
                except Exception as e:
                    logger.warning(f"Failed to read MCP config {config_path}: {e}")
                    
        return servers
        
    async def _discover_wellknown_servers(self) -> List[MCPServerInfo]:
        """Discover well-known MCP servers and services."""
        servers = []
        
        # Well-known MCP servers
        wellknown_servers = [
            {
                "id": "anthropic_research",
                "name": "Anthropic Research MCP",
                "url": "https://api.anthropic.com/mcp",
                "capabilities": ["research", "analysis", "reasoning"]
            },
            {
                "id": "openai_research",
                "name": "OpenAI Research MCP", 
                "url": "https://api.openai.com/mcp",
                "capabilities": ["research", "documentation", "analysis"]
            },
            {
                "id": "local_filesystem",
                "name": "Local Filesystem MCP",
                "capabilities": ["filesystem", "documentation", "file_analysis"]
            },
            {
                "id": "web_research",
                "name": "Web Research MCP",
                "capabilities": ["web_search", "research", "information_gathering"]
            }
        ]
        
        for server_info in wellknown_servers:
            server = MCPServerInfo(
                server_id=f"wellknown_{server_info['id']}",
                name=server_info["name"],
                url=server_info.get("url"),
                discovery_method="wellknown",
                status="available",
                metadata=server_info
            )
            
            # Add predefined capabilities
            for cap_name in server_info.get("capabilities", []):
                capability = MCPServerCapability(
                    name=cap_name,
                    description=f"{cap_name} capability",
                    parameters={},
                    category=cap_name,
                    confidence_score=0.8  # Lower confidence for predefined
                )
                server.capabilities.append(capability)
                
            servers.append(server)
            
        return servers
        
    async def _probe_server_capabilities(self, server: MCPServerInfo):
        """Probe a server to discover its actual capabilities."""
        if server.status == "failed":
            return
            
        try:
            # Try to get capabilities through various methods
            capabilities = []
            
            if server.url:
                capabilities.extend(await self._probe_http_capabilities(server))
            elif server.process_info:
                capabilities.extend(await self._probe_process_capabilities(server))
                
            # Update server capabilities
            server.capabilities.extend(capabilities)
            server.status = "healthy" if capabilities else "limited"
            server.last_health_check = datetime.now()
            
        except Exception as e:
            logger.warning(f"Failed to probe capabilities for {server.name}: {e}")
            server.status = "failed"
            
    async def _probe_http_capabilities(self, server: MCPServerInfo) -> List[MCPServerCapability]:
        """Probe HTTP-based MCP server capabilities."""
        capabilities = []
        
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=5)) as session:
                # Try standard MCP endpoints
                endpoints = ['/capabilities', '/tools', '/resources', '/methods']
                
                for endpoint in endpoints:
                    try:
                        async with session.get(f"{server.url}{endpoint}") as response:
                            if response.status == 200:
                                data = await response.json()
                                
                                # Parse capabilities from response
                                if isinstance(data, dict):
                                    for key, value in data.items():
                                        if isinstance(value, dict) and 'description' in value:
                                            capability = MCPServerCapability(
                                                name=key,
                                                description=value['description'],
                                                parameters=value.get('parameters', {}),
                                                category=self._categorize_capability(key, value),
                                                confidence_score=0.9
                                            )
                                            capabilities.append(capability)
                                            
                    except Exception:
                        continue
                        
        except Exception as e:
            logger.debug(f"HTTP capability probing failed for {server.name}: {e}")
            
        return capabilities
        
    async def _probe_process_capabilities(self, server: MCPServerInfo) -> List[MCPServerCapability]:
        """Probe process-based MCP server capabilities."""
        capabilities = []
        
        # For process-based servers, try to infer capabilities from command
        if server.process_info and 'command' in server.process_info:
            command = server.process_info['command'].lower()
            
            # Infer capabilities from command line
            capability_keywords = {
                'filesystem': ['file', 'fs', 'directory', 'path'],
                'research': ['search', 'research', 'web', 'api'],
                'documentation': ['doc', 'markdown', 'wiki', 'help'],
                'analysis': ['analyze', 'process', 'parse', 'extract'],
                'database': ['db', 'sql', 'postgres', 'mysql', 'mongo']
            }
            
            for category, keywords in capability_keywords.items():
                if any(keyword in command for keyword in keywords):
                    capability = MCPServerCapability(
                        name=f"{category}_capability",
                        description=f"Inferred {category} capability",
                        parameters={},
                        category=category,
                        confidence_score=0.6  # Lower confidence for inferred
                    )
                    capabilities.append(capability)
                    
        return capabilities
        
    def _categorize_capability(self, name: str, info: Dict[str, Any]) -> str:
        """Categorize a capability based on its name and description."""
        name_lower = name.lower()
        desc_lower = info.get('description', '').lower()
        combined = f"{name_lower} {desc_lower}"
        
        categories = {
            'research': ['search', 'research', 'query', 'find', 'lookup'],
            'documentation': ['document', 'wiki', 'help', 'manual', 'guide'],
            'filesystem': ['file', 'directory', 'path', 'read', 'write'],
            'analysis': ['analyze', 'process', 'parse', 'extract', 'compute'],
            'communication': ['message', 'email', 'chat', 'notify'],
            'database': ['database', 'sql', 'query', 'table', 'record'],
            'web': ['http', 'web', 'url', 'scrape', 'crawl'],
            'ai': ['model', 'ai', 'ml', 'predict', 'generate']
        }
        
        for category, keywords in categories.items():
            if any(keyword in combined for keyword in keywords):
                return category
                
        return 'general'
        
    def _update_capability_index(self):
        """Update the capability index for fast lookups."""
        self.capability_index.clear()
        
        for server_id, server in self.discovered_servers.items():
            if server.status in ['healthy', 'limited', 'available']:
                for capability in server.capabilities:
                    category = capability.category
                    if category not in self.capability_index:
                        self.capability_index[category] = []
                    self.capability_index[category].append(server_id)
                    
    async def find_capable_servers(
        self, 
        capability_category: str, 
        min_confidence: float = 0.5,
        max_servers: int = 3
    ) -> List[MCPServerInfo]:
        """Find servers capable of handling a specific capability category."""
        candidate_servers = []
        
        # Get servers for this capability category
        server_ids = self.capability_index.get(capability_category, [])
        
        for server_id in server_ids:
            server = self.discovered_servers.get(server_id)
            if not server or server.status == "failed":
                continue
                
            # Find relevant capabilities
            relevant_caps = [
                cap for cap in server.capabilities 
                if cap.category == capability_category and cap.confidence_score >= min_confidence
            ]
            
            if relevant_caps:
                # Calculate server score based on performance and confidence
                performance_score = (server.successful_requests / max(server.total_requests, 1)) * 0.7
                confidence_score = max(cap.confidence_score for cap in relevant_caps) * 0.3
                total_score = performance_score + confidence_score
                
                candidate_servers.append((total_score, server))
                
        # Sort by score and return top servers
        candidate_servers.sort(key=lambda x: x[0], reverse=True)
        return [server for _, server in candidate_servers[:max_servers]]
        
    async def execute_capability_request(self, request: CapabilityRequest) -> Dict[str, Any]:
        """Execute a capability request using the best available servers."""
        logger.info(f"Executing capability request: {request.capability_category}")
        
        # Find capable servers
        servers = await self.find_capable_servers(
            request.capability_category,
            min_confidence=0.3,  # Lower threshold for execution
            max_servers=3
        )
        
        if not servers:
            return {
                "success": False,
                "error": f"No servers available for capability: {request.capability_category}",
                "request_id": request.request_id
            }
            
        # Try servers in order of preference
        last_error = None
        
        for attempt in range(request.retry_attempts):
            for server in servers:
                try:
                    start_time = time.time()
                    
                    # Execute the request
                    result = await self._execute_on_server(server, request)
                    
                    # Record successful execution
                    execution_time = time.time() - start_time
                    await self._record_request_result(server, request, True, execution_time)
                    
                    return {
                        "success": True,
                        "result": result,
                        "server_used": server.server_id,
                        "execution_time": execution_time,
                        "request_id": request.request_id
                    }
                    
                except Exception as e:
                    last_error = str(e)
                    execution_time = time.time() - start_time
                    await self._record_request_result(server, request, False, execution_time, str(e))
                    
                    logger.warning(f"Request failed on {server.name}: {e}")
                    continue
                    
            # Brief delay between retry attempts
            if attempt < request.retry_attempts - 1:
                await asyncio.sleep(0.5 * (attempt + 1))
                
        return {
            "success": False,
            "error": f"All servers failed. Last error: {last_error}",
            "request_id": request.request_id,
            "servers_tried": [s.server_id for s in servers]
        }
        
    async def _execute_on_server(self, server: MCPServerInfo, request: CapabilityRequest) -> Any:
        """Execute a request on a specific server."""
        # This is a placeholder for actual MCP protocol execution
        # In a real implementation, this would use the MCP client protocol
        
        if server.url:
            return await self._execute_http_request(server, request)
        elif server.process_info:
            return await self._execute_process_request(server, request)
        else:
            raise Exception("Server has no execution method available")
            
    async def _execute_http_request(self, server: MCPServerInfo, request: CapabilityRequest) -> Any:
        """Execute request via HTTP to MCP server."""
        async with aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=request.timeout_seconds)
        ) as session:
            payload = {
                "method": "execute_capability",
                "params": {
                    "capability": request.capability_category,
                    "task": request.task_description,
                    "parameters": request.parameters
                },
                "id": request.request_id
            }
            
            async with session.post(
                f"{server.url}/execute",
                json=payload
            ) as response:
                response.raise_for_status()
                return await response.json()
                
    async def _execute_process_request(self, server: MCPServerInfo, request: CapabilityRequest) -> Any:
        """Execute request via process communication."""
        # Placeholder for process-based MCP communication
        # This would typically use stdin/stdout JSON-RPC
        return {
            "result": f"Simulated result from {server.name}",
            "capability": request.capability_category,
            "task": request.task_description
        }
        
    async def _record_request_result(
        self, 
        server: MCPServerInfo, 
        request: CapabilityRequest,
        success: bool, 
        execution_time: float,
        error: Optional[str] = None
    ):
        """Record the result of a request for performance tracking."""
        server.total_requests += 1
        if success:
            server.successful_requests += 1
            
        # Update average response time
        if server.avg_response_time == 0:
            server.avg_response_time = execution_time
        else:
            # Exponential moving average
            alpha = 0.1
            server.avg_response_time = (1 - alpha) * server.avg_response_time + alpha * execution_time
            
        # Update error rate
        server.error_rate = 1.0 - (server.successful_requests / server.total_requests)
        
        # Update capability usage
        for capability in server.capabilities:
            if capability.category == request.capability_category:
                capability.usage_count += 1
                capability.last_used = datetime.now()
                if success:
                    capability.success_rate = (
                        capability.success_rate * (capability.usage_count - 1) + 1.0
                    ) / capability.usage_count
                else:
                    capability.success_rate = (
                        capability.success_rate * (capability.usage_count - 1)
                    ) / capability.usage_count
                break
                
        # Record in request history
        self.request_history.append({
            "timestamp": datetime.now(),
            "server_id": server.server_id,
            "capability": request.capability_category,
            "success": success,
            "execution_time": execution_time,
            "error": error
        })
        
        # Keep only recent history
        if len(self.request_history) > 1000:
            self.request_history = self.request_history[-500:]
            
    async def _health_monitoring_loop(self):
        """Continuous health monitoring of discovered servers."""
        while not self._shutdown_event.is_set():
            try:
                await asyncio.sleep(self.health_check_interval)
                await self._perform_health_checks()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in health monitoring: {e}")
                await asyncio.sleep(5)
                
    async def _discovery_loop(self):
        """Periodic server discovery to find new servers."""
        while not self._shutdown_event.is_set():
            try:
                await asyncio.sleep(self.discovery_interval)
                await self.discover_servers()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in discovery loop: {e}")
                await asyncio.sleep(30)
                
    async def _perform_health_checks(self):
        """Perform health checks on all discovered servers."""
        for server in list(self.discovered_servers.values()):
            try:
                if server.url:
                    await self._health_check_http_server(server)
                elif server.process_info:
                    await self._health_check_process_server(server)
                    
                server.last_health_check = datetime.now()
                
            except Exception as e:
                logger.warning(f"Health check failed for {server.name}: {e}")
                server.status = "failed"
                
    async def _health_check_http_server(self, server: MCPServerInfo):
        """Perform health check on HTTP-based server."""
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=5)) as session:
                async with session.get(f"{server.url}/health") as response:
                    if response.status == 200:
                        server.status = "healthy"
                    else:
                        server.status = "degraded"
        except:
            server.status = "failed"
            
    async def _health_check_process_server(self, server: MCPServerInfo):
        """Perform health check on process-based server."""
        if not server.process_info or 'pid' not in server.process_info:
            server.status = "failed"
            return
            
        try:
            # Check if process is still running
            result = subprocess.run(
                ["ps", "-p", server.process_info['pid']],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                server.status = "healthy"
            else:
                server.status = "failed"
                
        except:
            server.status = "failed"
            
    def get_discovery_summary(self) -> Dict[str, Any]:
        """Get a summary of discovered servers and capabilities."""
        total_servers = len(self.discovered_servers)
        healthy_servers = len([s for s in self.discovered_servers.values() if s.status == "healthy"])
        total_capabilities = sum(len(s.capabilities) for s in self.discovered_servers.values())
        
        capability_categories = set()
        for server in self.discovered_servers.values():
            for cap in server.capabilities:
                capability_categories.add(cap.category)
                
        return {
            "total_servers": total_servers,
            "healthy_servers": healthy_servers,
            "failed_servers": len([s for s in self.discovered_servers.values() if s.status == "failed"]),
            "total_capabilities": total_capabilities,
            "capability_categories": sorted(list(capability_categories)),
            "discovery_methods": list(set(s.discovery_method for s in self.discovered_servers.values())),
            "average_response_time": sum(s.avg_response_time for s in self.discovered_servers.values() if s.avg_response_time > 0) / max(1, len([s for s in self.discovered_servers.values() if s.avg_response_time > 0]))
        }


# Global MCP discovery instance
_mcp_discovery: Optional[MCPDiscoverySystem] = None

def get_mcp_discovery() -> MCPDiscoverySystem:
    """Get the global MCP discovery system instance."""
    global _mcp_discovery
    if _mcp_discovery is None:
        _mcp_discovery = MCPDiscoverySystem()
    return _mcp_discovery
