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

def get_memory_by_type(memory_type: str, config: dict):
    # Simulated memory retrieval logic based on type
    memory_data = {
        "RAM": {"total": "16GB", "used": "8GB", "free": "8GB"},
        "SSD": {"total": "512GB", "used": "200GB", "free": "312GB"},
        "HDD": {"total": "1TB", "used": "500GB", "free": "500GB"}
    }
    return memory_data.get(memory_type, {"error": "Memory type not found"})

@click.command()
@click.option('--memory-type', '-m', required=True, type=str, help='Type of memory to retrieve (e.g., RAM, SSD, HDD)')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--output', '-o', type=click.Choice(['json', 'table', 'plain']), 
              default='table', help='Output format')
@click.option('--config', type=click.Path(exists=True), help='Configuration file')
@click.pass_context
def getmemorybytype(ctx, memory_type: str, verbose: bool, output: str, config: Optional[str]):
    """
    GetMemoryByType command.
    
    Retrieves memory information based on the specified type.
    """
    try:
        if verbose:
            console.print(f"[blue]Running GetMemoryByType command for type: {memory_type}...[/blue]")
        
        config_data = {}
        if config:
            config_data = load_config(config)

        memory_info = get_memory_by_type(memory_type, config_data)
        
        if "error" in memory_info:
            raise ValueError(memory_info["error"])

        # Output results based on format
        if output == 'json':
            console.print_json(json.dumps(memory_info, indent=2))
        elif output == 'table':
            table = Table(title=f"GetMemoryByType Results for {memory_type}")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="magenta")
            
            for key, value in memory_info.items():
                table.add_row(str(key), str(value))
            
            console.print(table)
        else:  # plain
            for key, value in memory_info.items():
                console.print(f"{key}: {value}")
        
        if verbose:
            console.print(f"[green]✅ GetMemoryByType completed successfully[/green]")
            
    except ValueError as ve:
        console.print(f"[red]❌ GetMemoryByType failed: {str(ve)}[/red]")
        ctx.exit(1)
    except Exception as e:
        console.print(f"[red]❌ GetMemoryByType failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)

# Export command for CLI registration
__all__ = ["getmemorybytype"]