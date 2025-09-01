"""Enhanced MCP Tool with Advanced Discovery Integration.

This module provides an enhanced MCP tool that integrates with the MCP discovery
system for intelligent server selection, automatic failover, and optimized
capability routing for research and documentation tasks.

Cross-references:
    - MCP Discovery: ai/integration/mcp_discovery.py for server discovery
    - MCP Client: ai/tools/mcp_client.py for basic MCP functionality
    - Memory System: ai/memory/README.md for result caching
    - Agent Development: docs/AGENT_DEVELOPMENT.md#tool-development

Related:
    - Intelligent server selection based on capability and performance
    - Automatic failover and retry mechanisms
    - Result caching for improved performance
    - Enhanced error handling and diagnostics
"""
from __future__ import annotations
import asyncio
import json
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass
import hashlib

from ai.integration.mcp_discovery import (
    get_mcp_discovery, 
    CapabilityRequest, 
    MCPDiscoverySystem
)
from ai.tools.memory_tools import WriteMemory, ReadMemoryContext

logger = logging.getLogger(__name__)


@dataclass
class MCPResult:
    """Result from an MCP operation with metadata."""
    success: bool
    result: Any = None
    error: Optional[str] = None
    server_used: Optional[str] = None
    execution_time: float = 0.0
    cached: bool = False
    capability_used: Optional[str] = None
    metadata: Dict[str, Any] = None


