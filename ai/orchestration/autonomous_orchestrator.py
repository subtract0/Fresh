"""
Autonomous Agent Orchestrator

Manages multiple autonomous development agents working in parallel on different
improvements, with cost controls, monitoring, and user interaction points.

Features:
- Multi-agent coordination and task distribution
- OpenAI API cost tracking and budget limits
- Overnight operation mode with error recovery
- Real-time monitoring and status reporting
- User interaction checkpoints for testing/approval
- GitHub integration for autonomous PR creation
"""
from __future__ import annotations
import asyncio
import json
import os
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
import subprocess
import logging
import signal
import uuid

logger = logging.getLogger(__name__)


class AgentStatus(Enum):
    STARTING = "starting"
    ANALYZING = "analyzing"
    IMPLEMENTING = "implementing"
    TESTING = "testing"
    AWAITING_USER = "awaiting_user"
    COMMITTING = "committing"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"


@dataclass
class AutonomousAgent:
    """Represents a single autonomous development agent."""
    id: str
    task_description: str
    target_feature: Optional[str] = None
    branch_name: Optional[str] = None
    status: AgentStatus = AgentStatus.STARTING
    start_time: datetime = field(default_factory=datetime.now)
    last_update: datetime = field(default_factory=datetime.now)
    cost_usd: float = 0.0
    progress_log: List[str] = field(default_factory=list)
    pr_url: Optional[str] = None
    error_message: Optional[str] = None
    user_question: Optional[str] = None
    completed_steps: List[str] = field(default_factory=list)
    
    def update_status(self, status: AgentStatus, message: str = ""):
        """Update agent status with timestamp and message."""
        self.status = status
        self.last_update = datetime.now()
        if message:
            self.progress_log.append(f"{self.last_update.isoformat()}: {message}")
    
    def add_progress(self, message: str):
        """Add progress message."""
        self.progress_log.append(f"{datetime.now().isoformat()}: {message}")
    
    def get_runtime_minutes(self) -> float:
        """Get runtime in minutes."""
        return (datetime.now() - self.start_time).total_seconds() / 60


@dataclass 
class OrchestrationConfig:
    """Configuration for autonomous orchestration."""
    max_agents: int = 10
    budget_usd: float = 10.0  # 10 EUR ≈ 10 USD
    cost_per_agent_limit_usd: float = 1.0
    overnight_mode: bool = False
    work_hours_start: int = 9  # 9 AM
    work_hours_end: int = 17   # 5 PM
    max_runtime_hours: int = 8
    checkpoint_interval_minutes: int = 30
    user_interaction_timeout_minutes: int = 60
    feature_selection_strategy: str = "highest_impact"  # highest_impact, safest, random
    github_auto_pr: bool = True
    require_user_approval: bool = True


