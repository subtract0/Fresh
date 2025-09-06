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

def validate_config(config):
    required_keys = ['api_key', 'endpoint']
    for key in required_keys:
        if key not in config:
            raise ValueError(f"Missing required config key: {key}")

def perform_memory_sync(config):
    # Simulate a memory sync operation
    # In a real implementation, this would interact with an API or database
    return {
        "synced_items": 42,
        "status": "success",
        "message": "Memory sync completed successfully"
    }

@click.command()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--output', '-o', type=click.Choice(['json', 'table', 'plain']), 
              default='table', help='Output format')
@click.option('--config', type=click.Path(exists=True), help='Configuration file')
@click.pass_context
def memorysync(ctx, verbose: bool, output: str, config: Optional[str]):
    """
    MemorySync command.
    Synchronizes memory data with a specified endpoint.
    """
    try:
        if verbose:
            console.print(f"[blue]Running MemorySync command...[/blue]")
        
        if not config:
            raise ValueError("Configuration file must be provided.")
        
        config_data = load_config(config)
        validate_config(config_data)

        result_data = perform_memory_sync(config_data)
        
        # Output results based on format
        if output == 'json':
            console.print_json(json.dumps(result_data, indent=2))
        elif output == 'table':
            table = Table(title=f"MemorySync Results")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="magenta")
            
            for key, value in result_data.items():
                table.add_row(str(key), str(value))
            
            console.print(table)
        else:  # plain
            for key, value in result_data.items():
                console.print(f"{key}: {value}")
        
        if verbose:
            console.print(f"[green]✅ MemorySync completed successfully[/green]")
            
    except Exception as e:
        console.print(f"[red]❌ MemorySync failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)

# Export command for CLI registration
__all__ = ["memorysync"]