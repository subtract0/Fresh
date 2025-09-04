"""
CLI commands for Product-Driven Autonomous Development

Provides CLI interface for the product manager agent and product-driven
autonomous orchestrator functionality.
"""
import asyncio
import json
import sys
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

try:
    import click
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.progress import Progress, SpinnerColumn, TextColumn
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    # Fallback console for testing
    class Console:
        def print(self, text):
            print(text)

from ai.agents.product_manager import ProductManagerAgent, create_product_manager_agent
from ai.orchestration.product_autonomous_orchestrator import ProductAutonomousOrchestrator, create_product_orchestrator
from ai.memory.intelligent_store import IntelligentMemoryStore

console = Console()

# Make click decorators optional for testing
if not RICH_AVAILABLE:
    def click_dummy(*args, **kwargs):
        def decorator(func):
            return func
        return decorator
    
    class ClickGroup:
        def __init__(self, name=None):
            self.commands = {}
        def add_command(self, cmd):
            pass
        def command(self, *args, **kwargs):
            return click_dummy
    
    click = type('click', (), {
        'group': lambda **kw: ClickGroup(),
        'argument': click_dummy,
        'option': click_dummy,
        'Choice': lambda choices: str
    })()

def scan_repository_for_features(path: str = ".") -> Dict[str, Any]:
    """Scan repository and convert to feature format."""
    try:
        from ai.loop.repo_scanner import scan_repository
        
        # Run repository scan
        tasks = scan_repository(path)
        
        # Convert tasks to features format
        features = {}
        for task in tasks:
            feature_name = f"Task-{task.type.value}-{len(features)}"
            features[feature_name] = {
                "name": feature_name,
                "description": task.description,
                "issues": [f"{task.type.value}: {task.description}"],
                "status": "needs_attention",
                "path": str(task.file_path),
                "line_number": task.line_number
            }
        
        return {
            "features": features,
            "total_count": len(features),
            "scanned_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        if RICH_AVAILABLE:
            console.print(f"⚠️ Scan failed: {e}")
        else:
            print(f"⚠️ Scan failed: {e}")
        return {"features": {}, "total_count": 0}

@click.group(name='product')
@click.pass_context
def product_cli(ctx):
    """Product Manager and product-driven autonomous development commands."""
    pass

@product_cli.command('analyze')
@click.argument('feature_name', required=False)
@click.option('--description', '-d', help='Feature description')
@click.option('--issues', '-i', multiple=True, help='Known issues with the feature')
@click.option('--output', '-o', type=click.Choice(['json', 'prd', 'summary']), default='summary', help='Output format')
@click.option('--save-prd', is_flag=True, help='Save PRD document to docs/prds/')
def analyze_feature(feature_name: Optional[str], description: str, issues: tuple, output: str, save_prd: bool):
    """Analyze a feature using Product Manager agent."""
    
    console.print("🎯 [bold blue]Product Manager Analysis[/bold blue]")
    
    try:
        # Create product manager
        pm = create_product_manager_agent()
        
        # If no feature specified, scan for features
        if not feature_name:
            console.print("🔍 Scanning codebase for features...")
            scan_result = scan_repository_for_features(".")
            
            if not scan_result or not scan_result.get('features'):
                console.print("❌ No features found to analyze")
                return
            
            # Display available features
            table = Table(title="Available Features")
            table.add_column("Feature", style="cyan")
            table.add_column("Status", style="yellow")  
            table.add_column("Issues", style="red")
            
            for name, data in scan_result['features'].items():
                issues_str = ", ".join(data.get('issues', []))
                table.add_row(name, data.get('status', 'unknown'), issues_str)
            
            console.print(table)
            
            # Let user pick a feature
            feature_list = list(scan_result['features'].keys())
            if len(feature_list) == 1:
                feature_name = feature_list[0]
                console.print(f"📍 Analyzing single feature: {feature_name}")
            else:
                console.print("\n💡 Run with specific feature name: fresh product analyze <feature_name>")
                return
        
        # Build feature data
        if feature_name and not description and not issues:
            # Try to get from scan results
            scan_result = scan_repository_for_features(".")
            if scan_result and scan_result.get('features', {}).get(feature_name):
                feature_data = scan_result['features'][feature_name]
                feature_data['name'] = feature_name
            else:
                feature_data = {'name': feature_name, 'description': '', 'issues': []}
        else:
            feature_data = {
                'name': feature_name or 'Unknown Feature',
                'description': description or '',
                'issues': list(issues) or []
            }
        
        # Run analysis
        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
            task = progress.add_task("Analyzing feature...", total=None)
            
            try:
                spec = pm.analyze_feature_request(feature_data)
                progress.remove_task(task)
                
                # Output results
                if output == 'json':
                    # Convert to JSON-serializable format
                    result = {
                        'feature_name': spec.feature_name,
                        'rice_score': {
                            'score': spec.rice_score.score,
                            'reach': spec.rice_score.reach,
                            'impact': spec.rice_score.impact,
                            'confidence': spec.rice_score.confidence,
                            'effort': spec.rice_score.effort
                        },
                        'problem_analysis': {
                            'problem_statement': spec.problem_analysis.problem_statement,
                            'severity_score': spec.problem_analysis.severity_score,
                            'affected_users': spec.problem_analysis.affected_users
                        },
                        'requirements_count': len(spec.requirements),
                        'estimated_effort_days': sum(spec.effort_estimate.values())
                    }
                    console.print(json.dumps(result, indent=2))
                
                elif output == 'prd':
                    prd_content = pm.create_prd_document(spec)
                    console.print(prd_content)
                    
                    if save_prd:
                        prd_path = Path(f"docs/prds/PRD-{spec.feature_name.replace(' ', '-')}.md")
                        prd_path.parent.mkdir(parents=True, exist_ok=True)
                        prd_path.write_text(prd_content)
                        console.print(f"📄 PRD saved to: {prd_path}")
                
                else:  # summary
                    _display_analysis_summary(spec)
                    
            except ValueError as e:
                progress.remove_task(task)
                console.print(f"❌ Analysis failed: {e}")
                
    except Exception as e:
        console.print(f"💥 Error: {e}")

def _display_analysis_summary(spec):
    """Display a formatted summary of the analysis."""
    
    # Header
    console.print(f"\n📊 [bold green]Analysis Results: {spec.feature_name}[/bold green]")
    
    # Problem section
    problem_panel = Panel(
        f"**Problem**: {spec.problem_analysis.problem_statement}\n"
        f"**Severity**: {spec.problem_analysis.severity_score}/10\n" 
        f"**Affected Users**: {', '.join(spec.problem_analysis.affected_users)}\n"
        f"**Frequency**: {spec.problem_analysis.frequency}",
        title="🎯 Problem Analysis",
        border_style="red"
    )
    console.print(problem_panel)
    
    # RICE Score
    rice_panel = Panel(
        f"**Score**: {spec.rice_score.score:.1f}\n"
        f"**Reach**: {spec.rice_score.reach} users/quarter\n"
        f"**Impact**: {spec.rice_score.impact:.1f}/3.0\n" 
        f"**Confidence**: {spec.rice_score.confidence:.0%}\n"
        f"**Effort**: {spec.rice_score.effort} person-months",
        title="🎲 RICE Prioritization",
        border_style="blue"
    )
    console.print(rice_panel)
    
    # User Story
    story_text = (
        f"**As a** {spec.user_story.persona}\n"
        f"**I want to** {spec.user_story.action}\n" 
        f"**So that I can** {spec.user_story.benefit}"
    )
    story_panel = Panel(story_text, title="👤 User Story", border_style="green")
    console.print(story_panel)
    
    # Requirements Summary  
    req_table = Table(title="📋 Requirements Summary")
    req_table.add_column("ID", style="cyan")
    req_table.add_column("Priority", style="yellow")
    req_table.add_column("Description", style="white")
    
    for req in spec.requirements[:5]:  # Show first 5
        req_table.add_row(req.requirement_id, req.priority, req.description)
    
    if len(spec.requirements) > 5:
        req_table.add_row("...", "...", f"({len(spec.requirements) - 5} more requirements)")
    
    console.print(req_table)
    
    # Success Metrics
    primary_metric = spec.success_metrics['primary_metric']
    metrics_text = (
        f"**Primary**: {primary_metric['name']}\n"
        f"**Target**: {primary_metric['target']}\n"
        f"**Measurement**: {primary_metric['measurement']}"
    )
    metrics_panel = Panel(metrics_text, title="📈 Success Metrics", border_style="yellow")
    console.print(metrics_panel)
    
    # Bottom line
    effort_days = sum(spec.effort_estimate.values())
    console.print(f"\n💡 **Recommendation**: {'✅ High Priority' if spec.rice_score.score >= 10 else '⚠️ Consider Deferring'} "
                  f"(~{effort_days:.0f} days estimated)")

@product_cli.command('roadmap') 
@click.option('--horizon', '-h', default=90, help='Planning horizon in days')
@click.option('--output', '-o', type=click.Choice(['json', 'markdown', 'table']), default='table', help='Output format')
@click.option('--save', is_flag=True, help='Save roadmap to docs/roadmap.md')
def generate_roadmap(horizon: int, output: str, save: bool):
    """Generate product roadmap from feature analysis."""
    
    console.print("🗺️ [bold blue]Generating Product Roadmap[/bold blue]")
    
    try:
        # Scan features
        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
            task = progress.add_task("Scanning features...", total=None)
            
            scan_result = scan_repository_for_features(".")
            progress.update(task, description="Analyzing features...")
            
            if not scan_result or not scan_result.get('features'):
                progress.remove_task(task)
                console.print("❌ No features found for roadmap")
                return
            
            # Convert to PM format
            features = []
            for feature_name, feature_data in scan_result['features'].items():
                features.append({
                    'name': feature_name,
                    'description': feature_data.get('description', ''),
                    'issues': feature_data.get('issues', []),
                    'status': feature_data.get('status', 'unknown')
                })
            
            # Create PM and generate roadmap
            pm = create_product_manager_agent()
            progress.update(task, description="Generating roadmap...")
            
            roadmap = pm.generate_product_roadmap(features, horizon)
            prioritized = pm.prioritize_features(features)
            
            progress.remove_task(task)
        
        # Output roadmap
        if output == 'json':
            result = {
                'roadmap': roadmap,
                'prioritized_features': [(f, s.score) for f, s in prioritized]
            }
            console.print(json.dumps(result, indent=2, default=str))
            
        elif output == 'markdown':
            markdown_content = _generate_roadmap_markdown(roadmap, prioritized)
            console.print(markdown_content)
            
            if save:
                roadmap_path = Path("docs/roadmap.md")
                roadmap_path.parent.mkdir(parents=True, exist_ok=True)
                roadmap_path.write_text(markdown_content)
                console.print(f"\n💾 Roadmap saved to: {roadmap_path}")
                
        else:  # table
            _display_roadmap_table(roadmap, prioritized)
            
    except Exception as e:
        console.print(f"💥 Error generating roadmap: {e}")

def _generate_roadmap_markdown(roadmap: Dict[str, Any], prioritized: list) -> str:
    """Generate markdown roadmap document."""
    
    content = f"""# Product Roadmap

Generated: {datetime.now().strftime("%Y-%m-%d %H:%M")}
Planning Horizon: {roadmap.get('roadmap_period', 'N/A')}

## Strategic Themes

"""
    
    for theme in roadmap.get('strategic_themes', []):
        content += f"- {theme}\n"
    
    content += f"""

## Now (0-30 days) - {roadmap.get('now_0_30_days', {}).get('focus', '')}

"""
    for feature in roadmap.get('now_0_30_days', {}).get('features', []):
        content += f"- [ ] {feature}\n"
    
    content += f"""

## Next (30-60 days) - {roadmap.get('next_30_60_days', {}).get('focus', '')}

"""
    for feature in roadmap.get('next_30_60_days', {}).get('features', []):
        content += f"- [ ] {feature}\n"
    
    content += f"""

## Later (60-90 days) - {roadmap.get('later_60_90_days', {}).get('focus', '')}

"""  
    for feature in roadmap.get('later_60_90_days', {}).get('features', []):
        content += f"- [ ] {feature}\n"
    
    # Add prioritization details
    content += "\n## Feature Prioritization (RICE Scores)\n\n"
    for feature, rice_score in prioritized[:10]:  # Top 10
        content += f"- **{feature.get('name', 'Unknown')}**: {rice_score.score:.1f}\n"
    
    backlog_count = roadmap.get('backlog', {}).get('features_count', 0)
    if backlog_count > 0:
        content += f"\n*+{backlog_count} more features in backlog*\n"
    
    return content

def _display_roadmap_table(roadmap: Dict[str, Any], prioritized: list):
    """Display roadmap as formatted tables."""
    
    from datetime import datetime
    
    # Header
    console.print(f"\n🗺️ [bold blue]Product Roadmap[/bold blue] ({roadmap.get('roadmap_period', 'N/A')})")
    console.print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    
    # Strategic themes
    themes_panel = Panel(
        "\n".join(f"• {theme}" for theme in roadmap.get('strategic_themes', [])),
        title="🎯 Strategic Themes",
        border_style="blue"
    )
    console.print(themes_panel)
    
    # Now section
    now_table = Table(title=f"Now (0-30 days): {roadmap.get('now_0_30_days', {}).get('focus', '')}")
    now_table.add_column("Feature", style="green")
    
    for feature in roadmap.get('now_0_30_days', {}).get('features', []):
        now_table.add_row(feature)
    
    console.print(now_table)
    
    # Next section
    next_table = Table(title=f"Next (30-60 days): {roadmap.get('next_30_60_days', {}).get('focus', '')}")
    next_table.add_column("Feature", style="yellow")
    
    for feature in roadmap.get('next_30_60_days', {}).get('features', []):
        next_table.add_row(feature)
    
    console.print(next_table)
    
    # Prioritization table
    priority_table = Table(title="🎲 Top Priorities (RICE Score)")
    priority_table.add_column("Rank", style="cyan")
    priority_table.add_column("Feature", style="white")
    priority_table.add_column("RICE Score", style="green")
    priority_table.add_column("Impact", style="yellow")
    
    for i, (feature, rice_score) in enumerate(prioritized[:10], 1):
        impact_emoji = "🔥" if rice_score.score >= 15 else "⚡" if rice_score.score >= 8 else "💡"
        priority_table.add_row(
            str(i),
            feature.get('name', 'Unknown'),
            f"{rice_score.score:.1f}",
            impact_emoji
        )
    
    console.print(priority_table)
    
    # Backlog summary
    backlog_count = roadmap.get('backlog', {}).get('features_count', 0)
    if backlog_count > 0:
        console.print(f"\n📋 [dim]+{backlog_count} more features in backlog[/dim]")

@product_cli.command('auto')
@click.option('--agents', '-a', default=3, help='Maximum number of concurrent agents')
@click.option('--budget', '-b', default=5.0, help='API budget limit in EUR')
@click.option('--overnight', is_flag=True, help='Enable overnight autonomous operation')
@click.option('--min-rice', default=5.0, help='Minimum RICE score for auto-approval')
@click.option('--no-prds', is_flag=True, help='Disable PRD generation')
def start_product_auto(agents: int, budget: float, overnight: bool, min_rice: float, no_prds: bool):
    """Start product-driven autonomous development."""
    
    console.print("🚀 [bold blue]Starting Product-Driven Autonomous Development[/bold blue]")
    
    async def _start_auto():
        try:
            # Create memory store and orchestrator
            memory_store = IntelligentMemoryStore()
            orchestrator = await create_product_orchestrator(memory_store)
            
            # Configure product-specific settings
            orchestrator.min_rice_score = min_rice
            orchestrator.generate_prds = not no_prds
            
            console.print(f"⚙️ Configuration:")
            console.print(f"  • Max agents: {agents}")
            console.print(f"  • Budget limit: €{budget}")
            console.print(f"  • Min RICE score: {min_rice}")
            console.print(f"  • Generate PRDs: {not no_prds}")
            console.print(f"  • Overnight mode: {overnight}")
            
            # Start autonomous operation
            result = await orchestrator.start_autonomous_operation(
                max_agents=agents,
                budget_limit=budget,
                overnight_mode=overnight
            )
            
            console.print("\n✅ [bold green]Product-driven autonomous development started![/bold green]")
            console.print(f"Orchestrator ID: {result.get('orchestrator_id')}")
            
            # Display product context
            product_ctx = result.get('product_context', {})
            console.print(f"\n📊 Product Context:")
            console.print(f"  • Features prioritized: {product_ctx.get('prioritized_features_count', 0)}")
            console.print(f"  • Roadmap generated: {product_ctx.get('roadmap_generated', False)}")
            console.print(f"  • Auto-approval enabled: {product_ctx.get('auto_approval_enabled', False)}")
            
            console.print(f"\n💡 Monitor progress with: fresh product status")
            
        except Exception as e:
            console.print(f"❌ Failed to start: {e}")
    
    asyncio.run(_start_auto())

@product_cli.command('status')  
def product_status():
    """Show product-driven autonomous development status."""
    
    console.print("📊 [bold blue]Product Development Status[/bold blue]")
    
    async def _show_status():
        try:
            memory_store = IntelligentMemoryStore()
            orchestrator = ProductAutonomousOrchestrator(memory_store)
            
            report = await orchestrator.generate_product_status_report()
            
            # Display orchestrator status
            orch_status = report.get('orchestrator_status', {})
            
            status_table = Table(title="System Status")
            status_table.add_column("Metric", style="cyan")
            status_table.add_column("Value", style="white")
            
            status_table.add_row("Active Agents", str(orch_status.get('active_agents', 0)))
            status_table.add_row("Total Tasks", str(orch_status.get('total_tasks', 0)))
            status_table.add_row("API Usage", f"€{orch_status.get('total_cost', 0):.2f}")
            status_table.add_row("Runtime", orch_status.get('runtime', 'N/A'))
            
            console.print(status_table)
            
            # Display product metrics
            product_metrics = report.get('product_metrics', {})
            
            product_table = Table(title="Product Metrics")
            product_table.add_column("Metric", style="cyan")
            product_table.add_column("Value", style="green")
            
            product_table.add_row("Product Tasks", str(product_metrics.get('total_product_tasks', 0)))
            product_table.add_row("Total RICE Score", f"{product_metrics.get('total_rice_score', 0):.1f}")
            product_table.add_row("Avg Problem Severity", f"{product_metrics.get('average_problem_severity', 0):.1f}/10")
            
            console.print(product_table)
            
            # Display top priorities
            top_priorities = report.get('top_priorities', [])
            if top_priorities:
                priority_table = Table(title="🔥 Top Priorities")
                priority_table.add_column("Feature", style="white")
                priority_table.add_column("RICE Score", style="green")
                priority_table.add_column("Impact", style="yellow")
                
                for priority in top_priorities:
                    impact = "🔥" if priority['rice_score'] >= 15 else "⚡" if priority['rice_score'] >= 8 else "💡"
                    priority_table.add_row(
                        priority['feature'],
                        f"{priority['rice_score']:.1f}",
                        impact
                    )
                
                console.print(priority_table)
            
            # Display roadmap summary
            roadmap = report.get('roadmap_summary', {})
            if roadmap.get('strategic_themes'):
                roadmap_panel = Panel(
                    f"**Now**: {roadmap.get('now_focus', 'Not set')}\n"
                    f"**Next**: {roadmap.get('next_focus', 'Not set')}\n" 
                    f"**Backlog**: {roadmap.get('backlog_size', 0)} features",
                    title="🗺️ Roadmap Focus",
                    border_style="blue"
                )
                console.print(roadmap_panel)
            
            # PRD Documents
            prd_count = len(report.get('prd_documents', []))
            if prd_count > 0:
                console.print(f"\n📄 Generated {prd_count} PRD documents")
            
        except Exception as e:
            console.print(f"❌ Error retrieving status: {e}")
    
    asyncio.run(_show_status())

if __name__ == '__main__':
    product_cli()
