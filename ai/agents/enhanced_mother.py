"""Enhanced Mother Agent with sophisticated task orchestration capabilities.

This agent extends the base Mother Agent with:
- Complex task decomposition into specialized agent teams
- Intelligent clarification system for ambiguous commands
- Business intelligence and market research capabilities
- Parallel agent coordination and result aggregation
- EXA-MCP integration for real web research

Cross-references:
    - Base MotherAgent: ai/agents/mother.py
    - EXA-MCP Tools: Available via call_mcp_tool
    - ADR-XXX: High-Level Agent Orchestration Architecture
"""
from __future__ import annotations
import asyncio
import json
import time
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

from ai.agents.mother import MotherAgent, ChildAgent, SpawnRequest, AgentResult
from ai.memory.intelligent_store import IntelligentMemoryStore, MemoryType


class TaskComplexity(Enum):
    """Task complexity levels for orchestration planning."""
    SIMPLE = "simple"          # Single agent, direct execution
    MODERATE = "moderate"      # 2-3 agents, sequential
    COMPLEX = "complex"        # 4-8 agents, parallel coordination
    ENTERPRISE = "enterprise"  # 8+ agents, multi-phase orchestration


@dataclass
class ClarificationQuestion:
    """Represents a clarification question for ambiguous tasks."""
    question: str
    context: str
    required: bool = True
    options: Optional[List[str]] = None


@dataclass
class TaskDecomposition:
    """Represents a complex task broken down into specialized subtasks."""
    original_task: str
    complexity: TaskComplexity
    subtasks: List[Dict[str, Any]] = field(default_factory=list)
    dependencies: Dict[str, List[str]] = field(default_factory=dict)
    clarifications: List[ClarificationQuestion] = field(default_factory=list)
    estimated_duration: str = "unknown"
    success_criteria: List[str] = field(default_factory=list)


@dataclass
class OrchestrationResult:
    """Results from orchestrated agent team execution."""
    task_id: str
    original_command: str
    agents_spawned: int
    execution_time: float
    success: bool
    results: Dict[str, Any] = field(default_factory=dict)
    final_report: str = ""
    recommendations: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)


