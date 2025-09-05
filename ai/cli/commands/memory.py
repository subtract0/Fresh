import click
from typing import Optional
from rich.console import Console
from rich.table import Table
from pathlib import Path
import json
import os

console = Console()

MEMORY_FILE = Path.home() / '.memory.json'

def load_memory():
    if MEMORY_FILE.exists():
        with open(MEMORY_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_memory(data):
    with open(MEMORY_FILE, 'w') as f:
        json.dump(data, f, indent=2)

@click.command()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--output', '-o', type=click.Choice(['json', 'table', 'plain']), 
              default='table', help='Output format')
@click.option('--config', type=click.Path(exists=True), help='Configuration file')
@click.pass_context
def memory(ctx, verbose: bool, output: str, config: Optional[str]):
    """
    memory command to manage persistent memory storage.
    """
    try:
        if verbose:
            console.print(f"[blue]Running memory command...[/blue]")
        
        memory_data = load_memory()
        
        if not memory_data:
            result_data = {
                "feature": "memory",
                "status": "empty",
                "message": "No memory data found.",
                "config_used": config,
                "verbose": verbose
            }
        else:
            result_data = {
                "feature": "memory",
                "status": "loaded",
                "data": memory_data,
                "config_used": config,
                "verbose": verbose
            }
        
        # Output results based on format
        if output == 'json':
            console.print_json(json.dumps(result_data, indent=2))
        elif output == 'table':
            table = Table(title=f"Memory Results")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="magenta")
            
            for key, value in result_data.items():
                if isinstance(value, dict):
                    value = json.dumps(value, indent=2)
                table.add_row(str(key), str(value))
            
            console.print(table)
        else:  # plain
            for key, value in result_data.items():
                if isinstance(value, dict):
                    value = json.dumps(value, indent=2)
                console.print(f"{key}: {value}")
        
        if verbose:
            console.print(f"[green]✅ memory command completed successfully[/green]")
            
    except FileNotFoundError as fnf_error:
        console.print(f"[red]❌ memory failed: Configuration file not found: {str(fnf_error)}[/red]")
        ctx.exit(1)
    except json.JSONDecodeError as json_error:
        console.print(f"[red]❌ memory failed: Error decoding JSON: {str(json_error)}[/red]")
        ctx.exit(1)
    except Exception as e:
        console.print(f"[red]❌ memory failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)

__all__ = ["memory"]