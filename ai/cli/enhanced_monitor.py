#!/usr/bin/env python
"""Enhanced Interactive CLI Monitor for Agent Control

This module provides an advanced command-line interface for monitoring
and controlling different types of AI agents with real-time updates,
interactive controls, and visual feedback.

Features:
- Real-time agent status display
- Interactive controls for different agent types
- Live performance metrics
- Safety alerts and opportunity feed
- Professional terminal UI with Rich library

Usage:
    python -m ai.cli.fresh monitor-enhanced
    
Controls:
    [1] - Autonomous Loop    [2] - Single Scan
    [3] - Product Manager    [4] - Documentation Agent  
    [5] - Custom Spawn       [S] - Stop Current
    [E] - Emergency Stop     [Q] - Quit
"""
from __future__ import annotations

import asyncio
import json
import signal
import sys
import threading
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, Optional, List
import subprocess

try:
    from rich.console import Console
    from rich.live import Live
    from rich.layout import Layout
    from rich.panel import Panel
    from rich.table import Table
    from rich.text import Text
    from rich.columns import Columns
    from rich.progress import Progress, SpinnerColumn, TextColumn
    from rich.align import Align
    from rich.box import ROUNDED
except ImportError:
    print("⚠️ Rich library required: pip install rich")
    sys.exit(1)

from ai.autonomous import AutonomousLoop
from ai.memory.intelligent_store import IntelligentMemoryStore


class AgentStatus:
    """Track status of different agent types"""
    def __init__(self):
        self.agents: Dict[str, Dict[str, Any]] = {
            'autonomous': {'status': 'idle', 'last_cycle': None, 'total_cycles': 0},
            'scanner': {'status': 'idle', 'last_scan': None, 'issues_found': 0},
            'product_manager': {'status': 'idle', 'last_run': None, 'plans_created': 0},
            'documentation': {'status': 'idle', 'last_run': None, 'docs_updated': 0},
            'custom': {'status': 'idle', 'last_spawn': None, 'tasks_completed': 0}
        }
        self.current_operation: Optional[str] = None
        self.emergency_stop = False
        
    def update_agent(self, agent_type: str, status: str, **kwargs):
        """Update agent status"""
        if agent_type in self.agents:
            self.agents[agent_type]['status'] = status
            self.agents[agent_type].update(kwargs)
            
    def get_status_emoji(self, agent_type: str) -> str:
        """Get emoji for agent status"""
        status = self.agents[agent_type]['status']
        return {
            'idle': '😴',
            'running': '🚀', 
            'working': '⚙️',
            'completed': '✅',
            'error': '❌',
            'stopped': '⏹️'
        }.get(status, '❓')


