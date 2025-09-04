"""
Product-Driven Autonomous Orchestrator

Enhanced version of the autonomous orchestrator that integrates Product Manager 
thinking into the agent spawn and task allocation process. Provides product-driven
autonomous development with RICE prioritization and strategic roadmap generation.
"""
from __future__ import annotations
import asyncio
import json
import logging
import time
import uuid
from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass, asdict, field
from datetime import datetime, timedelta
from pathlib import Path

from ai.orchestration.autonomous_orchestrator import AutonomousOrchestrator, AgentStatus, AutonomousAgent, OrchestrationConfig
from ai.agents.product_manager import ProductManagerAgent, FeatureSpecification
from ai.memory.intelligent_store import IntelligentMemoryStore
from ai.tools.enhanced_mcp import EnhancedMCPTool
from ai.integration.mcp_discovery import get_mcp_discovery
from ai.integration.mcp_server_registry import get_mcp_registry, ensure_mcp_servers_for_agents


@dataclass
class TaskRequest:
    """Base class for task requests."""
    task_id: str
    description: str
    priority: int = 5
    requested_at: datetime = field(default_factory=datetime.now)
    

@dataclass
class AgentInstance:
    """Represents an agent instance for compatibility."""
    id: str
    status: AgentStatus
    task_id: str
    created_at: datetime = field(default_factory=datetime.now)


@dataclass 
class ProductTaskRequest(TaskRequest):
    """Enhanced task request with product manager analysis."""
    feature_specification: Optional[FeatureSpecification] = None
    rice_score: float = 0.0
    problem_severity: int = 5
    user_impact: str = "unknown"
    product_priority: str = "P2"
    

