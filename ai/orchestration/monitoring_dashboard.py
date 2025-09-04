"""
Simple Monitoring Dashboard for Autonomous Development Orchestration

Provides a real-time terminal-based dashboard to monitor multiple autonomous
development agents working in parallel.
"""
from __future__ import annotations
import asyncio
import json
import time
import os
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path


class MonitoringDashboard:
    """Simple terminal-based monitoring dashboard."""
    
    def __init__(self, orchestrator):
        self.orchestrator = orchestrator
        self.is_running = False
    
    async def start_monitoring(self):
        """Start the monitoring dashboard."""
        self.is_running = True
        
        print("🖥️  Starting Monitoring Dashboard")
        print("   Press Ctrl+C to exit\n")
        
        try:
            while self.is_running:
                self._clear_screen()
                await self._render_dashboard()
                await asyncio.sleep(5)  # Update every 5 seconds
        except KeyboardInterrupt:
            self.is_running = False
            print("\n👋 Dashboard stopped")
    
    def _clear_screen(self):
        """Clear terminal screen."""
        os.system('clear' if os.name == 'posix' else 'cls')
    
    async def _render_dashboard(self):
        """Render the main dashboard."""
        now = datetime.now()
        status = self.orchestrator.get_status()
        
        # Header
        print(f"🤖 AUTONOMOUS DEVELOPMENT ORCHESTRATION DASHBOARD")
        print(f"{'='*70}")
        print(f"Time: {now.strftime('%Y-%m-%d %H:%M:%S')} | Running: {'Yes' if status['is_running'] else 'No'}")
        print(f"Budget: ${status['total_cost_usd']:.2f} / ${status['budget_usd']:.2f} | Agents: {len(status['agents'])}")
        print()
        
        if not status['agents']:
            print("📋 No agents active")
            print("\n💡 Tip: Agents will be spawned automatically as suitable features are found")
            return
        
        # Agents overview
        by_status = {}
        for agent_data in status['agents'].values():
            agent_status = agent_data['status']
            if agent_status not in by_status:
                by_status[agent_status] = []
            by_status[agent_status].append(agent_data)
        
        print("📊 AGENT STATUS OVERVIEW:")
        for status_name, agents in by_status.items():
            emoji = {
                'starting': '🚀',
                'analyzing': '🔍',
                'implementing': '🛠️', 
                'testing': '🧪',
                'awaiting_user': '👤',
                'committing': '📋',
                'completed': '✅',
                'failed': '❌'
            }.get(status_name, '🤖')
            print(f"  {emoji} {status_name.upper()}: {len(agents)}")
        
        print()
        
        # Active agents detail
        active_agents = [a for a in status['agents'].values() 
                        if a['status'] not in ['completed', 'failed']]
        
        if active_agents:
            print("🔄 ACTIVE AGENTS:")
            for agent in active_agents[:10]:  # Show top 10
                self._render_agent_row(agent)
        
        # Completed agents summary
        completed = [a for a in status['agents'].values() if a['status'] == 'completed']
        if completed:
            print(f"\n✅ COMPLETED ({len(completed)}):")
            for agent in completed[-5:]:  # Show last 5
                print(f"  {agent['id'][:8]} | {agent['target_feature']} | {agent['runtime_minutes']:.1f}min | ${agent['cost_usd']:.2f}")
                if agent['pr_url']:
                    print(f"    🔗 {agent['pr_url']}")
        
        # Failed agents
        failed = [a for a in status['agents'].values() if a['status'] == 'failed']
        if failed:
            print(f"\n❌ FAILED ({len(failed)}):")
            for agent in failed[-3:]:  # Show last 3
                print(f"  {agent['id'][:8]} | {agent['target_feature']} | Runtime: {agent['runtime_minutes']:.1f}min")
        
        # User actions needed
        awaiting = [a for a in status['agents'].values() if a['status'] == 'awaiting_user']
        if awaiting:
            print(f"\n👤 AWAITING YOUR APPROVAL ({len(awaiting)}):")
            for agent in awaiting:
                print(f"  Agent {agent['id'][:8]} working on {agent['target_feature']}")
                print(f"  💭 {agent['user_question'][:60]}..." if agent['user_question'] else "  💭 Ready for testing")
                print(f"  ✅ To approve: fresh auto approve {agent['id'][:8]}")
                print()
        
        # Footer
        runtime = (datetime.now() - self.orchestrator.start_time).total_seconds()
        runtime_hours = runtime / 3600
        print(f"\n⏱️  Runtime: {runtime_hours:.1f}h | Refresh: 5s | Ctrl+C to exit")
    
    def _render_agent_row(self, agent: Dict[str, Any]):
        """Render a single agent row."""
        emoji = {
            'starting': '🚀',
            'analyzing': '🔍',
            'implementing': '🛠️',
            'testing': '🧪', 
            'awaiting_user': '👤',
            'committing': '📋'
        }.get(agent['status'], '🤖')
        
        feature_name = (agent['target_feature'] or 'N/A')[:20]
        status_name = agent['status'][:12]
        runtime = f"{agent['runtime_minutes']:.1f}m"
        cost = f"${agent['cost_usd']:.2f}"
        
        print(f"  {emoji} {agent['id'][:8]} | {feature_name:<20} | {status_name:<12} | {runtime:>6} | {cost:>5}")
        
        # Show last progress if available
        if agent.get('last_progress'):
            progress_text = agent['last_progress'].split(': ', 1)[-1][:50]
            print(f"    💭 {progress_text}...")


def create_monitoring_dashboard(orchestrator) -> MonitoringDashboard:
    """Create a monitoring dashboard for the orchestrator."""
    return MonitoringDashboard(orchestrator)


async def main():
    """Test the monitoring dashboard."""
    # This would typically be called with a real orchestrator
    print("⚠️  Monitoring dashboard test mode")
    print("   This would normally connect to a running orchestrator")
    
    class MockOrchestrator:
        def __init__(self):
            self.start_time = datetime.now()
        
        def get_status(self):
            return {
                'is_running': True,
                'total_cost_usd': 2.50,
                'budget_usd': 10.0,
                'agents': {
                    'abc123': {
                        'id': 'abc123',
                        'status': 'implementing',
                        'target_feature': 'build_enhanced_agency',
                        'runtime_minutes': 15.5,
                        'cost_usd': 0.75,
                        'user_question': None,
                        'pr_url': None,
                        'last_progress': '2025-01-04T21:30:00: Adding CLI commands'
                    },
                    'def456': {
                        'id': 'def456', 
                        'status': 'awaiting_user',
                        'target_feature': 'demo_enhanced_agency',
                        'runtime_minutes': 8.2,
                        'cost_usd': 0.25,
                        'user_question': 'Agent completed work, please test branch',
                        'pr_url': None,
                        'last_progress': '2025-01-04T21:25:00: Tests passing, ready for review'
                    }
                }
            }
    
    mock_orchestrator = MockOrchestrator()
    dashboard = create_monitoring_dashboard(mock_orchestrator)
    
    await dashboard.start_monitoring()


if __name__ == '__main__':
    asyncio.run(main())