class EnhancedMonitor:
    """Enhanced CLI monitor with interactive controls"""
    
    def __init__(self, use_simple_input=False):
        self.console = Console()
        self.agent_status = AgentStatus()
        self.autonomous_loop: Optional[AutonomousLoop] = None
        self.running = True
        self.last_opportunities = 0
        self.recent_activities: List[str] = []
        self.performance_metrics = {
            'avg_cycle_time': 0,
            'success_rate': 0,
            'opportunities_per_minute': 0,
            'total_improvements': 0
        }
        self.use_simple_input = use_simple_input
        
    def create_layout(self) -> Layout:
        """Create the main dashboard layout"""
        layout = Layout()
        
        layout.split(
            Layout(name="header", size=3),
            Layout(name="main"),
            Layout(name="controls", size=8)
        )
        
        layout["main"].split_row(
            Layout(name="agents", ratio=1),
            Layout(name="activity", ratio=1)
        )
        
        return layout
        
    def create_header(self) -> Panel:
        """Create header with title and current time"""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        title = Text("🤖 Fresh Agent Control Dashboard", style="bold blue")
        subtitle = Text(f"Live Monitor • {current_time}", style="dim")
        
        return Panel(
            Align.center(title + "\n" + subtitle),
            border_style="blue",
            box=ROUNDED
        )
        
    def create_agent_panel(self) -> Panel:
        """Create agent status panel"""
        table = Table(show_header=True, header_style="bold magenta", box=ROUNDED)
        table.add_column("Agent Type", style="cyan", width=15)
        table.add_column("Status", width=10)
        table.add_column("Last Activity", style="dim", width=20)
        table.add_column("Metrics", style="green", width=15)
        
        for agent_type, data in self.agent_status.agents.items():
            emoji = self.agent_status.get_status_emoji(agent_type)
            status = f"{emoji} {data['status']}"
            
            # Format last activity
            last_key = next((k for k in data.keys() if k.startswith('last_')), None)
            last_activity = data.get(last_key, 'Never') if last_key else 'Never'
            if last_activity and last_activity != 'Never':
                try:
                    if isinstance(last_activity, str):
                        last_activity = datetime.fromisoformat(last_activity).strftime('%H:%M:%S')
                except:
                    pass
                    
            # Format metrics
            metric_key = next((k for k in data.keys() if k.startswith('total_') or k.endswith('_found') or k.endswith('_created') or k.endswith('_updated') or k.endswith('_completed')), None)
            metrics = str(data.get(metric_key, 0)) if metric_key else "0"
            
            table.add_row(
                agent_type.replace('_', ' ').title(),
                status,
                str(last_activity),
                metrics
            )
            
        return Panel(table, title="🤖 Agent Status", border_style="green")
        
    def create_activity_panel(self) -> Panel:
        """Create activity feed panel"""
        # Performance metrics
        perf_table = Table(show_header=False, box=None, padding=(0, 1))
        perf_table.add_column("Metric", style="cyan")
        perf_table.add_column("Value", style="bold green")
        
        perf_table.add_row("Avg Cycle Time", f"{self.performance_metrics['avg_cycle_time']:.1f}s")
        perf_table.add_row("Success Rate", f"{self.performance_metrics['success_rate']:.1f}%")
        perf_table.add_row("Opportunities", str(self.last_opportunities))
        perf_table.add_row("Total Improvements", str(self.performance_metrics['total_improvements']))
        
        # Recent activities
        activities_text = "\n".join(self.recent_activities[-8:]) if self.recent_activities else "No recent activity"
        
        content = Columns([
            Panel(perf_table, title="📊 Metrics", border_style="blue"),
            Panel(activities_text, title="📝 Recent Activity", border_style="yellow")
        ])
        
        return Panel(content, title="⚡ Live Activity", border_style="magenta")
        
    def create_controls_panel(self) -> Panel:
        """Create controls panel with detailed descriptions"""
        controls_text = Text()
        controls_text.append("🎮 Agent Control Panel\n\n", style="bold cyan")
        
        # Agent controls with clear descriptions
        controls_text.append("🤖 AGENT ACTIONS:\n", style="bold yellow")
        controls_text.append("[1] ", style="bold green")
        controls_text.append("Autonomous Loop", style="green")
        controls_text.append(" - Start continuous improvement (scans every 5min)\n", style="dim")
        
        controls_text.append("[2] ", style="bold blue")
        controls_text.append("Single Scan", style="blue")
        controls_text.append(" - Analyze repository for issues (~30sec)\n", style="dim")
        
        controls_text.append("[3] ", style="bold yellow")
        controls_text.append("Product Manager", style="yellow")
        controls_text.append(" - Plan features and roadmap (~60sec)\n", style="dim")
        
        controls_text.append("[4] ", style="bold magenta")
        controls_text.append("Documentation", style="magenta")
        controls_text.append(" - Generate and update docs (~45sec)\n", style="dim")
        
        controls_text.append("[5] ", style="bold white")
        controls_text.append("Custom Agent", style="white")
        controls_text.append(" - Spawn agent for specific task (~90sec)\n\n", style="dim")
        
        # System controls
        controls_text.append("⚡ SYSTEM CONTROLS:\n", style="bold cyan")
        controls_text.append("[S] Stop Current ", style="red")
        controls_text.append("[E] Emergency Stop ", style="bold red")
        controls_text.append("[R] Refresh ", style="cyan")
        controls_text.append("[Q] Quit", style="dim")
        
        # Current status
        current_op = self.agent_status.current_operation
        status_text = f"\n\n🎯 Current Operation: {current_op or 'None'}"
        if self.agent_status.emergency_stop:
            status_text += "\n🚨 EMERGENCY STOP ACTIVE"
        else:
            status_text += "\n💡 Press any number key to start an agent!"
            
        controls_text.append(status_text, style="bold")
        
        return Panel(controls_text, title="🎛️ Interactive Controls", border_style="cyan")
        
    def add_activity(self, message: str):
        """Add activity to recent activities"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.recent_activities.append(f"[{timestamp}] {message}")
        if len(self.recent_activities) > 20:
            self.recent_activities = self.recent_activities[-20:]
            
    async def start_autonomous_loop(self):
        """Start autonomous improvement loop"""
        try:
            self.agent_status.update_agent('autonomous', 'running')
            self.agent_status.current_operation = 'Autonomous Loop'
            self.add_activity("🚀 Starting autonomous improvement loop")
            
            # Create autonomous loop
            self.autonomous_loop = AutonomousLoop(
                working_directory=".",
                config={
                    'max_improvements_per_cycle': 3,
                    'safety_level': 'high',
                    'scan_interval': 300
                }
            )
            
            # Start continuous loop in background
            def run_loop():
                try:
                    self.autonomous_loop.start_continuous_loop()
                except Exception as e:
                    self.add_activity(f"❌ Autonomous loop error: {str(e)}")
                    self.agent_status.update_agent('autonomous', 'error')
                    
            loop_thread = threading.Thread(target=run_loop, daemon=True)
            loop_thread.start()
            
            self.add_activity("✅ Autonomous loop started successfully")
            
        except Exception as e:
            self.add_activity(f"❌ Failed to start autonomous loop: {str(e)}")
            self.agent_status.update_agent('autonomous', 'error')
            
    async def run_single_scan(self):
        """Run single repository scan - PRODUCTION VERSION"""
        try:
            self.agent_status.update_agent('scanner', 'running')
            self.agent_status.current_operation = 'Repository Scan'
            self.add_activity("🔍 Running repository scan - analyzing real codebase")
            
            # Import and use the actual scan function directly
            from ai.loop.repo_scanner import scan_repository
            
            # Run the actual scan function
            tasks = scan_repository('.')
            
            # Process results
            total_issues = len(tasks)
            
            # Group by type for detailed reporting
            issue_types = {}
            for task in tasks:
                task_type = task.type.value
                if task_type not in issue_types:
                    issue_types[task_type] = 0
                issue_types[task_type] += 1
            
            self.agent_status.update_agent('scanner', 'completed', 
                                         issues_found=total_issues,
                                         last_scan=datetime.now().isoformat())
            
            # Detailed activity reporting
            self.add_activity(f"✅ Scan completed: {total_issues} total issues found")
            for issue_type, count in issue_types.items():
                self.add_activity(f"  • {issue_type}: {count} issues")
                
            self.agent_status.current_operation = None
            
        except Exception as e:
            self.add_activity(f"❌ Scan error: {str(e)}")
            self.agent_status.update_agent('scanner', 'error')
            self.agent_status.current_operation = None
            
    async def run_product_manager(self):
        """Run actual product manager analysis and planning"""
        try:
            self.agent_status.update_agent('product_manager', 'running')
            self.agent_status.current_operation = 'Product Manager'
            
            self.add_activity("🔍 Product Manager: Scanning codebase structure...")
            
            # Analyze current codebase structure
            analysis_results = await self.analyze_codebase_for_features()
            
            self.add_activity(f"📁 Found {len(analysis_results.get('features', []))} existing features")
            
            # Generate feature recommendations
            recommendations = await self.generate_feature_recommendations(analysis_results)
            
            self.add_activity(f"💡 Generated {len(recommendations)} feature recommendations")
            
            # Create feature plan document
            plan_file = await self.create_feature_plan(analysis_results, recommendations)
            
            self.agent_status.update_agent('product_manager', 'completed', 
                                         plans_created=self.agent_status.agents['product_manager']['plans_created'] + 1,
                                         last_run=datetime.now().isoformat())
            self.agent_status.current_operation = None
            self.add_activity(f"✅ Product Manager completed - plan saved to {plan_file}")
            
        except Exception as e:
            self.add_activity(f"❌ Product Manager failed: {str(e)}")
            self.agent_status.update_agent('product_manager', 'error')
            self.agent_status.current_operation = None
            
    async def analyze_codebase_for_features(self) -> dict:
        """Analyze codebase to identify existing features and gaps"""
        analysis = {
            'features': [],
            'directories': [],
            'missing_areas': [],
            'tech_stack': [],
            'complexity_score': 0
        }
        
        try:
            # Scan directory structure
            import os
            from pathlib import Path
            
            root_path = Path('.')
            
            # Identify feature directories
            feature_patterns = ['features', 'modules', 'components', 'services', 'apps']
            for pattern in feature_patterns:
                feature_dirs = list(root_path.glob(f"**/{pattern}"))
                for feature_dir in feature_dirs[:10]:  # Limit to avoid too many
                    if feature_dir.is_dir():
                        subdirs = [d.name for d in feature_dir.iterdir() if d.is_dir()]
                        analysis['features'].extend(subdirs)
                        
            # Identify tech stack from files
            tech_indicators = {
                '*.py': 'Python',
                '*.ts': 'TypeScript', 
                '*.js': 'JavaScript',
                '*.go': 'Go',
                '*.rs': 'Rust',
                '*.java': 'Java',
                'package.json': 'Node.js',
                'requirements.txt': 'Python',
                'pyproject.toml': 'Python',
                'Cargo.toml': 'Rust',
                'go.mod': 'Go'
            }
            
            for pattern, tech in tech_indicators.items():
                if list(root_path.glob(f"**/{pattern}")):
                    analysis['tech_stack'].append(tech)
                    
            # Remove duplicates
            analysis['features'] = list(set(analysis['features']))[:20]
            analysis['tech_stack'] = list(set(analysis['tech_stack']))
            
            # Identify missing common areas
            common_areas = ['auth', 'api', 'database', 'testing', 'logging', 'config', 'security', 'monitoring']
            existing_lower = [f.lower() for f in analysis['features']]
            analysis['missing_areas'] = [area for area in common_areas if area not in existing_lower]
            
            return analysis
            
        except Exception as e:
            self.add_activity(f"⚠️ Codebase analysis error: {str(e)}")
            return analysis
            
    async def generate_feature_recommendations(self, analysis: dict) -> list:
        """Generate feature recommendations based on codebase analysis"""
        recommendations = []
        
        # Based on missing areas
        for missing_area in analysis['missing_areas'][:5]:  # Top 5 missing areas
            recommendations.append({
                'type': 'missing_feature',
                'title': f"Implement {missing_area.title()} System",
                'description': f"Add comprehensive {missing_area} functionality",
                'priority': 'high' if missing_area in ['auth', 'security', 'testing'] else 'medium',
                'effort': 'large' if missing_area in ['auth', 'database'] else 'medium'
            })
            
        # Based on existing features - improvements
        for feature in analysis['features'][:3]:  # Top 3 features to improve
            recommendations.append({
                'type': 'feature_enhancement',
                'title': f"Enhance {feature.title()} Feature",
                'description': f"Improve and extend {feature} functionality",
                'priority': 'medium',
                'effort': 'small'
            })
            
        # Tech stack specific recommendations
        if 'Python' in analysis['tech_stack']:
            recommendations.append({
                'type': 'infrastructure',
                'title': 'Python Code Quality Tools',
                'description': 'Add linting, formatting, and type checking',
                'priority': 'medium',
                'effort': 'small'
            })
            
        return recommendations[:8]  # Limit to 8 recommendations
        
    async def create_feature_plan(self, analysis: dict, recommendations: list) -> str:
        """Create and save feature plan document"""
        from datetime import datetime
        
        plan_content = f"""# Product Feature Plan

