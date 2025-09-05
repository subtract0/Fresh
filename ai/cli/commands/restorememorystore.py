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

def restore_memory_store(config):
    # Simulate restoring memory store logic
    if 'memory_store_path' not in config:
        raise ValueError("Configuration must include 'memory_store_path'")
    
    memory_store_path = config['memory_store_path']
    
    if not os.path.exists(memory_store_path):
        raise FileNotFoundError(f"Memory store path '{memory_store_path}' does not exist.")
    
    # Simulate loading data from memory store
    with open(memory_store_path, 'r') as file:
        data = json.load(file)
    
    return data

@click.command()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--output', '-o', type=click.Choice(['json', 'table', 'plain']), 
              default='table', help='Output format')
@click.option('--config', type=click.Path(exists=True), help='Configuration file', required=True)
@click.pass_context
def restorememorystore(ctx, verbose: bool, output: str, config: Optional[str]):
    """
    RestoreMemoryStore command.
    Restores the memory store from the specified configuration.
    """
    try:
        if verbose:
            console.print(f"[blue]Running RestoreMemoryStore command...[/blue]")
        
        config_data = load_config(config)
        restored_data = restore_memory_store(config_data)
        
        result_data = {
            "feature": "RestoreMemoryStore",
            "status": "success", 
            "message": "Memory store restored successfully",
            "data": restored_data,
            "config_used": config,
            "verbose": verbose
        }
        
        # Output results based on format
        if output == 'json':
            console.print_json(json.dumps(result_data, indent=2))
        elif output == 'table':
            table = Table(title=f"RestoreMemoryStore Results")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="magenta")
            
            for key, value in result_data.items():
                table.add_row(str(key), str(value))
            
            console.print(table)
        else:  # plain
            for key, value in result_data.items():
                console.print(f"{key}: {value}")
        
        if verbose:
            console.print(f"[green]✅ RestoreMemoryStore completed successfully[/green]")
            
    except Exception as e:
        console.print(f"[red]❌ RestoreMemoryStore failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)

__all__ = ["restorememorystore"]