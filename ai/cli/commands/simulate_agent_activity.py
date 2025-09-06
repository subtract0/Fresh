import click
from typing import Optional
from rich.console import Console
from rich.table import Table
from pathlib import Path
import json
import yaml

console = Console()

def load_config(config_path: str):
    if config_path.endswith('.json'):
        with open(config_path, 'r') as f:
            return json.load(f)
    elif config_path.endswith('.yaml') or config_path.endswith('.yml'):
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    else:
        raise ValueError("Unsupported config file format. Use JSON or YAML.")

def simulate_activity(config):
    # Simulate some agent activity based on the configuration
    # This is a placeholder for actual simulation logic
    if 'agents' not in config:
        raise ValueError("Configuration must contain 'agents' key.")
    
    results = []
    for agent in config['agents']:
        result = {
            "agent_id": agent.get("id", "unknown"),
            "status": "active",
            "activity": "simulated_activity"
        }
        results.append(result)
    
    return results

@click.command()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--output', '-o', type=click.Choice(['json', 'table', 'plain']), 
              default='table', help='Output format')
@click.option('--config', type=click.Path(exists=True), help='Configuration file')
@click.pass_context
def simulate_agent_activity(ctx, verbose: bool, output: str, config: Optional[str]):
    """
    Simulate agent activity based on the provided configuration.
    """
    try:
        if verbose:
            console.print(f"[blue]Running simulate_agent_activity command...[/blue]")
        
        if not config:
            raise ValueError("Configuration file must be provided.")
        
        config_data = load_config(config)
        
        result_data = simulate_activity(config_data)
        
        # Output results based on format
        if output == 'json':
            console.print_json(json.dumps(result_data, indent=2))
        elif output == 'table':
            table = Table(title=f"simulate_agent_activity Results")
            table.add_column("Agent ID", style="cyan")
            table.add_column("Status", style="magenta")
            table.add_column("Activity", style="magenta")
            
            for item in result_data:
                table.add_row(item["agent_id"], item["status"], item["activity"])
            
            console.print(table)
        else:  # plain
            for item in result_data:
                console.print(f"Agent ID: {item['agent_id']}, Status: {item['status']}, Activity: {item['activity']}")
        
        if verbose:
            console.print(f"[green]✅ simulate_agent_activity completed successfully[/green]")
            
    except Exception as e:
        console.print(f"[red]❌ simulate_agent_activity failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)

__all__ = ["simulate_agent_activity"]