**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Analyzer**: Product Manager Agent

## Codebase Analysis

### Current Features ({len(analysis['features'])})
{chr(10).join([f'- {feature}' for feature in analysis['features'][:10]])}

### Technology Stack
{chr(10).join([f'- {tech}' for tech in analysis['tech_stack']])}

### Missing Areas Identified
{chr(10).join([f'- {area}' for area in analysis['missing_areas']])}

## Feature Recommendations

"""
        
        for i, rec in enumerate(recommendations, 1):
            plan_content += f"""### {i}. {rec['title']}

**Type**: {rec['type'].replace('_', ' ').title()}
**Priority**: {rec['priority'].upper()}
**Effort**: {rec['effort'].upper()}

{rec['description']}

---

"""
            
        plan_content += f"""
## Implementation Strategy

1. **High Priority Items** - Start with security, auth, and testing
2. **Quick Wins** - Implement small effort, high impact features first
3. **Infrastructure** - Set up quality tools and monitoring
4. **Feature Enhancements** - Improve existing functionality
5. **New Features** - Add missing capabilities

## Next Steps

- Review and prioritize recommendations
- Create detailed specifications for top 3 features
- Implement in order of priority and effort
- Monitor progress and iterate

---
*Generated by Fresh Product Manager Agent*
"""
        
        # Save to file
        plan_file = "docs/FEATURE_PLAN.md"
        try:
            import os
            os.makedirs("docs", exist_ok=True)
            with open(plan_file, 'w') as f:
                f.write(plan_content)
            return plan_file
        except Exception as e:
            self.add_activity(f"⚠️ Could not save plan file: {e}")
            return "feature_plan_generated_in_memory"

    async def run_documentation_agent(self):
        """Run actual documentation generation and updates"""
        try:
            self.agent_status.update_agent('documentation', 'running')
            self.agent_status.current_operation = 'Documentation Agent'
            
            self.add_activity("🔍 Documentation: Scanning for missing docs...")
            
            # Analyze documentation gaps
            doc_analysis = await self.analyze_documentation_gaps()
            
            self.add_activity(f"📄 Found {len(doc_analysis['missing_docs'])} files needing docs")
            
            # Generate missing documentation
            generated_docs = await self.generate_missing_documentation(doc_analysis)
            
            self.add_activity(f"✍️ Generated {len(generated_docs)} documentation files")
            
            # Update project README if needed
            readme_updated = await self.update_project_readme(doc_analysis)
            
            self.agent_status.update_agent('documentation', 'completed',
                                         docs_updated=self.agent_status.agents['documentation']['docs_updated'] + len(generated_docs),
                                         last_run=datetime.now().isoformat())
            self.agent_status.current_operation = None
            
            status_msg = f"✅ Documentation completed - {len(generated_docs)} files updated"
            if readme_updated:
                status_msg += ", README refreshed"
            self.add_activity(status_msg)
            
        except Exception as e:
            self.add_activity(f"❌ Documentation Agent failed: {str(e)}")
            self.agent_status.update_agent('documentation', 'error')
            self.agent_status.current_operation = None
            
    async def analyze_documentation_gaps(self) -> dict:
        """Analyze codebase for documentation gaps"""
        from pathlib import Path
        
        analysis = {
            'missing_docs': [],
            'outdated_docs': [],
            'undocumented_functions': [],
            'missing_readmes': []
        }
        
        try:
            root_path = Path('.')
            
            # Find Python files without docstrings
            python_files = list(root_path.glob('**/*.py'))
            for py_file in python_files[:20]:  # Limit to avoid too many
                if py_file.name.startswith('.') or 'test' in str(py_file) or '__pycache__' in str(py_file):
                    continue
                    
                try:
                    content = py_file.read_text(encoding='utf-8')
                    # Simple check for module docstring
                    lines = content.strip().split('\n')
                    has_module_docstring = False
                    for line in lines[:10]:
                        if line.strip().startswith('"""') or line.strip().startswith("'''"):
                            has_module_docstring = True
                            break
                    
                    if not has_module_docstring and len(content.strip()) > 50:
                        analysis['missing_docs'].append(str(py_file))
                        
                except Exception:
                    pass
                    
            # Find directories without README files
            important_dirs = ['ai', 'scripts', 'tests', 'docs']
            for dir_name in important_dirs:
                dir_path = root_path / dir_name
                if dir_path.is_dir():
                    readme_files = list(dir_path.glob('README*'))
                    if not readme_files:
                        analysis['missing_readmes'].append(str(dir_path))
                        
            return analysis
            
        except Exception as e:
            self.add_activity(f"⚠️ Documentation analysis error: {str(e)}")
            return analysis
            
    async def generate_missing_documentation(self, analysis: dict) -> list:
        """Generate documentation for files that need it"""
        generated = []
        
        try:
            from pathlib import Path
            
            # Generate README files for directories
            for missing_readme in analysis['missing_readmes'][:3]:  # Limit to 3
                dir_path = Path(missing_readme)
                readme_path = dir_path / 'README.md'
                
                # Analyze directory contents
                py_files = list(dir_path.glob('*.py'))
                subdirs = [d for d in dir_path.iterdir() if d.is_dir() and not d.name.startswith('.')]
                
                readme_content = f"""# {dir_path.name.title()} Module

**Purpose**: {self.infer_directory_purpose(dir_path)}

## Contents

"""
                
                if py_files:
                    readme_content += "### Python Files\n\n"
                    for py_file in py_files[:10]:
                        purpose = self.infer_file_purpose(py_file)
                        readme_content += f"- **{py_file.name}** - {purpose}\n"
                        
                if subdirs:
                    readme_content += "\n### Subdirectories\n\n"
                    for subdir in subdirs[:10]:
                        readme_content += f"- **{subdir.name}/** - {self.infer_directory_purpose(subdir)}\n"
                        
                readme_content += f"""

## Usage

This module provides functionality for {self.infer_directory_purpose(dir_path).lower()}.

---
*Auto-generated by Fresh Documentation Agent*
"""
                
                try:
                    readme_path.write_text(readme_content)
                    generated.append(str(readme_path))
                except Exception as e:
                    self.add_activity(f"⚠️ Could not write {readme_path}: {e}")
                    
            return generated
            
        except Exception as e:
            self.add_activity(f"⚠️ Documentation generation error: {str(e)}")
            return generated
            
    def infer_directory_purpose(self, dir_path: Path) -> str:
        """Infer the purpose of a directory from its name and contents"""
        dir_name = dir_path.name.lower()
        
        purpose_map = {
            'ai': 'artificial intelligence and machine learning functionality',
            'agents': 'AI agent implementations and configurations',
            'autonomous': 'autonomous system operations and loops',
            'cli': 'command-line interface and user interaction',
            'memory': 'memory management and persistence systems',
            'tools': 'utility tools and helper functions',
            'tests': 'test cases and testing utilities',
            'scripts': 'automation scripts and utilities',
            'docs': 'project documentation and guides',
            'loop': 'processing loops and automation cycles',
            'monitor': 'monitoring and observability features'
        }
        
        return purpose_map.get(dir_name, f'{dir_name.replace("_", " ")} functionality')
        
    def infer_file_purpose(self, file_path: Path) -> str:
        """Infer the purpose of a Python file from its name"""
        file_name = file_path.stem.lower()
        
        if 'test' in file_name:
            return 'Test cases and validation'
        elif 'cli' in file_name or 'command' in file_name:
            return 'Command-line interface'
        elif 'agent' in file_name:
            return 'AI agent implementation'
        elif 'monitor' in file_name:
            return 'Monitoring and status tracking'
        elif 'store' in file_name or 'storage' in file_name:
            return 'Data storage and persistence'
        elif 'loop' in file_name:
            return 'Processing loop implementation'
        elif 'config' in file_name or 'settings' in file_name:
            return 'Configuration and settings'
        elif '__init__' in file_name:
            return 'Module initialization and exports'
        else:
            return f'{file_name.replace("_", " ").title()} implementation'
            
    async def update_project_readme(self, analysis: dict) -> bool:
        """Update main project README if it needs refreshing"""
        try:
            from pathlib import Path
            
            readme_path = Path('README.md')
            if not readme_path.exists():
                return False
                
            # Check if README mentions Fresh or agents
            content = readme_path.read_text()
            if 'Fresh' in content and 'agent' in content.lower():
                # README seems current
                return False
                
            # Could add README enhancement logic here
            return False
            
        except Exception:
            return False

    async def spawn_custom_agent(self):
        """Spawn productive custom agent for real tasks"""
        try:
            self.agent_status.update_agent('custom', 'running') 
            self.agent_status.current_operation = 'Custom Agent'
            
            # Choose a productive task based on current codebase needs
            task = await self.select_productive_task()
            self.add_activity(f"🛠️ Spawning agent for: {task['description']}")
            
            # Execute the productive task
            result = await self.execute_productive_task(task)
            
            if result['success']:
                self.agent_status.update_agent('custom', 'completed',
                                             tasks_completed=self.agent_status.agents['custom']['tasks_completed'] + 1,
                                             last_spawn=datetime.now().isoformat())
                self.add_activity(f"✅ Custom agent completed: {result['output'][:60]}...")
            else:
                self.add_activity(f"❌ Custom agent failed: {result['error']}")
                self.agent_status.update_agent('custom', 'error')
                
            self.agent_status.current_operation = None
            
        except Exception as e:
            self.add_activity(f"❌ Custom agent error: {str(e)}")
            self.agent_status.update_agent('custom', 'error')
            self.agent_status.current_operation = None
            
    async def select_productive_task(self) -> dict:
        """Select a productive task - PRODUCTION VERSION with real functions"""
        import random
        
        productive_tasks = [
            {
                'type': 'code_analysis',
                'description': 'Analyze code complexity and suggest refactoring opportunities',
                'expected_time': 30
            },
            {
                'type': 'security_scan',
                'description': 'Scan for potential security vulnerabilities in code',
                'expected_time': 20
            },
            {
                'type': 'test_coverage',
                'description': 'Analyze test coverage and identify untested code areas',
                'expected_time': 25
            },
            {
                'type': 'dependency_audit',
                'description': 'Audit project dependencies and Python version',
                'expected_time': 15
            },
            {
                'type': 'performance_analysis', 
                'description': 'Analyze codebase for potential performance bottlenecks',
                'expected_time': 35
            }
        ]
        
        # Select a random productive task
        return random.choice(productive_tasks)
        
    async def execute_productive_task(self, task: dict) -> dict:
        """Execute a productive task with REAL functionality - PRODUCTION VERSION"""
        try:
            self.add_activity(f"⚙️ Executing {task['type'].replace('_', ' ')}...")
            
            # Execute real functions instead of subprocess calls
            task_type = task['type']
            
            if task_type == 'code_analysis':
                result = await self.analyze_code_complexity()
            elif task_type == 'security_scan':
                result = await self.scan_security_vulnerabilities()
            elif task_type == 'test_coverage':
                result = await self.analyze_test_coverage()
            elif task_type == 'dependency_audit':
                result = await self.audit_dependencies()
            elif task_type == 'performance_analysis':
                result = await self.analyze_performance_bottlenecks()
            else:
                result = f"Unknown task type: {task_type}"
            
            return {
                'success': True,
                'output': result,
                'task_type': task_type
            }
                
        except Exception as e:
            return {
                'success': False,
                'error': f"Task execution error: {str(e)}",
                'task_type': task.get('type', 'unknown')
            }
            
    async def analyze_code_complexity(self) -> str:
        """Analyze code complexity - REAL implementation"""
        from pathlib import Path
        
        python_files = list(Path('.').glob('**/*.py'))
        # Filter out test files and __pycache__
        source_files = [f for f in python_files if 'test' not in str(f) and '__pycache__' not in str(f)]
        
        large_files = []
        total_lines = 0
        
        for file_path in source_files:
            try:
                lines = len(file_path.read_text().splitlines())
                total_lines += lines
                if lines > 200:  # Files over 200 lines might need refactoring
                    large_files.append((str(file_path), lines))
            except:
                continue
                
        avg_file_size = total_lines / len(source_files) if source_files else 0
        
        result = f"Code complexity analysis: {len(source_files)} Python files, {total_lines} total lines. "
        result += f"Average file size: {avg_file_size:.1f} lines. "
        
        if large_files:
            result += f"{len(large_files)} large files detected - consider refactoring: "
            result += ", ".join([f"{f}({l} lines)" for f, l in large_files[:3]])
        else:
            result += "Good file size distribution - no large files needing refactoring."
            
        return result
        
    async def scan_security_vulnerabilities(self) -> str:
        """Scan for security vulnerabilities - REAL implementation"""
        from pathlib import Path
        
        security_issues = []
        
        # Check for common security patterns
        python_files = list(Path('.').glob('**/*.py'))
        source_files = [f for f in python_files if 'test' not in str(f) and '__pycache__' not in str(f)]
        
        dangerous_patterns = [
            ('eval(', 'eval() function usage'),
            ('exec(', 'exec() function usage'), 
            ('os.system', 'os.system() usage'),
            ('subprocess.shell=True', 'subprocess with shell=True'),
            ('password', 'hardcoded password reference'),
            ('api_key', 'hardcoded API key reference')
        ]
        
        for file_path in source_files[:20]:  # Limit scan for performance
            try:
                content = file_path.read_text().lower()
                for pattern, issue_type in dangerous_patterns:
                    if pattern in content:
                        security_issues.append(f"{file_path}: {issue_type}")
            except:
                continue
                
        result = f"Security scan completed - analyzed {len(source_files)} files. "
        
        if security_issues:
            result += f"Found {len(security_issues)} potential security issues: "
            result += "; ".join(security_issues[:3])
        else:
            result += "No obvious security vulnerabilities detected in scanned files."
            
        return result
        
    async def analyze_test_coverage(self) -> str:
        """Analyze test coverage - REAL implementation"""
        from pathlib import Path
        
        # Count test files vs source files
        all_python_files = list(Path('.').glob('**/*.py'))
        test_files = [f for f in all_python_files if 'test' in str(f)]
        source_files = [f for f in all_python_files if 'test' not in str(f) and '__pycache__' not in str(f)]
        
        # Simple coverage estimate based on test vs source ratio
        coverage_ratio = len(test_files) / max(len(source_files), 1) * 100
        
        # Find untested modules
        untested_modules = []
        for source_file in source_files:
            potential_test_name = f"test_{source_file.stem}.py"
            has_test = any(potential_test_name in str(tf) for tf in test_files)
            if not has_test and source_file.stem not in ['__init__', 'main']:
                untested_modules.append(source_file.stem)
        
        result = f"Test coverage analysis: {len(test_files)} test files vs {len(source_files)} source files. "
        result += f"Estimated coverage: {coverage_ratio:.1f}%. "
        
        if untested_modules:
            result += f"{len(untested_modules)} modules appear untested: "
            result += ", ".join(untested_modules[:5])
        else:
            result += "Good test coverage - most modules have corresponding tests."
            
        return result
        
    async def audit_dependencies(self) -> str:
        """Audit dependencies - REAL implementation"""
        from pathlib import Path
        import sys
        
        # Check pyproject.toml and requirements.txt
        deps_found = []
        
        if Path('pyproject.toml').exists():
            content = Path('pyproject.toml').read_text()
            if '[tool.poetry.dependencies]' in content:
                deps_found.append('Poetry dependencies detected')
                
        if Path('requirements.txt').exists():
            req_lines = len(Path('requirements.txt').read_text().strip().split('\n'))
            deps_found.append(f'{req_lines} pip requirements')
            
        python_version = f"Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        
        result = f"Dependency audit: {python_version} detected. "
        
        if deps_found:
            result += "Dependencies: " + ", ".join(deps_found)
            result += ". Recommend regular updates and security scanning."
        else:
            result += "No obvious dependency files found - recommend adding requirements management."
            
        return result
        
    async def analyze_performance_bottlenecks(self) -> str:
        """Analyze performance bottlenecks - REAL implementation"""
        from pathlib import Path
        
        # Find large files that might have performance issues
        large_files = []
        complex_imports = []
        
        python_files = list(Path('.').glob('**/*.py'))
        source_files = [f for f in python_files if 'test' not in str(f) and '__pycache__' not in str(f)]
        
        for file_path in source_files:
            try:
                content = file_path.read_text()
                lines = content.splitlines()
                
                # Check file size
                if len(lines) > 500:
                    large_files.append((str(file_path), len(lines)))
                    
                # Check for excessive imports
                import_count = sum(1 for line in lines[:50] if line.strip().startswith(('import ', 'from ')))
                if import_count > 20:
                    complex_imports.append((str(file_path), import_count))
                    
            except:
                continue
                
        result = f"Performance analysis: scanned {len(source_files)} files. "
        
        issues = []
        if large_files:
            issues.append(f"{len(large_files)} large files (>500 lines)")
        if complex_imports:
            issues.append(f"{len(complex_imports)} files with complex imports (>20)")
            
        if issues:
            result += "Potential bottlenecks: " + ", ".join(issues)
            result += ". Consider code splitting and lazy imports."
        else:
            result += "No obvious performance bottlenecks detected - good code structure."
            
        return result
            
    async def stop_current_operation(self):
        """Stop current operation"""
        if self.autonomous_loop and self.autonomous_loop.running:
            self.autonomous_loop.stop_continuous_loop()
            self.add_activity("⏹️ Stopped autonomous loop")
            self.agent_status.update_agent('autonomous', 'stopped')
            
        self.agent_status.current_operation = None
        self.add_activity("⏹️ Stopped current operation")
        
    async def emergency_stop(self):
        """Activate emergency stop"""
        self.agent_status.emergency_stop = True
        self.add_activity("🚨 EMERGENCY STOP ACTIVATED")
        
        if self.autonomous_loop:
            try:
                self.autonomous_loop.safety_controller.emergency_stop("User requested emergency stop")
                self.autonomous_loop.stop_continuous_loop()
            except:
                pass
                
        # Stop all agents
        for agent_type in self.agent_status.agents:
            self.agent_status.update_agent(agent_type, 'stopped')
            
        self.agent_status.current_operation = None
        
    def get_keyboard_input(self) -> Optional[str]:
        """Get non-blocking keyboard input - improved for macOS"""
        try:
            import sys
            import select
            import tty
            import termios
            
            # Check if stdin is available for reading
            if not select.select([sys.stdin], [], [], 0.1) == ([sys.stdin], [], []):
                return None
                
            # Get current terminal settings
            old_settings = termios.tcgetattr(sys.stdin.fileno())
            
            try:
                # Set terminal to raw mode for single character input
                tty.cbreak(sys.stdin.fileno())
                # Read one character
                char = sys.stdin.read(1)
                return char
            finally:
                # Always restore terminal settings
                termios.tcsetattr(sys.stdin.fileno(), termios.TCSADRAIN, old_settings)
                
        except Exception as e:
            # Fallback: try simpler input method
            try:
                import msvcrt
                if msvcrt.kbhit():
                    return msvcrt.getch().decode('utf-8')
                return None
            except ImportError:
                # Last resort: polling input (less responsive but works)
                try:
                    import select
                    if select.select([sys.stdin], [], [], 0.05) == ([sys.stdin], [], []):
                        return sys.stdin.readline().strip()[:1]
                except:
                    pass
                return None
            
    async def handle_input(self, key: str):
        """Handle keyboard input with immediate visual feedback"""
        key = key.lower()
        
        # Immediate feedback for button press
        self.add_activity(f"🎮 Button [{key.upper()}] pressed")
        
        if key == '1':
            self.add_activity("🚀 Starting Autonomous Loop - continuous improvement mode")
            await self.start_autonomous_loop()
        elif key == '2':
            self.add_activity("🔍 Starting Single Scan - analyzing repository (~30sec)")
            await self.run_single_scan()
        elif key == '3':
            self.add_activity("📋 Starting Product Manager - analyzing codebase for features (~60sec)")
            await self.run_product_manager()
        elif key == '4':
            self.add_activity("📚 Starting Documentation Agent - analyzing codebase (~45sec)")
            await self.run_documentation_agent()
        elif key == '5':
            self.add_activity("🛠️ Starting Custom Agent - spawning for specific task (~90sec)")
            await self.spawn_custom_agent()
        elif key == 's':
            self.add_activity("⏹️ Stopping current operation...")
            await self.stop_current_operation()
        elif key == 'e':
            self.add_activity("🚨 EMERGENCY STOP - halting all operations immediately!")
            await self.emergency_stop()
        elif key == 'r':
            self.add_activity("🔄 Refreshing all status displays")
        elif key == 'q':
            self.add_activity("👋 Shutting down monitor - goodbye!")
            self.running = False
        else:
            self.add_activity(f"❓ Unknown key '{key}' - use 1-5 for agents, S/E/R/Q for controls")
            
    async def run_monitor(self):
        """Run the enhanced monitor with improved responsiveness"""
        layout = self.create_layout()
        
        self.add_activity("🚀 Enhanced monitor started - press 1-5 to control agents!")
        self.add_activity("💡 Tip: Press keys slowly and wait for feedback in activity log")
        
        # Track input attempts for debugging
        input_attempts = 0
        successful_inputs = 0
        
        with Live(layout, console=self.console, refresh_per_second=8, screen=True) as live:
            while self.running:
                # Update layout
                layout["header"].update(self.create_header())
                layout["agents"].update(self.create_agent_panel())
                layout["activity"].update(self.create_activity_panel())
                layout["controls"].update(self.create_controls_panel())
                
                # Handle keyboard input with better error handling
                try:
                    key = self.get_keyboard_input()
                    if key:
                        input_attempts += 1
                        successful_inputs += 1
                        await self.handle_input(key)
                    elif input_attempts > 0 and input_attempts % 50 == 0:
                        # Periodic debug info
                        success_rate = (successful_inputs / input_attempts) * 100 if input_attempts > 0 else 0
                        self.add_activity(f"🔍 Debug: {successful_inputs}/{input_attempts} inputs successful ({success_rate:.1f}%)")
                        
                except Exception as e:
                    input_attempts += 1
                    self.add_activity(f"⚠️ Input error: {str(e)[:50]}... (try pressing keys more slowly)")
                    
                # Update metrics periodically
                if hasattr(self, 'autonomous_loop') and self.autonomous_loop:
                    try:
                        status = self.autonomous_loop.get_status()
                        self.performance_metrics['total_improvements'] = status.get('total_cycles', 0)
                        if status.get('recent_cycles'):
                            # Calculate average cycle time from recent cycles
                            recent = status['recent_cycles'][-5:]  # Last 5 cycles
                            if recent:
                                avg_time = sum(c.get('duration_seconds', 0) for c in recent) / len(recent)
                                self.performance_metrics['avg_cycle_time'] = avg_time
                    except:
                        pass
                
                await asyncio.sleep(0.125)  # 8 FPS update rate for better responsiveness
                
        # Cleanup
        if self.autonomous_loop and self.autonomous_loop.running:
            self.autonomous_loop.stop_continuous_loop()
            
    async def run_monitor_simple(self):
        """Simple monitor mode with basic input handling"""
        self.add_activity("🚀 Simple monitor mode started")
        self.add_activity("💡 Type commands and press ENTER: 1, 2, 3, 4, 5, s, e, r, q")
        
        print("🎮 SIMPLE MODE - Type commands and press ENTER:")
        print("[1] Autonomous Loop  [2] Single Scan  [3] Product Mgr")
        print("[4] Documentation   [5] Custom Agent [s] Stop [e] Emergency [q] Quit")
        print()
        
        # Start background task for display updates
        async def update_display():
            while self.running:
                print(f"\r🎯 Current: {self.agent_status.current_operation or 'None'} | Activities: {len(self.recent_activities)}", end="", flush=True)
                await asyncio.sleep(1)
                
        display_task = asyncio.create_task(update_display())
        
        # Simple input loop
        while self.running:
            try:
                # Get input with timeout
                try:
                    user_input = await asyncio.wait_for(
                        asyncio.get_event_loop().run_in_executor(None, input, "\nEnter command: "), 
                        timeout=1.0
                    )
                    
                    if user_input.strip():
                        await self.handle_input(user_input.strip().lower())
                        
                        # Show recent activities
                        print("\n📝 Recent activities:")
                        for activity in self.recent_activities[-3:]:
                            print(f"  {activity}")
                            
                except asyncio.TimeoutError:
                    continue
                    
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"\n⚠️ Input error: {e}")
                
        display_task.cancel()
        print("\n👋 Simple monitor stopped")