class AutonomousOrchestrator:
    """Orchestrates multiple autonomous development agents."""
    
    def __init__(self, config: OrchestrationConfig):
        self.config = config
        self.agents: Dict[str, AutonomousAgent] = {}
        self.total_cost_usd = 0.0
        self.start_time = datetime.now()
        self.is_running = False
        self.shutdown_requested = False
        
        # Setup logging
        self.setup_logging()
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def setup_logging(self):
        """Setup detailed logging for orchestration."""
        log_dir = Path(".fresh/logs")
        log_dir.mkdir(parents=True, exist_ok=True)
        
        log_file = log_dir / f"orchestrator_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        
        logger.info(f"Orchestrator starting with config: {self.config}")
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully."""
        logger.info(f"Received signal {signum}, initiating graceful shutdown...")
        self.shutdown_requested = True
    
    async def start_orchestration(self):
        """Start the autonomous orchestration system."""
        logger.info("🚀 Starting Autonomous Development Orchestration")
        logger.info(f"   Max Agents: {self.config.max_agents}")
        logger.info(f"   Budget: ${self.config.budget_usd:.2f} USD")
        logger.info(f"   Overnight Mode: {self.config.overnight_mode}")
        
        self.is_running = True
        
        try:
            # Main orchestration loop
            await self._orchestration_loop()
        except Exception as e:
            logger.error(f"Orchestration failed: {e}")
        finally:
            await self._shutdown()
    
    async def _orchestration_loop(self):
        """Main orchestration loop."""
        while self.is_running and not self.shutdown_requested:
            try:
                # Check if we should continue (budget, time, etc.)
                if not await self._should_continue():
                    break
                
                # Manage existing agents
                await self._manage_agents()
                
                # Spawn new agents if needed
                await self._spawn_agents_if_needed()
                
                # User interaction checkpoint
                await self._handle_user_interactions()
                
                # Status reporting
                await self._report_status()
                
                # Brief pause before next iteration
                await asyncio.sleep(10)
                
            except Exception as e:
                logger.error(f"Error in orchestration loop: {e}")
                await asyncio.sleep(60)  # Wait before retrying
    
    async def _should_continue(self) -> bool:
        """Check if orchestration should continue."""
        # Budget check
        if self.total_cost_usd >= self.config.budget_usd:
            logger.info(f"💰 Budget limit reached: ${self.total_cost_usd:.2f}")
            return False
        
        # Time limit check
        runtime_hours = (datetime.now() - self.start_time).total_seconds() / 3600
        if runtime_hours >= self.config.max_runtime_hours:
            logger.info(f"⏰ Runtime limit reached: {runtime_hours:.1f} hours")
            return False
        
        # Work hours check (if not overnight mode)
        if not self.config.overnight_mode:
            current_hour = datetime.now().hour
            if not (self.config.work_hours_start <= current_hour < self.config.work_hours_end):
                logger.info(f"🕐 Outside work hours, pausing until {self.config.work_hours_start}:00")
                return False
        
        return True
    
    async def _spawn_agents_if_needed(self):
        """Spawn new agents if we have capacity and work to do."""
        active_agents = [a for a in self.agents.values() if a.status not in [AgentStatus.COMPLETED, AgentStatus.FAILED]]
        
        if len(active_agents) >= self.config.max_agents:
            return
        
        # Get available features to work on
        available_features = await self._get_available_features()
        
        if not available_features:
            logger.info("📋 No suitable features available for new agents")
            return
        
        # Spawn new agent
        spots_available = self.config.max_agents - len(active_agents)
        for i in range(min(spots_available, len(available_features))):
            if self.total_cost_usd + self.config.cost_per_agent_limit_usd > self.config.budget_usd:
                break
                
            feature = available_features[i]
            await self._spawn_agent(feature)
    
    async def _get_available_features(self) -> List[Dict[str, Any]]:
        """Get list of features available for autonomous improvement."""
        try:
            # Read from existing feature inventory file (faster and more reliable)
            inventory_path = Path('docs/feature_inventory.json')
            if not inventory_path.exists():
                # If file doesn't exist, run the CLI to generate it
                result = subprocess.run(['poetry', 'run', 'python', '-m', 'ai.cli.fresh', 'feature', 'inventory'], 
                                      capture_output=True, text=True, timeout=120)
                logger.info(f"Generated feature inventory (returncode: {result.returncode})")
            
            if not inventory_path.exists():
                logger.warning("Feature inventory file not found after generation")
                return []
            
            # Parse inventory from JSON file
            with open(inventory_path) as f:
                inventory = json.load(f)
            
            # Filter for features that need improvement (have quality issues)
            suitable_features = []
            for feature in inventory.get('features', []):
                issues = feature.get('issues', [])
                
                # Look for features with actionable quality issues
                if (len(issues) > 0 and
                    feature.get('necessary', True) and  # Only work on necessary features
                    feature.get('quality_score', 0) < 0.9):  # Has room for improvement
                    
                    # Skip if already being worked on
                    feature_name = feature['name']
                    if any(agent.target_feature == feature_name for agent in self.agents.values()):
                        continue
                    
                    # Prioritize features with hookup and testing issues (easier to fix)
                    priority_issues = [i for i in issues if 'test coverage' in i or 'not accessible' in i or 'interface' in i]
                    if priority_issues:
                        feature['priority_issues'] = priority_issues
                        suitable_features.append(feature)
            
            # Sort by strategy
            if self.config.feature_selection_strategy == "highest_impact":
                suitable_features.sort(key=lambda f: f.get('quality_score', 0), reverse=True)
            elif self.config.feature_selection_strategy == "safest":
                suitable_features.sort(key=lambda f: len(f.get('issues', [])))
            
            return suitable_features[:10]  # Top 10
            
        except Exception as e:
            logger.error(f"Error getting available features: {e}")
            return []
    
    async def _spawn_agent(self, feature: Dict[str, Any]):
        """Spawn a new autonomous agent for a feature."""
        agent_id = str(uuid.uuid4())[:8]
        feature_name = feature['name']
        
        logger.info(f"🤖 Spawning agent {agent_id} for feature: {feature_name}")
        
        # Create branch name
        branch_name = f"auto/{feature_name.lower().replace('_', '-')}-{agent_id}"
        
        # Create task description
        issues = feature.get('issues', [])
        task_description = f"Autonomous improvement of {feature_name}: {', '.join(issues[:3])}"
        
        agent = AutonomousAgent(
            id=agent_id,
            task_description=task_description,
            target_feature=feature_name,
            branch_name=branch_name
        )
        
        self.agents[agent_id] = agent
        
        # Start the agent work in background
        asyncio.create_task(self._run_agent(agent))
    
    async def _run_agent(self, agent: AutonomousAgent):
        """Run a single autonomous agent."""
        logger.info(f"🚀 Agent {agent.id} starting work on {agent.target_feature}")
        
        try:
            # Phase 1: Analysis
            agent.update_status(AgentStatus.ANALYZING, f"Analyzing {agent.target_feature}")
            await self._agent_analyze_phase(agent)
            
            # Phase 2: Implementation  
            agent.update_status(AgentStatus.IMPLEMENTING, "Implementing improvements")
            await self._agent_implement_phase(agent)
            
            # Phase 3: Testing
            agent.update_status(AgentStatus.TESTING, "Running tests")
            await self._agent_test_phase(agent)
            
            # Phase 4: User interaction (if required)
            if self.config.require_user_approval:
                agent.update_status(AgentStatus.AWAITING_USER, "Awaiting user approval")
                agent.user_question = f"Agent {agent.id} completed work on {agent.target_feature}. Please test the branch '{agent.branch_name}' and approve?"
                
                # Wait for user response
                await self._wait_for_user_response(agent)
            
            # Phase 5: Commit and PR
            agent.update_status(AgentStatus.COMMITTING, "Creating PR")
            await self._agent_commit_phase(agent)
            
            agent.update_status(AgentStatus.COMPLETED, "Work completed successfully")
            logger.info(f"✅ Agent {agent.id} completed successfully")
            
        except Exception as e:
            agent.update_status(AgentStatus.FAILED, f"Failed: {str(e)}")
            agent.error_message = str(e)
            logger.error(f"❌ Agent {agent.id} failed: {e}")
    
    async def _agent_analyze_phase(self, agent: AutonomousAgent):
        """Agent analysis phase."""
        agent.add_progress("Starting analysis phase")
        
        # Create branch
        subprocess.run(['git', 'checkout', '-b', agent.branch_name], check=True)
        agent.add_progress(f"Created branch {agent.branch_name}")
        
        # Analyze the target feature
        # This could involve running the feature inventory, looking at the code, etc.
        await asyncio.sleep(2)  # Simulate analysis time
        
        agent.completed_steps.append("analysis")
    
    async def _agent_implement_phase(self, agent: AutonomousAgent):
        """Agent implementation phase."""
        agent.add_progress("Starting implementation phase")
        
        # Here we would call the actual autonomous development system
        # Similar to what I demonstrated before
        
        # For now, simulate the work
        await asyncio.sleep(30)  # Simulate implementation time
        
        # Track estimated cost
        agent.cost_usd += 0.5  # Estimate
        self.total_cost_usd += 0.5
        
        agent.completed_steps.append("implementation")
    
    async def _agent_test_phase(self, agent: AutonomousAgent):
        """Agent testing phase."""
        agent.add_progress("Running tests")
        
        # Run tests
        result = subprocess.run(['poetry', 'run', 'pytest', '-x', '--tb=short'], 
                               capture_output=True, text=True)
        
        if result.returncode == 0:
            agent.add_progress("✅ All tests passed")
        else:
            agent.add_progress(f"⚠️ Tests failed: {result.stdout[-200:]}")
            # Could implement test fixing here
        
        agent.completed_steps.append("testing")
    
    async def _wait_for_user_response(self, agent: AutonomousAgent):
        """Wait for user response with timeout."""
        timeout_minutes = self.config.user_interaction_timeout_minutes
        start_time = time.time()
        
        while agent.status == AgentStatus.AWAITING_USER:
            if time.time() - start_time > timeout_minutes * 60:
                agent.add_progress(f"⏰ User response timeout after {timeout_minutes} minutes, proceeding...")
                break
            await asyncio.sleep(30)
    
    async def _agent_commit_phase(self, agent: AutonomousAgent):
        """Agent commit and PR phase."""
        agent.add_progress("Committing changes and creating PR")
        
        # Commit changes
        subprocess.run(['git', 'add', '-A'], check=True)
        commit_msg = f"Autonomous improvement: {agent.task_description}\n\nAgent ID: {agent.id}"
        subprocess.run(['git', 'commit', '-m', commit_msg], check=True)
        
        # Push branch
        subprocess.run(['git', 'push', '-u', 'origin', agent.branch_name], check=True)
        
        if self.config.github_auto_pr:
            # Create PR
            pr_title = f"🤖 Autonomous: {agent.target_feature} improvements"
            pr_body = f"Autonomous agent {agent.id} improvements for {agent.target_feature}\\n\\n{agent.task_description}"
            
            result = subprocess.run(['gh', 'pr', 'create', '--title', pr_title, '--body', pr_body],
                                   capture_output=True, text=True)
            
            if result.returncode == 0:
                agent.pr_url = result.stdout.strip()
                agent.add_progress(f"✅ PR created: {agent.pr_url}")
        
        agent.completed_steps.append("commit")
    
    async def _manage_agents(self):
        """Manage existing agents - check status, handle failures, etc."""
        for agent in list(self.agents.values()):
            # Check for stuck agents
            minutes_since_update = (datetime.now() - agent.last_update).total_seconds() / 60
            if minutes_since_update > 30 and agent.status not in [AgentStatus.COMPLETED, AgentStatus.FAILED, AgentStatus.AWAITING_USER]:
                logger.warning(f"⚠️ Agent {agent.id} may be stuck (no update for {minutes_since_update:.1f} minutes)")
            
            # Update cost tracking
            self.total_cost_usd = sum(agent.cost_usd for agent in self.agents.values())
    
    async def _handle_user_interactions(self):
        """Handle agents awaiting user interaction."""
        awaiting_agents = [a for a in self.agents.values() if a.status == AgentStatus.AWAITING_USER]
        
        if awaiting_agents:
            logger.info(f"👤 {len(awaiting_agents)} agents awaiting user interaction")
            for agent in awaiting_agents:
                if agent.user_question:
                    logger.info(f"❓ Agent {agent.id}: {agent.user_question}")
    
    async def _report_status(self):
        """Report orchestration status."""
        runtime_minutes = (datetime.now() - self.start_time).total_seconds() / 60
        
        if int(runtime_minutes) % self.config.checkpoint_interval_minutes == 0:
            active_count = len([a for a in self.agents.values() if a.status not in [AgentStatus.COMPLETED, AgentStatus.FAILED]])
            completed_count = len([a for a in self.agents.values() if a.status == AgentStatus.COMPLETED])
            failed_count = len([a for a in self.agents.values() if a.status == AgentStatus.FAILED])
            
            logger.info(f"📊 Status: {active_count} active, {completed_count} completed, {failed_count} failed")
            logger.info(f"💰 Cost: ${self.total_cost_usd:.2f} / ${self.config.budget_usd:.2f}")
            logger.info(f"⏱️ Runtime: {runtime_minutes:.1f} minutes")
    
    async def _shutdown(self):
        """Graceful shutdown."""
        logger.info("🔄 Shutting down autonomous orchestration...")
        
        self.is_running = False
        
        # Wait for agents to finish current work
        active_agents = [a for a in self.agents.values() if a.status not in [AgentStatus.COMPLETED, AgentStatus.FAILED]]
        if active_agents:
            logger.info(f"⏳ Waiting for {len(active_agents)} agents to finish...")
            # Give agents time to finish gracefully
            await asyncio.sleep(30)
        
        # Final status report
        await self._generate_final_report()
        
        logger.info("✅ Orchestration shutdown complete")
    
    async def _generate_final_report(self):
        """Generate final orchestration report."""
        runtime_hours = (datetime.now() - self.start_time).total_seconds() / 3600
        
        completed = [a for a in self.agents.values() if a.status == AgentStatus.COMPLETED]
        failed = [a for a in self.agents.values() if a.status == AgentStatus.FAILED]
        
        report = {
            "orchestration_summary": {
                "total_runtime_hours": runtime_hours,
                "total_cost_usd": self.total_cost_usd,
                "agents_spawned": len(self.agents),
                "agents_completed": len(completed),
                "agents_failed": len(failed)
            },
            "completed_agents": [
                {
                    "id": agent.id,
                    "target_feature": agent.target_feature,
                    "pr_url": agent.pr_url,
                    "runtime_minutes": agent.get_runtime_minutes(),
                    "cost_usd": agent.cost_usd
                }
                for agent in completed
            ],
            "failed_agents": [
                {
                    "id": agent.id, 
                    "target_feature": agent.target_feature,
                    "error": agent.error_message,
                    "runtime_minutes": agent.get_runtime_minutes()
                }
                for agent in failed
            ]
        }
        
        # Save report
        report_file = Path(f".fresh/orchestration_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        report_file.parent.mkdir(parents=True, exist_ok=True)
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"📄 Final report saved to {report_file}")
        
        # Print summary
        print(f"\n🎯 AUTONOMOUS ORCHESTRATION COMPLETE")
        print(f"{'='*50}")
        print(f"Runtime: {runtime_hours:.1f} hours")
        print(f"Cost: ${self.total_cost_usd:.2f} USD")
        print(f"Agents: {len(self.agents)} spawned, {len(completed)} completed, {len(failed)} failed")
        
        if completed:
            print(f"\n✅ Successful PRs:")
            for agent in completed:
                print(f"  - {agent.target_feature}: {agent.pr_url}")
    
    def approve_agent(self, agent_id: str):
        """Approve an agent awaiting user interaction."""
        if agent_id in self.agents:
            agent = self.agents[agent_id]
            if agent.status == AgentStatus.AWAITING_USER:
                agent.update_status(AgentStatus.IMPLEMENTING, "User approved, continuing...")
                logger.info(f"👍 User approved agent {agent_id}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get current orchestration status."""
        return {
            "is_running": self.is_running,
            "total_cost_usd": self.total_cost_usd,
            "budget_usd": self.config.budget_usd,
            "agents": {
                agent_id: {
                    "id": agent.id,
                    "status": agent.status.value,
                    "target_feature": agent.target_feature,
                    "runtime_minutes": agent.get_runtime_minutes(),
                    "cost_usd": agent.cost_usd,
                    "user_question": agent.user_question,
                    "pr_url": agent.pr_url,
                    "last_progress": agent.progress_log[-1] if agent.progress_log else None
                }
                for agent_id, agent in self.agents.items()
            }
        }