class ProductAutonomousOrchestrator:
    """Product-driven autonomous orchestrator with PM agent integration."""
    
    def __init__(self, memory_store: Optional[IntelligentMemoryStore] = None):
        self.memory_store = memory_store or IntelligentMemoryStore()
        self.config = OrchestrationConfig()
        self.agents: Dict[str, AutonomousAgent] = {}
        self.total_cost_usd = 0.0
        self.start_time = datetime.now()
        self.is_running = False
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
        
        # MCP integration
        self.mcp_tool: Optional[EnhancedMCPTool] = None
        self.mcp_servers_available = False
        self.product_manager = ProductManagerAgent()
        self.feature_roadmap: Dict[str, Any] = {}
        self.prioritized_features: List[Tuple[Dict[str, Any], float]] = []
        
        # Product-specific configuration
        self.min_rice_score = 5.0  # Minimum RICE score to auto-approve
        self.auto_approve_quick_wins = True  # Auto-approve low effort, high impact
        self.generate_prds = True  # Generate PRD documents
        self.strategy_review_interval = 3600  # Review strategy every hour
        
        # Tracking
        self.prd_documents: Dict[str, str] = {}
        self.last_strategy_review = 0
        
        # Task management
        self.active_tasks: Dict[str, TaskRequest] = {}
        
        self.logger.info(f"🎯 Product-driven orchestrator initialized with PM agent v{self.product_manager.version}")
    
    async def spawn_agent(self, description: str, agent_name: Optional[str] = None, auto_approve: bool = False) -> str:
        """Spawn a regular agent (for compatibility)."""
        agent_id = f"agent-{uuid.uuid4().hex[:8]}"
        agent = AutonomousAgent(
            id=agent_id,
            task_description=description,
            status=AgentStatus.STARTING
        )
        self.agents[agent_id] = agent
        return agent_id
    
    async def get_status(self) -> Dict[str, Any]:
        """Get orchestrator status (for compatibility)."""
        return {
            'active_agents': len([a for a in self.agents.values() if a.status not in [AgentStatus.COMPLETED, AgentStatus.FAILED]]),
            'total_tasks': len(self.active_tasks),
            'total_cost': self.total_cost_usd,
            'runtime': str(datetime.now() - self.start_time).split('.')[0]
        }
    
    async def initialize_product_strategy(self):
        """Initialize the product strategy and roadmap."""
        try:
            self.logger.info("🚀 Initializing product strategy...")
            
            # Initialize MCP integration first
            await self._initialize_mcp_capabilities()
            
            # Scan for features that need product analysis
            scan_result = await self._scan_features_for_analysis()
            
            if scan_result.get('features'):
                # Generate product roadmap
                self.feature_roadmap = self.product_manager.generate_product_roadmap(
                    scan_result['features'], 
                    time_horizon=90
                )
                
                # Prioritize features using RICE
                self.prioritized_features = self.product_manager.prioritize_features(
                    scan_result['features']
                )
                
                self.logger.info(f"📋 Product roadmap generated with {len(self.prioritized_features)} prioritized features")
                
                # Store roadmap in memory
                await self.memory_store.store_memory(
                    "product_roadmap",
                    "system",
                    {
                        "roadmap": self.feature_roadmap,
                        "prioritized_features": [(f, s.score) for f, s in self.prioritized_features],
                        "generated_at": datetime.now().isoformat()
                    },
                    metadata={"type": "product_strategy", "source": "pm_agent"}
                )
                
            else:
                self.logger.warning("⚠️ No features found for product analysis")
                
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize product strategy: {e}")
    
    async def _initialize_mcp_capabilities(self):
        """Initialize MCP server integration for enhanced agent capabilities."""
        try:
            self.logger.info("🔌 Initializing MCP server integration with known servers...")
            
            # Initialize enhanced MCP registry with known servers
            self.mcp_registry = await get_mcp_registry(self.memory_store)
            
            # Ensure servers are ready for agents
            self.mcp_servers_available = await ensure_mcp_servers_for_agents()
            
            # Get server status summary
            server_status = self.mcp_registry.get_server_status_summary()
            
            if self.mcp_servers_available:
                active_count = server_status["active_servers"]
                total_count = server_status["total_servers"]
                
                self.logger.info(f"✅ MCP integration ready: {active_count}/{total_count} servers active")
                
                # Log detailed server information
                for server_info in server_status["servers"]:
                    status_emoji = "✅" if server_info["status"] == "active" else "❌"
                    self.logger.info(f"  {status_emoji} {server_info['name']} ({server_info['id']}) - {server_info['capabilities']} capabilities")
                
                # Store enhanced MCP registry reference for agents
                self.mcp_tool = self.mcp_registry  # Use registry instead of basic tool
                
                self.logger.info("🎆 Agents now have access to:")
                self.logger.info("  • Reference Server (688cf28d...): Documentation, examples, templates")
                self.logger.info("  • Analysis Server (613c9e91...): Code analysis, security audits, performance")
                self.logger.info("  • Research Server (a62d40d5...): Web search, competitive analysis, benchmarking")
            else:
                self.logger.warning("⚠️ No MCP servers active - agents will have limited external capabilities")
                
        except Exception as e:
            self.logger.warning(f"⚠️ MCP initialization failed: {e} - proceeding without MCP capabilities")
            self.mcp_servers_available = False
    
    async def _scan_features_for_analysis(self) -> Dict[str, Any]:
        """Scan codebase for features that need product analysis."""
        try:
            from ai.cli.fresh import scan_command
            
            # Run feature scan to get current feature inventory
            scan_result = scan_command(".", output_format="json")
            
            if scan_result and scan_result.get('features'):
                # Transform scan results to product manager format
                features = []
                for feature_name, feature_data in scan_result['features'].items():
                    features.append({
                        'name': feature_name,
                        'description': feature_data.get('description', ''),
                        'issues': feature_data.get('issues', []),
                        'status': feature_data.get('status', 'unknown'),
                        'path': feature_data.get('path', '')
                    })
                
                return {
                    'features': features,
                    'total_count': len(features),
                    'scanned_at': datetime.now().isoformat()
                }
            
            return {'features': [], 'total_count': 0}
            
        except Exception as e:
            self.logger.error(f"❌ Feature scan failed: {e}")
            return {'features': [], 'total_count': 0}
    
    async def spawn_agent_with_product_analysis(self, task_description: str, 
                                              feature_data: Optional[Dict[str, Any]] = None) -> str:
        """Spawn agent with full product manager analysis."""
        
        try:
            # If no feature data provided, try to extract from task description
            if not feature_data:
                feature_data = self._extract_feature_from_task(task_description)
            
            # Run product manager analysis
            if feature_data:
                try:
                    feature_spec = self.product_manager.analyze_feature_request(feature_data)
                    
                    # Create enhanced task request
                    task_request = ProductTaskRequest(
                        task_id=f"pm-task-{int(time.time())}",
                        description=task_description,
                        priority=self._map_rice_to_priority(feature_spec.rice_score.score),
                        requested_at=datetime.now(),
                        feature_specification=feature_spec,
                        rice_score=feature_spec.rice_score.score,
                        problem_severity=feature_spec.problem_analysis.severity_score,
                        user_impact=feature_spec.problem_analysis.affected_users[0] if feature_spec.problem_analysis.affected_users else "unknown",
                        product_priority=self._determine_product_priority(feature_spec)
                    )
                    
                    # Generate PRD if enabled
                    if self.generate_prds:
                        prd_content = self.product_manager.create_prd_document(feature_spec)
                        self.prd_documents[task_request.task_id] = prd_content
                        
                        # Save PRD to file
                        prd_path = Path(f"docs/prds/PRD-{feature_spec.feature_name.replace(' ', '-')}.md")
                        prd_path.parent.mkdir(parents=True, exist_ok=True)
                        prd_path.write_text(prd_content)
                        
                        self.logger.info(f"📄 PRD generated: {prd_path}")
                    
                    # Determine if auto-approval is appropriate
                    auto_approve = self._should_auto_approve_product_task(feature_spec)
                    
                    # Enhanced task description with product context
                    enhanced_description = self._create_enhanced_task_description(task_description, feature_spec)
                    
                    # Spawn agent with enhanced context
                    agent_id = await super().spawn_agent(
                        enhanced_description,
                        agent_name=f"ProductAgent-{feature_spec.feature_name.replace(' ', '')}",
                        auto_approve=auto_approve
                    )
                    
                    # Store product task request
                    self.active_tasks[task_request.task_id] = task_request
                    
                    self.logger.info(f"🎯 Product-driven agent spawned: {agent_id} (RICE: {feature_spec.rice_score.score:.1f})")
                    
                    return agent_id
                    
                except ValueError as e:
                    # Feature didn't meet PM criteria
                    self.logger.warning(f"⚠️ Feature rejected by PM analysis: {e}")
                    return await super().spawn_agent(task_description)  # Fall back to regular spawn
            
            else:
                # No feature data available, use regular spawn
                return await super().spawn_agent(task_description)
                
        except Exception as e:
            self.logger.error(f"❌ Product analysis failed: {e}")
            return await super().spawn_agent(task_description)  # Fall back to regular spawn
    
    def _extract_feature_from_task(self, task_description: str) -> Optional[Dict[str, Any]]:
        """Extract feature information from task description."""
        # Simple extraction - could be enhanced with NLP
        if "hook up" in task_description.lower() or "add cli" in task_description.lower():
            # Extract feature name (basic pattern matching)
            words = task_description.split()
            for i, word in enumerate(words):
                if word.lower() in ["hook", "add", "implement"] and i + 1 < len(words):
                    feature_name = words[i + 1].strip(".,!?")
                    return {
                        'name': feature_name,
                        'description': task_description,
                        'issues': ['not accessible via CLI'],
                        'status': 'needs_hookup'
                    }
        
        return None
    
    def _map_rice_to_priority(self, rice_score: float) -> int:
        """Map RICE score to numeric priority."""
        if rice_score >= 20:
            return 1  # Highest priority
        elif rice_score >= 10:
            return 2  # High priority
        elif rice_score >= 5:
            return 3  # Medium priority
        else:
            return 4  # Low priority
    
    def _determine_product_priority(self, spec: FeatureSpecification) -> str:
        """Determine product priority (P0, P1, P2) from feature spec."""
        if spec.problem_analysis.severity_score >= 8 and spec.rice_score.score >= 15:
            return "P0"
        elif spec.problem_analysis.severity_score >= 6 and spec.rice_score.score >= 8:
            return "P1"
        else:
            return "P2"
    
    def _should_auto_approve_product_task(self, spec: FeatureSpecification) -> bool:
        """Determine if a product task should be auto-approved."""
        
        # Auto-approve high RICE score features
        if spec.rice_score.score >= self.min_rice_score:
            return True
        
        # Auto-approve quick wins if enabled
        if (self.auto_approve_quick_wins and 
            spec.rice_score.effort <= 0.5 and 
            spec.rice_score.impact >= 1.0):
            return True
        
        # Auto-approve critical issues
        if spec.problem_analysis.severity_score >= 8:
            return True
        
        return False
    
    def _create_enhanced_task_description(self, original: str, spec: FeatureSpecification) -> str:
        """Create enhanced task description with product context and MCP capabilities."""
        
        # Build MCP capabilities section if available
        mcp_context = ""
        if self.mcp_servers_available and hasattr(self, 'mcp_registry'):
            mcp_context = f"""

🎆 ENHANCED MCP SERVER ACCESS:
You have direct access to specialized MCP servers for advanced development capabilities:

📚 REFERENCE SERVER (688cf28d-e69c-4624-b7cb-0725f36f9518):
• Documentation generation and examples
• Code templates and best practices
• Standard operation references
• Usage: await self.mcp_registry.execute_documentation_generation("topic")

🔍 ANALYSIS SERVER (613c9e91-4c54-43e9-b7c7-387c78d44459):
• Advanced code analysis and review
• Security audits and vulnerability scanning
• Performance analysis and optimization
• Architecture and dependency analysis
• Usage: await self.mcp_registry.execute_code_analysis("/path/to/code")

🔍 RESEARCH SERVER (a62d40d5-264a-4e05-bab3-b9da886ff14d):
• Comprehensive web search and data extraction
• Competitive analysis and market research  
• Technology trend analysis
• API and library discovery
• Usage: await self.mcp_registry.execute_research_query("research topic")

🛠️ MCP Integration Instructions:
1. Use the registry methods for high-level operations
2. All MCP calls are async - use await
3. Results include success status, data, and metadata
4. MCP servers provide enhanced capabilities beyond standard tools
5. Leverage research for competitive analysis and trend identification
6. Use analysis server for deep code reviews and security audits
7. Reference server provides authoritative documentation and examples

MCP Status: ✅ Servers initialized and ready for enhanced development
"""
        
        enhancement = f"""
PRODUCT CONTEXT:
Problem: {spec.problem_analysis.problem_statement}
RICE Score: {spec.rice_score.score:.1f} (Reach: {spec.rice_score.reach}, Impact: {spec.rice_score.impact}, Confidence: {spec.rice_score.confidence:.0%}, Effort: {spec.rice_score.effort}mo)
Priority: {spec.problem_analysis.severity_score}/10 severity

SUCCESS CRITERIA:
{chr(10).join(f'- {criteria}' for criteria in spec.user_story.acceptance_criteria)}

REQUIREMENTS:
{chr(10).join(f'- {req.requirement_id}: {req.description} ({req.priority})' for req in spec.requirements)}

PRIMARY METRIC: {spec.success_metrics['primary_metric']['name']}
Target: {spec.success_metrics['primary_metric']['target']}{mcp_context}

ORIGINAL TASK: {original}
"""
        return enhancement.strip()
    
    async def review_and_adjust_strategy(self):
        """Periodically review and adjust product strategy."""
        
        current_time = time.time()
        if current_time - self.last_strategy_review < self.strategy_review_interval:
            return
        
        self.logger.info("🔍 Reviewing product strategy...")
        
        try:
            # Re-scan features
            scan_result = await self._scan_features_for_analysis()
            
            # Check if new high-priority features have emerged
            if scan_result.get('features'):
                new_prioritized = self.product_manager.prioritize_features(scan_result['features'])
                
                # Compare with existing prioritization
                if len(new_prioritized) != len(self.prioritized_features):
                    self.logger.info(f"📊 Priority changes detected: {len(new_prioritized)} vs {len(self.prioritized_features)} features")
                    self.prioritized_features = new_prioritized
                    
                    # Update roadmap
                    self.feature_roadmap = self.product_manager.generate_product_roadmap(
                        scan_result['features']
                    )
                    
                    # Store updated strategy
                    await self.memory_store.store_memory(
                        "strategy_update",
                        "system", 
                        {
                            "updated_roadmap": self.feature_roadmap,
                            "priority_changes": len(new_prioritized),
                            "review_time": datetime.now().isoformat()
                        },
                        metadata={"type": "strategy_review", "source": "orchestrator"}
                    )
            
            self.last_strategy_review = current_time
            
        except Exception as e:
            self.logger.error(f"❌ Strategy review failed: {e}")
    
    async def get_next_product_task(self) -> Optional[ProductTaskRequest]:
        """Get the next highest priority product task."""
        
        await self.review_and_adjust_strategy()
        
        # Find highest priority unassigned feature
        for feature_data, rice_score in self.prioritized_features:
            # Check if already being worked on
            feature_name = feature_data.get('name', '')
            if not any(feature_name in task.description for task in self.active_tasks.values()):
                
                # Create product task request
                try:
                    spec = self.product_manager.analyze_feature_request(feature_data)
                    
                    return ProductTaskRequest(
                        task_id=f"auto-pm-{int(time.time())}",
                        description=f"Hook up {feature_name} functionality based on product analysis",
                        priority=self._map_rice_to_priority(rice_score.score),
                        requested_at=datetime.now(),
                        feature_specification=spec,
                        rice_score=rice_score.score,
                        problem_severity=spec.problem_analysis.severity_score,
                        user_impact=', '.join(spec.problem_analysis.affected_users),
                        product_priority=self._determine_product_priority(spec)
                    )
                    
                except ValueError:
                    continue  # Skip features that don't meet PM criteria
        
        return None
    
    async def generate_product_status_report(self) -> Dict[str, Any]:
        """Generate comprehensive product status report."""
        
        active_product_tasks = [
            task for task in self.active_tasks.values() 
            if isinstance(task, ProductTaskRequest)
        ]
        
        # Calculate metrics
        total_rice_score = sum(task.rice_score for task in active_product_tasks)
        avg_severity = sum(task.problem_severity for task in active_product_tasks) / max(len(active_product_tasks), 1)
        
        # Priority distribution
        priority_dist = {}
        for task in active_product_tasks:
            priority_dist[task.product_priority] = priority_dist.get(task.product_priority, 0) + 1
        
        # Get MCP server status if available
        mcp_status = {}
        if hasattr(self, 'mcp_registry') and self.mcp_registry:
            mcp_status = self.mcp_registry.get_server_status_summary()
            mcp_status["detailed_servers"] = [
                {
                    "name": "Reference Server",
                    "id": "688cf28d...",
                    "status": "active" if "688cf28d-e69c-4624-b7cb-0725f36f9518" in self.mcp_registry.active_servers else "inactive",
                    "capabilities": ["documentation", "examples", "templates"]
                },
                {
                    "name": "Analysis Server", 
                    "id": "613c9e91...",
                    "status": "active" if "613c9e91-4c54-43e9-b7c7-387c78d44459" in self.mcp_registry.active_servers else "inactive",
                    "capabilities": ["code_analysis", "security_audit", "performance"]
                },
                {
                    "name": "Research Server",
                    "id": "a62d40d5...", 
                    "status": "active" if "a62d40d5-264a-4e05-bab3-b9da886ff14d" in self.mcp_registry.active_servers else "inactive",
                    "capabilities": ["web_search", "competitive_analysis", "research"]
                }
            ]
        
        return {
            "timestamp": datetime.now().isoformat(),
            "orchestrator_status": await self.get_status(),
            "product_metrics": {
                "total_product_tasks": len(active_product_tasks),
                "total_rice_score": total_rice_score,
                "average_problem_severity": avg_severity,
                "priority_distribution": priority_dist
            },
            "roadmap_summary": {
                "strategic_themes": self.feature_roadmap.get("strategic_themes", []),
                "now_focus": self.feature_roadmap.get("now_0_30_days", {}).get("focus", ""),
                "next_focus": self.feature_roadmap.get("next_30_60_days", {}).get("focus", ""),
                "backlog_size": self.feature_roadmap.get("backlog", {}).get("features_count", 0)
            },
            "top_priorities": [
                {
                    "feature": feature.get('name', 'Unknown'),
                    "rice_score": score.score,
                    "problem_severity": score.reach * score.impact  # Simplified metric
                }
                for feature, score in self.prioritized_features[:5]
            ],
            "prd_documents": list(self.prd_documents.keys()),
            "pm_agent_version": self.product_manager.version,
            "mcp_status": mcp_status
        }
    
    # Override parent methods to use product-driven approach
    
    async def start_autonomous_operation(self, max_agents: int = 5, budget_limit: float = 10.0, 
                                       overnight_mode: bool = False) -> Dict[str, Any]:
        """Start product-driven autonomous operation."""
        
        # Initialize product strategy first
        await self.initialize_product_strategy()
        
        self.logger.info(f"🎯 Starting product-driven autonomous operation with {len(self.prioritized_features)} prioritized features")
        
        # Call parent with product context
        result = await super().start_autonomous_operation(max_agents, budget_limit, overnight_mode)
        
        # Enhance result with product data
        result["product_context"] = {
            "roadmap_generated": bool(self.feature_roadmap),
            "prioritized_features_count": len(self.prioritized_features),
            "auto_approval_enabled": self.auto_approve_quick_wins,
            "min_rice_score": self.min_rice_score
        }
        
        return result


async def create_product_orchestrator(memory_store: Optional[IntelligentMemoryStore] = None) -> ProductAutonomousOrchestrator:
    """Factory function to create a product-driven autonomous orchestrator."""
    orchestrator = ProductAutonomousOrchestrator(memory_store)
    await orchestrator.initialize_product_strategy()
    return orchestrator