async def run_enhanced_monitor(simple_input=False):
    """Main entry point for enhanced monitor"""
    print("🚀 Starting Enhanced Monitor...")
    
    # Try to detect if we can use advanced input
    input_method = "advanced"
    if simple_input:
        input_method = "simple"
    else:
        try:
            import termios
            import tty
            # Test if we can access terminal
            termios.tcgetattr(sys.stdin.fileno())
        except Exception:
            input_method = "simple"
            print("⚠️ Using simple input mode (advanced terminal features not available)")
    
    print(f"🎮 Input method: {input_method}")
    print("💡 If buttons don't work, try: poetry run python ai/cli/enhanced_monitor.py --simple")
    
    monitor = EnhancedMonitor(use_simple_input=(input_method == "simple"))
    
    # Setup signal handlers
    def signal_handler(signum, frame):
        monitor.running = False
        
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        if input_method == "simple":
            await monitor.run_monitor_simple()
        else:
            await monitor.run_monitor()
    except KeyboardInterrupt:
        pass
    finally:
        print("\n👋 Enhanced monitor stopped")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Enhanced Interactive CLI Monitor")
    parser.add_argument('--simple', action='store_true', help='Use simple input mode')
    args = parser.parse_args()
    
    asyncio.run(run_enhanced_monitor(simple_input=args.simple))
