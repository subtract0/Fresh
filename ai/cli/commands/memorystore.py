import click
from typing import Optional
from rich.console import Console
from rich.table import Table
from pathlib import Path
import json
import os

console = Console()

def load_config(config_path: str):
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    with open(config_path, 'r') as file:
        return json.load(file)

def save_data_to_memory(data: dict, memory_store_path: str):
    with open(memory_store_path, 'w') as file:
        json.dump(data, file)

def load_data_from_memory(memory_store_path: str):
    if not os.path.exists(memory_store_path):
        return {}
    with open(memory_store_path, 'r') as file:
        return json.load(file)

@click.command()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--output', '-o', type=click.Choice(['json', 'table', 'plain']), 
              default='table', help='Output format')
@click.option('--config', type=click.Path(exists=True), help='Configuration file')
@click.option('--memory-store', type=click.Path(), default='memory_store.json', help='Memory store file path')
@click.pass_context
def memorystore(ctx, verbose: bool, output: str, config: Optional[str], memory_store: str):
    """
    MemoryStore command to manage memory storage.
    """
    try:
        if verbose:
            console.print(f"[blue]Running MemoryStore command...[/blue]")
        
        config_data = load_config(config) if config else {}
        memory_data = load_data_from_memory(memory_store)

        if verbose:
            console.print(f"[yellow]Loaded configuration: {config_data}[/yellow]")
            console.print(f"[yellow]Loaded memory data: {memory_data}[/yellow]")

        # Example operation: Add a new entry to memory
        new_entry = {"example_key": "example_value"}
        memory_data.update(new_entry)
        save_data_to_memory(memory_data, memory_store)

        result_data = {
            "feature": "MemoryStore",
            "status": "success", 
            "message": "MemoryStore functionality implemented",
            "config_used": config_data,
            "memory_data": memory_data,
            "verbose": verbose
        }
        
        # Output results based on format
        if output == 'json':
            console.print_json(json.dumps(result_data, indent=2))
        elif output == 'table':
            table = Table(title=f"MemoryStore Results")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="magenta")
            
            for key, value in result_data.items():
                table.add_row(str(key), str(value))
            
            console.print(table)
        else:  # plain
            for key, value in result_data.items():
                console.print(f"{key}: {value}")
        
        if verbose:
            console.print(f"[green]✅ MemoryStore completed successfully[/green]")
            
    except FileNotFoundError as fnf_error:
        console.print(f"[red]❌ MemoryStore failed: {str(fnf_error)}[/red]")
        ctx.exit(1)
    except json.JSONDecodeError as json_error:
        console.print(f"[red]❌ JSON error: {str(json_error)}[/red]")
        ctx.exit(1)
    except Exception as e:
        console.print(f"[red]❌ MemoryStore failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)

# Export command for CLI registration
__all__ = ["memorystore"]