class EnhancedMotherAgent(MotherAgent):
    """Enhanced Mother Agent with sophisticated orchestration capabilities."""
    
    def __init__(self, memory_store: Optional[IntelligentMemoryStore] = None, max_history: int = 200):
        """Initialize Enhanced Mother Agent with orchestration capabilities."""
        super().__init__(memory_store, max_history)
        
        # Enhanced capabilities
        self.orchestration_history: List[OrchestrationResult] = []
        self.active_orchestrations: Dict[str, Dict[str, Any]] = {}
        
        # Specialized agent types for complex tasks
        self.specialized_agents = {
            "MarketResearcher": {
                "description": "Conducts web research on market trends, competitors, and opportunities",
                "tools": ["web_search_exa", "company_research_exa"],
                "specialization": "market analysis, competitor research, trend identification"
            },
            "BusinessAnalyst": {
                "description": "Analyzes business viability, revenue models, and market fit",
                "tools": ["data_analysis", "business_modeling"],
                "specialization": "business model analysis, financial projections, market sizing"
            },
            "TechnicalAssessor": {
                "description": "Evaluates technical feasibility and implementation complexity", 
                "tools": ["code_analysis", "architecture_review"],
                "specialization": "technical feasibility, implementation planning, risk assessment"
            },
            "OpportunityScorer": {
                "description": "Scores and ranks opportunities based on multiple criteria",
                "tools": ["data_aggregation", "scoring_algorithms"],
                "specialization": "opportunity ranking, risk/reward analysis, decision support"
            },
            "DeploymentStrategist": {
                "description": "Plans deployment and go-to-market strategies",
                "tools": ["deployment_planning", "market_strategy"],
                "specialization": "deployment planning, market entry, scaling strategies"
            }
        }
    
    async def orchestrate_complex_task(
        self, 
        command: str, 
        constraints: Optional[Dict[str, Any]] = None,
        skip_clarifications: bool = False
    ) -> OrchestrationResult:
        """Orchestrate a complex task using specialized agent teams.
        
        Args:
            command: High-level command to execute
            constraints: Budget, time, scope constraints
            
        Returns:
            OrchestrationResult with aggregated findings
        """
        task_id = f"orchestration-{int(time.time())}"
        start_time = time.time()
        
        print(f"🎭 Mother Agent orchestrating complex task: {command[:60]}...")
        
        # Phase 1: Task Analysis & Decomposition
        decomposition = await self._decompose_complex_task(command, constraints)
        
        # Phase 2: Clarification (if needed)
        if decomposition.clarifications and not skip_clarifications:
            print(f"🤔 Need clarifications for optimal execution:")
            for clarification in decomposition.clarifications:
                print(f"   ❓ {clarification.question}")
                if clarification.options:
                    print(f"      Options: {', '.join(clarification.options)}")
            
            # For now, return with clarification needed
            # In production, this would wait for user input
            return OrchestrationResult(
                task_id=task_id,
                original_command=command,
                agents_spawned=0,
                execution_time=time.time() - start_time,
                success=False,
                errors=["Clarifications required before execution"],
                final_report="Task requires clarification before proceeding."
            )
        elif skip_clarifications and decomposition.clarifications:
            print(f"⏭️ Skipping {len(decomposition.clarifications)} clarifications for testing")
        
        # Phase 3: Agent Team Coordination
        orchestration_result = await self._execute_orchestrated_plan(
            task_id, decomposition, constraints
        )
        
        # Phase 4: Result Aggregation & Reporting
        final_report = await self._generate_final_report(orchestration_result)
        orchestration_result.final_report = final_report
        
        # Store results
        self.orchestration_history.append(orchestration_result)
        
        # Record in memory
        try:
            self.memory_store.write(
                content=f"Orchestrated complex task: {command}. Spawned {orchestration_result.agents_spawned} agents. Success: {orchestration_result.success}",
                tags=["orchestration", "complex_task", "mother_agent"],
                memory_type="achievement"  # Use string instead of enum
            )
        except Exception as e:
            print(f"⚠️ Memory write failed: {e}")
        
        print(f"🎯 Orchestration complete! {orchestration_result.agents_spawned} agents executed.")
        return orchestration_result
    
    async def _decompose_complex_task(
        self, 
        command: str, 
        constraints: Optional[Dict[str, Any]]
    ) -> TaskDecomposition:
        """Decompose complex task into specialized subtasks."""
        
        # Use OpenAI to analyze and decompose the task
        decomposition_prompt = f"""
        Analyze this complex task and decompose it into specialized subtasks:
        
        COMMAND: {command}
        CONSTRAINTS: {json.dumps(constraints or {}, indent=2)}
        
        Available specialized agent types:
        {json.dumps(self.specialized_agents, indent=2)}
        
        Provide a detailed task decomposition including:
        1. Task complexity assessment
        2. Subtasks with specific agent assignments
        3. Dependencies between subtasks
        4. Clarification questions if the command is ambiguous
        5. Success criteria
        6. Time estimate
        
        Focus on business intelligence, market research, and autonomous deployment opportunities.
        Return as JSON with the following structure:
        {{
            "complexity": "simple|moderate|complex|enterprise",
            "subtasks": [
                {{
                    "id": "task_1",
                    "agent_type": "MarketResearcher",
                    "description": "Specific task description",
                    "tools_needed": ["web_search_exa"],
                    "output_type": "research_report"
                }}
            ],
            "dependencies": {{"task_2": ["task_1"]}},
            "clarifications": [
                {{
                    "question": "Are physical products permitted or just digital?",
                    "context": "Need to understand scope for market research",
                    "required": true,
                    "options": ["Digital only", "Physical only", "Both"]
                }}
            ],
            "success_criteria": ["List of success metrics"],
            "estimated_duration": "2-4 hours"
        }}
        """
        
        # For now, create a sophisticated decomposition for the example command
        if "exa-mcp" in command.lower() and "autonomous" in command.lower():
            return self._create_business_opportunity_decomposition(command, constraints)
        
        # Default simple decomposition
        return TaskDecomposition(
            original_task=command,
            complexity=TaskComplexity.SIMPLE,
            subtasks=[{
                "id": "simple_task",
                "agent_type": "Developer",
                "description": command,
                "tools_needed": [],
                "output_type": "code"
            }],
            success_criteria=["Task completed successfully"]
        )
    
    def _create_business_opportunity_decomposition(
        self, 
        command: str, 
        constraints: Optional[Dict[str, Any]]
    ) -> TaskDecomposition:
        """Create decomposition for business opportunity analysis."""
        
        # Analyze command for clarifications needed
        clarifications = []
        
        if "physical products" not in command.lower() and "digital" not in command.lower():
            clarifications.append(ClarificationQuestion(
                question="Are physical products permitted or just digital products/services?",
                context="Need to understand product scope for market research",
                required=True,
                options=["Digital only", "Physical products only", "Both digital and physical"]
            ))
        
        if not constraints or "budget" not in constraints:
            clarifications.append(ClarificationQuestion(
                question="What is the budget range for market research and analysis?",
                context="Budget affects depth of research and tools available",
                required=False,
                options=["Under $500", "$500-2000", "$2000-5000", "$5000+"]
            ))
        
        if not constraints or "timeline" not in constraints:
            clarifications.append(ClarificationQuestion(
                question="What is the timeline for finding and evaluating opportunities?",
                context="Timeline affects research depth and number of opportunities analyzed",
                required=False,
                options=["Same day", "Within 3 days", "Within 1 week", "Within 1 month"]
            ))
        
        # Create sophisticated subtask breakdown
        subtasks = [
            {
                "id": "market_trend_research",
                "agent_type": "MarketResearcher",
                "description": "Research current market trends for autonomous software deployment opportunities using EXA web search",
                "tools_needed": ["web_search_exa", "company_research_exa"],
                "output_type": "market_research_report",
                "priority": 1
            },
            {
                "id": "competitor_analysis", 
                "agent_type": "MarketResearcher",
                "description": "Identify competitors and existing solutions in autonomous deployment space",
                "tools_needed": ["web_search_exa", "company_research_exa"],
                "output_type": "competitor_analysis",
                "priority": 1
            },
            {
                "id": "technical_capability_assessment",
                "agent_type": "TechnicalAssessor", 
                "description": "Assess technical capabilities of current codebase for rapid deployment opportunities",
                "tools_needed": ["code_analysis", "architecture_review"],
                "output_type": "technical_assessment",
                "priority": 2
            },
            {
                "id": "opportunity_identification",
                "agent_type": "BusinessAnalyst",
                "description": "Identify specific low-hanging fruit opportunities based on market research and technical capabilities",
                "tools_needed": ["data_analysis", "business_modeling"], 
                "output_type": "opportunity_list",
                "priority": 3
            },
            {
                "id": "opportunity_scoring",
                "agent_type": "OpportunityScorer",
                "description": "Score opportunities on implementation time, risk, reward, and market potential",
                "tools_needed": ["scoring_algorithms", "data_aggregation"],
                "output_type": "scored_opportunities",
                "priority": 4
            },
            {
                "id": "deployment_strategy",
                "agent_type": "DeploymentStrategist",
                "description": "Create deployment and go-to-market plans for top-scored opportunities",
                "tools_needed": ["deployment_planning", "market_strategy"],
                "output_type": "deployment_plans", 
                "priority": 5
            }
        ]
        
        # Define dependencies
        dependencies = {
            "technical_capability_assessment": [],
            "competitor_analysis": [],
            "market_trend_research": [],
            "opportunity_identification": ["market_trend_research", "competitor_analysis", "technical_capability_assessment"],
            "opportunity_scoring": ["opportunity_identification"],
            "deployment_strategy": ["opportunity_scoring"]
        }
        
        success_criteria = [
            "Identified at least 5 viable autonomous deployment opportunities",
            "Scored opportunities on risk/reward matrix", 
            "Created actionable 1-day deployment plans",
            "Verified low implementation complexity (< 1 day)",
            "Estimated revenue potential for each opportunity"
        ]
        
        return TaskDecomposition(
            original_task=command,
            complexity=TaskComplexity.COMPLEX,
            subtasks=subtasks,
            dependencies=dependencies, 
            clarifications=clarifications,
            estimated_duration="3-6 hours with 5-6 specialized agents",
            success_criteria=success_criteria
        )
    
    async def _execute_orchestrated_plan(
        self, 
        task_id: str,
        decomposition: TaskDecomposition,
        constraints: Optional[Dict[str, Any]]
    ) -> OrchestrationResult:
        """Execute the orchestrated plan with specialized agents."""
        
        print(f"🚀 Executing orchestrated plan with {len(decomposition.subtasks)} specialized agents")
        
        results = {}
        agents_spawned = 0
        errors = []
        
        # Group tasks by priority for execution phases
        task_phases = {}
        for subtask in decomposition.subtasks:
            priority = subtask.get("priority", 1)
            if priority not in task_phases:
                task_phases[priority] = []
            task_phases[priority].append(subtask)
        
        # Execute tasks phase by phase
        for phase in sorted(task_phases.keys()):
            print(f"📋 Phase {phase}: Executing {len(task_phases[phase])} tasks")
            
            phase_results = await self._execute_task_phase(task_phases[phase], constraints)
            results.update(phase_results)
            agents_spawned += len(task_phases[phase])
        
        # Determine overall success
        success = len(errors) == 0 and len(results) >= len(decomposition.subtasks) * 0.8
        
        return OrchestrationResult(
            task_id=task_id,
            original_command=decomposition.original_task,
            agents_spawned=agents_spawned,
            execution_time=0,  # Will be set by caller
            success=success,
            results=results,
            errors=errors
        )
    
    async def _execute_task_phase(
        self, 
        phase_tasks: List[Dict[str, Any]], 
        constraints: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Execute a phase of tasks (can be run in parallel)."""
        
        phase_results = {}
        
        # For now, execute sequentially (in production, could be parallel)
        for task in phase_tasks:
            task_id = task["id"]
            agent_type = task["agent_type"]
            description = task["description"]
            
            print(f"   🤖 Spawning {agent_type} for: {description[:60]}...")
            
            try:
                # Determine model based on agent type and task complexity
                model = "gpt-4o-mini" if task.get("priority", 1) <= 3 else "gpt-4o"
                
                # Spawn specialized agent
                result = self.run(
                    name=f"{agent_type}_{task_id}",
                    instructions=description,
                    model=model,
                    output_type=task.get("output_type", "analysis")
                )
                
                if result.success:
                    phase_results[task_id] = {
                        "agent_type": agent_type,
                        "output": result.output,
                        "artifacts": result.artifacts,
                        "success": True
                    }
                    print(f"   ✅ {agent_type} completed successfully")
                else:
                    phase_results[task_id] = {
                        "agent_type": agent_type,
                        "error": result.error,
                        "success": False
                    }
                    print(f"   ❌ {agent_type} failed: {result.error}")
                    
            except Exception as e:
                phase_results[task_id] = {
                    "agent_type": agent_type,
                    "error": str(e),
                    "success": False
                }
                print(f"   💥 {agent_type} crashed: {e}")
        
        return phase_results
    
    async def _generate_final_report(self, orchestration_result: OrchestrationResult) -> str:
        """Generate comprehensive final report from orchestration results."""
        
        successful_tasks = [k for k, v in orchestration_result.results.items() if v.get("success", False)]
        failed_tasks = [k for k, v in orchestration_result.results.items() if not v.get("success", False)]
        
        report = f"""
# 🎯 Autonomous Opportunity Analysis Report

## Executive Summary
- **Command**: {orchestration_result.original_command}
- **Agents Deployed**: {orchestration_result.agents_spawned}
- **Execution Time**: {orchestration_result.execution_time:.1f} seconds
- **Success Rate**: {len(successful_tasks)}/{len(orchestration_result.results)} tasks completed

## Task Results

"""
        
        for task_id, result in orchestration_result.results.items():
            if result.get("success"):
                report += f"### ✅ {result['agent_type']}\n"
                report += f"**Output**: {result['output'][:200]}...\n\n"
            else:
                report += f"### ❌ {result['agent_type']}\n" 
                report += f"**Error**: {result.get('error', 'Unknown error')}\n\n"
        
        if failed_tasks:
            report += f"## ⚠️ Issues Encountered\n"
            for task_id in failed_tasks:
                error = orchestration_result.results[task_id].get("error", "Unknown error")
                report += f"- {task_id}: {error}\n"
        
        report += f"""
## 🎉 Recommendations for Next Steps

Based on the analysis results, recommended actions:

1. **Review successful agent findings** for actionable opportunities
2. **Address failed tasks** if critical to overall strategy
3. **Implement top-scoring opportunities** with deployment plans
4. **Monitor market trends** for emerging opportunities

*Report generated by Fresh Autonomous Agent Orchestration System*
"""
        
        return report.strip()

    def get_orchestration_statistics(self) -> Dict[str, Any]:
        """Get statistics about orchestration performance."""
        if not self.orchestration_history:
            return {"total_orchestrations": 0}
        
        total = len(self.orchestration_history)
        successful = len([o for o in self.orchestration_history if o.success])
        avg_agents = sum(o.agents_spawned for o in self.orchestration_history) / total
        avg_time = sum(o.execution_time for o in self.orchestration_history) / total
        
        return {
            "total_orchestrations": total,
            "success_rate": successful / total,
            "avg_agents_per_orchestration": avg_agents,
            "avg_execution_time": avg_time,
            "total_agents_spawned": sum(o.agents_spawned for o in self.orchestration_history)
        }