class EnhancedMCPTool:
    """Enhanced MCP tool with discovery integration and intelligent routing."""
    
    def __init__(self):
        self.discovery_system: Optional[MCPDiscoverySystem] = None
        self.result_cache: Dict[str, Dict[str, Any]] = {}
        self.cache_ttl = timedelta(minutes=30)
        self.request_counter = 0
        
    async def initialize(self):
        """Initialize the enhanced MCP tool with discovery system."""
        self.discovery_system = get_mcp_discovery()
        
        # Start discovery system if not already running
        try:
            await self.discovery_system.start_discovery()
            logger.info("Enhanced MCP tool initialized with discovery system")
        except Exception as e:
            logger.warning(f"Failed to start MCP discovery system: {e}")
            
    async def research_query(
        self,
        query: str,
        sources: Optional[List[str]] = None,
        max_results: int = 10,
        timeout: int = 30
    ) -> MCPResult:
        """Perform a research query using optimal MCP servers.
        
        Args:
            query: The research question or topic
            sources: Optional list of preferred sources/servers
            max_results: Maximum number of results to return
            timeout: Request timeout in seconds
            
        Returns:
            MCPResult with research findings and metadata
        """
        return await self._execute_capability_request(
            capability="research",
            task_description=f"Research query: {query}",
            parameters={
                "query": query,
                "sources": sources or [],
                "max_results": max_results
            },
            timeout_seconds=timeout
        )
        
    async def analyze_document(
        self,
        document_path: str,
        analysis_type: str = "comprehensive",
        extract_key_points: bool = True
    ) -> MCPResult:
        """Analyze a document using MCP servers with analysis capabilities.
        
        Args:
            document_path: Path to the document to analyze
            analysis_type: Type of analysis (comprehensive, summary, technical)
            extract_key_points: Whether to extract key points
            
        Returns:
            MCPResult with document analysis
        """
        return await self._execute_capability_request(
            capability="analysis",
            task_description=f"Analyze document: {document_path}",
            parameters={
                "document_path": document_path,
                "analysis_type": analysis_type,
                "extract_key_points": extract_key_points
            }
        )
        
    async def generate_documentation(
        self,
        topic: str,
        format_type: str = "markdown",
        include_examples: bool = True,
        cross_references: Optional[List[str]] = None
    ) -> MCPResult:
        """Generate documentation using MCP servers with documentation capabilities.
        
        Args:
            topic: The topic to document
            format_type: Output format (markdown, html, rst)
            include_examples: Whether to include code examples
            cross_references: List of related topics to cross-reference
            
        Returns:
            MCPResult with generated documentation
        """
        return await self._execute_capability_request(
            capability="documentation",
            task_description=f"Generate documentation for: {topic}",
            parameters={
                "topic": topic,
                "format": format_type,
                "include_examples": include_examples,
                "cross_references": cross_references or []
            }
        )
        
    async def web_search(
        self,
        search_terms: str,
        search_engines: Optional[List[str]] = None,
        result_count: int = 5,
        filter_duplicates: bool = True
    ) -> MCPResult:
        """Perform web search using MCP servers with web search capabilities.
        
        Args:
            search_terms: Search query terms
            search_engines: Preferred search engines to use
            result_count: Number of results to return
            filter_duplicates: Whether to filter duplicate results
            
        Returns:
            MCPResult with search results
        """
        return await self._execute_capability_request(
            capability="web_search",
            task_description=f"Web search: {search_terms}",
            parameters={
                "query": search_terms,
                "engines": search_engines or ["google", "bing", "duckduckgo"],
                "count": result_count,
                "filter_duplicates": filter_duplicates
            }
        )
        
    async def file_analysis(
        self,
        file_path: str,
        analysis_types: List[str] = None,
        extract_metadata: bool = True
    ) -> MCPResult:
        """Analyze a file using MCP servers with filesystem capabilities.
        
        Args:
            file_path: Path to the file to analyze
            analysis_types: Types of analysis to perform
            extract_metadata: Whether to extract file metadata
            
        Returns:
            MCPResult with file analysis
        """
        if analysis_types is None:
            analysis_types = ["content", "structure", "dependencies"]
            
        return await self._execute_capability_request(
            capability="filesystem",
            task_description=f"Analyze file: {file_path}",
            parameters={
                "file_path": file_path,
                "analysis_types": analysis_types,
                "extract_metadata": extract_metadata
            }
        )
        
    async def database_query(
        self,
        query: str,
        database_type: str = "auto",
        connection_params: Optional[Dict[str, Any]] = None
    ) -> MCPResult:
        """Execute a database query using MCP servers with database capabilities.
        
        Args:
            query: SQL or database query to execute
            database_type: Type of database (auto, postgres, mysql, sqlite)
            connection_params: Database connection parameters
            
        Returns:
            MCPResult with query results
        """
        return await self._execute_capability_request(
            capability="database",
            task_description=f"Database query: {query[:100]}...",
            parameters={
                "query": query,
                "database_type": database_type,
                "connection_params": connection_params or {}
            }
        )
        
    async def ai_analysis(
        self,
        data: Any,
        analysis_prompt: str,
        model_preferences: Optional[List[str]] = None
    ) -> MCPResult:
        """Perform AI-powered analysis using MCP servers with AI capabilities.
        
        Args:
            data: Data to analyze (text, structured data, etc.)
            analysis_prompt: Prompt describing the desired analysis
            model_preferences: Preferred AI models to use
            
        Returns:
            MCPResult with AI analysis results
        """
        return await self._execute_capability_request(
            capability="ai",
            task_description=f"AI analysis: {analysis_prompt}",
            parameters={
                "data": data,
                "prompt": analysis_prompt,
                "model_preferences": model_preferences or []
            }
        )
        
    async def multi_capability_request(
        self,
        requests: List[Dict[str, Any]],
        parallel_execution: bool = True,
        fail_fast: bool = False
    ) -> List[MCPResult]:
        """Execute multiple capability requests, optionally in parallel.
        
        Args:
            requests: List of capability requests
            parallel_execution: Whether to execute requests in parallel
            fail_fast: Whether to stop on first failure
            
        Returns:
            List of MCPResult objects
        """
        if parallel_execution:
            tasks = []
            for req in requests:
                task = self._execute_capability_request(
                    capability=req["capability"],
                    task_description=req["task_description"],
                    parameters=req.get("parameters", {}),
                    timeout_seconds=req.get("timeout", 30)
                )
                tasks.append(task)
                
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Convert exceptions to MCPResult errors
            final_results = []
            for result in results:
                if isinstance(result, Exception):
                    final_results.append(MCPResult(
                        success=False,
                        error=str(result)
                    ))
                else:
                    final_results.append(result)
                    
            return final_results
        else:
            results = []
            for req in requests:
                result = await self._execute_capability_request(
                    capability=req["capability"],
                    task_description=req["task_description"],
                    parameters=req.get("parameters", {}),
                    timeout_seconds=req.get("timeout", 30)
                )
                
                results.append(result)
                
                if fail_fast and not result.success:
                    break
                    
            return results
            
    async def get_server_status(self) -> Dict[str, Any]:
        """Get status of all discovered MCP servers.
        
        Returns:
            Dictionary with server status information
        """
        if not self.discovery_system:
            return {"error": "Discovery system not initialized"}
            
        return self.discovery_system.get_discovery_summary()
        
    async def refresh_server_discovery(self) -> Dict[str, Any]:
        """Force a refresh of MCP server discovery.
        
        Returns:
            Discovery results summary
        """
        if not self.discovery_system:
            return {"error": "Discovery system not initialized"}
            
        servers = await self.discovery_system.discover_servers()
        
        return {
            "servers_discovered": len(servers),
            "total_servers": len(self.discovery_system.discovered_servers),
            "discovery_summary": self.discovery_system.get_discovery_summary()
        }
        
    async def _execute_capability_request(
        self,
        capability: str,
        task_description: str,
        parameters: Dict[str, Any],
        timeout_seconds: int = 30,
        priority: int = 1
    ) -> MCPResult:
        """Execute a capability request with intelligent server selection."""
        if not self.discovery_system:
            return MCPResult(
                success=False,
                error="MCP discovery system not initialized"
            )
            
        # Generate cache key
        cache_key = self._generate_cache_key(capability, task_description, parameters)
        
        # Check cache first
        cached_result = self._get_cached_result(cache_key)
        if cached_result:
            return MCPResult(
                success=True,
                result=cached_result["result"],
                server_used=cached_result.get("server_used"),
                execution_time=0.0,
                cached=True,
                capability_used=capability
            )
            
        # Create capability request
        self.request_counter += 1
        request = CapabilityRequest(
            request_id=f"enhanced_mcp_{self.request_counter}_{int(time.time())}",
            capability_category=capability,
            task_description=task_description,
            parameters=parameters,
            timeout_seconds=timeout_seconds,
            priority=priority
        )
        
        # Execute request
        start_time = time.time()
        response = await self.discovery_system.execute_capability_request(request)
        execution_time = time.time() - start_time
        
        # Process response
        if response["success"]:
            # Cache successful result
            self._cache_result(cache_key, {
                "result": response["result"],
                "server_used": response.get("server_used"),
                "timestamp": datetime.now(),
                "capability": capability
            })
            
            # Record success in memory
            WriteMemory(
                content=f"MCP request successful: {capability} - {task_description[:100]}",
                tags=["mcp", "success", capability, "enhanced"]
            ).run()
            
            return MCPResult(
                success=True,
                result=response["result"],
                server_used=response.get("server_used"),
                execution_time=execution_time,
                cached=False,
                capability_used=capability,
                metadata=response
            )
        else:
            # Record failure in memory
            WriteMemory(
                content=f"MCP request failed: {capability} - {response.get('error', 'Unknown error')}",
                tags=["mcp", "error", capability, "enhanced"]
            ).run()
            
            return MCPResult(
                success=False,
                error=response.get("error", "Unknown error"),
                execution_time=execution_time,
                capability_used=capability,
                metadata=response
            )
            
    def _generate_cache_key(
        self, 
        capability: str, 
        task_description: str, 
        parameters: Dict[str, Any]
    ) -> str:
        """Generate a cache key for the request."""
        cache_data = {
            "capability": capability,
            "task": task_description,
            "params": parameters
        }
        
        cache_string = json.dumps(cache_data, sort_keys=True)
        return hashlib.sha256(cache_string.encode()).hexdigest()[:16]
        
    def _get_cached_result(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Get cached result if available and not expired."""
        if cache_key not in self.result_cache:
            return None
            
        cached = self.result_cache[cache_key]
        
        # Check if expired
        if datetime.now() - cached["timestamp"] > self.cache_ttl:
            del self.result_cache[cache_key]
            return None
            
        return cached
        
    def _cache_result(self, cache_key: str, result_data: Dict[str, Any]):
        """Cache a successful result."""
        self.result_cache[cache_key] = result_data
        
        # Clean up old cache entries periodically
        if len(self.result_cache) > 100:
            # Remove oldest entries
            sorted_entries = sorted(
                self.result_cache.items(),
                key=lambda x: x[1]["timestamp"]
            )
            
            # Keep only the most recent 50 entries
            for key, _ in sorted_entries[:-50]:
                del self.result_cache[key]


# Tool functions for agent use
async def research_with_mcp(
    query: str,
    sources: Optional[List[str]] = None,
    max_results: int = 10
) -> Dict[str, Any]:
    """Research query using enhanced MCP tool with intelligent server selection.
    
    This function provides intelligent research capabilities by automatically
    selecting the best available MCP servers based on their capabilities and
    performance metrics.
    
    Args:
        query: Research question or topic
        sources: Optional preferred sources/servers
        max_results: Maximum results to return
        
    Returns:
        Dictionary with research results and metadata
        
    Cross-references:
        - MCP Discovery: ai/integration/mcp_discovery.py for server selection
        - Memory Tools: ai/tools/memory_tools.py for result persistence
    """
    tool = EnhancedMCPTool()
    await tool.initialize()
    
    result = await tool.research_query(query, sources, max_results)
    
    return {
        "success": result.success,
        "result": result.result,
        "error": result.error,
        "server_used": result.server_used,
        "execution_time": result.execution_time,
        "cached": result.cached
    }


async def analyze_with_mcp(
    document_path: str,
    analysis_type: str = "comprehensive"
) -> Dict[str, Any]:
    """Analyze document using enhanced MCP tool with optimal server selection.
    
    This function provides document analysis capabilities by automatically
    routing requests to MCP servers with the best analysis capabilities.
    
    Args:
        document_path: Path to document to analyze
        analysis_type: Type of analysis to perform
        
    Returns:
        Dictionary with analysis results and metadata
    """
    tool = EnhancedMCPTool()
    await tool.initialize()
    
    result = await tool.analyze_document(document_path, analysis_type)
    
    return {
        "success": result.success,
        "result": result.result,
        "error": result.error,
        "server_used": result.server_used,
        "execution_time": result.execution_time
    }


async def generate_docs_with_mcp(
    topic: str,
    format_type: str = "markdown",
    include_examples: bool = True
) -> Dict[str, Any]:
    """Generate documentation using enhanced MCP tool with capability routing.
    
    This function provides documentation generation by selecting MCP servers
    with the best documentation capabilities and performance.
    
    Args:
        topic: Topic to document
        format_type: Output format
        include_examples: Whether to include examples
        
    Returns:
        Dictionary with generated documentation and metadata
    """
    tool = EnhancedMCPTool()
    await tool.initialize()
    
    result = await tool.generate_documentation(topic, format_type, include_examples)
    
    return {
        "success": result.success,
        "result": result.result,
        "error": result.error,
        "server_used": result.server_used,
        "execution_time": result.execution_time
    }


async def web_search_with_mcp(
    search_terms: str,
    result_count: int = 5
) -> Dict[str, Any]:
    """Perform web search using enhanced MCP tool with intelligent routing.
    
    This function provides web search capabilities by routing to the best
    available MCP servers with web search functionality.
    
    Args:
        search_terms: Terms to search for
        result_count: Number of results to return
        
    Returns:
        Dictionary with search results and metadata
    """
    tool = EnhancedMCPTool()
    await tool.initialize()
    
    result = await tool.web_search(search_terms, result_count=result_count)
    
    return {
        "success": result.success,
        "result": result.result,
        "error": result.error,
        "server_used": result.server_used,
        "execution_time": result.execution_time
    }
