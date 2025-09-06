import click
from typing import Optional
from rich.console import Console
from rich.table import Table
from pathlib import Path
import json

console = Console()

def load_memory_store(config_path: str):
    try:
        with open(config_path, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    except json.JSONDecodeError:
        raise ValueError(f"Error decoding JSON from the configuration file: {config_path}")

@click.command()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--output', '-o', type=click.Choice(['json', 'table', 'plain']), 
              default='table', help='Output format')
@click.option('--config', type=click.Path(exists=True), help='Configuration file')
@click.pass_context
def get_memory_store(ctx, verbose: bool, output: str, config: Optional[str]):
    """
    get_memory_store command.
    Retrieves data from the memory store based on the provided configuration.
    """
    try:
        if verbose:
            console.print(f"[blue]Running get_memory_store command...[/blue]")
        
        if not config:
            raise ValueError("Configuration file must be provided.")
        
        memory_store_data = load_memory_store(config)
        
        # Output results based on format
        if output == 'json':
            console.print_json(json.dumps(memory_store_data, indent=2))
        elif output == 'table':
            table = Table(title=f"get_memory_store Results")
            table.add_column("Key", style="cyan")
            table.add_column("Value", style="magenta")
            
            for key, value in memory_store_data.items():
                table.add_row(str(key), str(value))
            
            console.print(table)
        else:  # plain
            for key, value in memory_store_data.items():
                console.print(f"{key}: {value}")
        
        if verbose:
            console.print(f"[green]✅ get_memory_store completed successfully[/green]")
            
    except Exception as e:
        console.print(f"[red]❌ get_memory_store failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)

# Export command for CLI registration
__all__ = ["get_memory_store"]