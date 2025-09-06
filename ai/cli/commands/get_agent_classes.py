import click
from typing import Optional
from rich.console import Console
from rich.table import Table
from pathlib import Path
import json
import os

console = Console()

def load_config(config_path: str):
    if config_path and Path(config_path).is_file():
        with open(config_path, 'r') as file:
            return json.load(file)
    return {}

def get_available_agent_classes(config):
    # Simulated logic to retrieve agent classes based on configuration
    agent_classes = config.get("agent_classes", [])
    if not agent_classes:
        raise ValueError("No agent classes found in the configuration.")
    return agent_classes

@click.command()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--output', '-o', type=click.Choice(['json', 'table', 'plain']), 
              default='table', help='Output format')
@click.option('--config', type=click.Path(exists=True), help='Configuration file')
@click.pass_context
def get_agent_classes(ctx, verbose: bool, output: str, config: Optional[str]):
    """
    get_agent_classes command.
    Retrieves available agent classes from the provided configuration file.
    """
    try:
        if verbose:
            console.print(f"[blue]Running get_agent_classes command...[/blue]")
        
        config_data = load_config(config)
        agent_classes = get_available_agent_classes(config_data)
        
        result_data = {
            "feature": "get_agent_classes",
            "status": "success", 
            "agent_classes": agent_classes,
            "config_used": config,
            "verbose": verbose
        }
        
        # Output results based on format
        if output == 'json':
            console.print_json(json.dumps(result_data, indent=2))
        elif output == 'table':
            table = Table(title=f"get_agent_classes Results")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="magenta")
            
            for key, value in result_data.items():
                if isinstance(value, list):
                    value = ', '.join(value)
                table.add_row(str(key), str(value))
            
            console.print(table)
        else:  # plain
            for key, value in result_data.items():
                if isinstance(value, list):
                    value = ', '.join(value)
                console.print(f"{key}: {value}")
        
        if verbose:
            console.print(f"[green]✅ get_agent_classes completed successfully[/green]")
            
    except ValueError as ve:
        console.print(f"[red]❌ get_agent_classes failed: {str(ve)}[/red]")
        ctx.exit(1)
    except Exception as e:
        console.print(f"[red]❌ get_agent_classes failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)

__all__ = ["get_agent_classes"]