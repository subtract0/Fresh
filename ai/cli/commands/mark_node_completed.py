import click
from typing import Optional
from rich.console import Console
from rich.table import Table
from pathlib import Path
import json
import os

console = Console()

def load_config(config_path: str):
    if config_path and Path(config_path).exists():
        with open(config_path, 'r') as file:
            return json.load(file)
    return {}

def mark_node_as_completed(node_id: str, config: dict):
    # Simulate marking a node as completed
    # In a real implementation, this would interact with a database or service
    if node_id not in config.get('nodes', {}):
        raise ValueError(f"Node ID '{node_id}' not found in configuration.")
    config['nodes'][node_id]['completed'] = True
    return {"node_id": node_id, "status": "completed"}

@click.command()
@click.option('--node-id', required=True, help='ID of the node to mark as completed')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--output', '-o', type=click.Choice(['json', 'table', 'plain']), 
              default='table', help='Output format')
@click.option('--config', type=click.Path(exists=True), help='Configuration file')
@click.pass_context
def mark_node_completed(ctx, node_id: str, verbose: bool, output: str, config: Optional[str]):
    """
    Mark a specified node as completed.
    """
    try:
        if verbose:
            console.print(f"[blue]Running mark_node_completed command for node ID: {node_id}...[/blue]")
        
        config_data = load_config(config)
        
        result_data = mark_node_as_completed(node_id, config_data)
        
        # Output results based on format
        if output == 'json':
            console.print_json(json.dumps(result_data, indent=2))
        elif output == 'table':
            table = Table(title=f"mark_node_completed Results")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="magenta")
            
            for key, value in result_data.items():
                table.add_row(str(key), str(value))
            
            console.print(table)
        else:  # plain
            for key, value in result_data.items():
                console.print(f"{key}: {value}")
        
        if verbose:
            console.print(f"[green]✅ Node '{node_id}' marked as completed successfully[/green]")
            
    except ValueError as ve:
        console.print(f"[red]❌ mark_node_completed failed: {str(ve)}[/red]")
        ctx.exit(1)
    except Exception as e:
        console.print(f"[red]❌ mark_node_completed failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)

# Export command for CLI registration
__all__ = ["mark_node_completed"]