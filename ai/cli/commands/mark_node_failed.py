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

def mark_node_failed_logic(node_id: str, config: dict):
    # Simulate marking a node as failed
    if node_id not in config['nodes']:
        raise ValueError(f"Node ID {node_id} not found in configuration.")
    
    config['nodes'][node_id]['status'] = 'failed'
    return {"node_id": node_id, "status": "failed"}

@click.command()
@click.option('--node-id', required=True, help='ID of the node to mark as failed')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--output', '-o', type=click.Choice(['json', 'table', 'plain']), 
              default='table', help='Output format')
@click.option('--config', type=click.Path(exists=True), help='Configuration file')
@click.pass_context
def mark_node_failed(ctx, node_id: str, verbose: bool, output: str, config: Optional[str]):
    """
    Mark a specified node as failed in the configuration.
    """
    try:
        if verbose:
            console.print(f"[blue]Running mark_node_failed command for node ID: {node_id}...[/blue]")
        
        if config is None:
            raise ValueError("Configuration file must be provided.")
        
        config_data = load_config(config)
        
        result_data = mark_node_failed_logic(node_id, config_data)
        
        # Output results based on format
        if output == 'json':
            console.print_json(json.dumps(result_data, indent=2))
        elif output == 'table':
            table = Table(title=f"mark_node_failed Results")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="magenta")
            
            for key, value in result_data.items():
                table.add_row(str(key), str(value))
            
            console.print(table)
        else:  # plain
            for key, value in result_data.items():
                console.print(f"{key}: {value}")
        
        if verbose:
            console.print(f"[green]✅ mark_node_failed completed successfully for node ID: {node_id}[/green]")
            
    except Exception as e:
        console.print(f"[red]❌ mark_node_failed failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)

__all__ = ["mark_node_failed"]