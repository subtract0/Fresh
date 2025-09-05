import click
from typing import Optional
from rich.console import Console
from rich.table import Table
from pathlib import Path
import json
import os

console = Console()

def load_config(config_path: str):
    with open(config_path, 'r') as file:
        return json.load(file)

def get_active_agents_from_config(config):
    # Simulated logic to get active agents based on the configuration
    active_agents = config.get("active_agents", [])
    return active_agents

@click.command()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--output', '-o', type=click.Choice(['json', 'table', 'plain']), 
              default='table', help='Output format')
@click.option('--config', type=click.Path(exists=True), help='Configuration file')
@click.pass_context
def get_active_agents(ctx, verbose: bool, output: str, config: Optional[str]):
    """
    get_active_agents command.
    Retrieves and displays active agents based on the provided configuration.
    """
    try:
        if verbose:
            console.print(f"[blue]Running get_active_agents command...[/blue]")
        
        if not config:
            raise ValueError("Configuration file must be provided.")
        
        config_data = load_config(config)
        active_agents = get_active_agents_from_config(config_data)
        
        if not active_agents:
            raise ValueError("No active agents found in the configuration.")
        
        result_data = {
            "feature": "get_active_agents",
            "status": "success", 
            "active_agents": active_agents,
            "config_used": config,
            "verbose": verbose
        }
        
        # Output results based on format
        if output == 'json':
            console.print_json(json.dumps(result_data, indent=2))
        elif output == 'table':
            table = Table(title=f"get_active_agents Results")
            table.add_column("Agent ID", style="cyan")
            table.add_column("Agent Name", style="magenta")
            
            for agent in active_agents:
                table.add_row(str(agent.get("id")), str(agent.get("name")))
            
            console.print(table)
        else:  # plain
            for agent in active_agents:
                console.print(f"Agent ID: {agent.get('id')}, Agent Name: {agent.get('name')}")
        
        if verbose:
            console.print(f"[green]✅ get_active_agents completed successfully[/green]")
            
    except Exception as e:
        console.print(f"[red]❌ get_active_agents failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)

__all__ = ["get_active_agents"]