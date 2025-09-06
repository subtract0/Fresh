import click
from typing import Optional
from rich.console import Console
from rich.table import Table
from pathlib import Path
import json
import os

console = Console()

def load_config(config_path: str):
    with open(config_path, 'r') as f:
        return json.load(f)

def validate_config(config):
    required_keys = ['api_key', 'endpoint']
    for key in required_keys:
        if key not in config:
            raise ValueError(f"Missing required config key: {key}")

def fetch_agent_metrics(config):
    # Simulating fetching metrics from an API or database
    return {
        "total_agents": 100,
        "active_agents": 80,
        "inactive_agents": 20,
        "average_response_time": "200ms"
    }

@click.command()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--output', '-o', type=click.Choice(['json', 'table', 'plain']), 
              default='table', help='Output format')
@click.option('--config', type=click.Path(exists=True), help='Configuration file')
@click.pass_context
def agentmetrics(ctx, verbose: bool, output: str, config: Optional[str]):
    """
    AgentMetrics command.
    Fetch and display metrics for agents.
    """
    try:
        if verbose:
            console.print(f"[blue]Running AgentMetrics command...[/blue]")
        
        if config is None:
            raise ValueError("Configuration file must be provided.")
        
        config_data = load_config(config)
        validate_config(config_data)

        result_data = fetch_agent_metrics(config_data)
        result_data["config_used"] = config
        result_data["verbose"] = verbose
        
        # Output results based on format
        if output == 'json':
            console.print_json(json.dumps(result_data, indent=2))
        elif output == 'table':
            table = Table(title=f"AgentMetrics Results")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="magenta")
            
            for key, value in result_data.items():
                table.add_row(str(key), str(value))
            
            console.print(table)
        else:  # plain
            for key, value in result_data.items():
                console.print(f"{key}: {value}")
        
        if verbose:
            console.print(f"[green]✅ AgentMetrics completed successfully[/green]")
            
    except Exception as e:
        console.print(f"[red]❌ AgentMetrics failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)

__all__ = ["agentmetrics"]