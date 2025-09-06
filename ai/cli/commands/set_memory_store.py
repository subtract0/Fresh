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

def save_memory_store(data: dict, memory_store_path: str):
    with open(memory_store_path, 'w') as file:
        json.dump(data, file, indent=2)

@click.command()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--output', '-o', type=click.Choice(['json', 'table', 'plain']), 
              default='table', help='Output format')
@click.option('--config', type=click.Path(exists=True), help='Configuration file')
@click.option('--memory-store', type=click.Path(), required=True, help='Path to memory store file')
@click.pass_context
def set_memory_store(ctx, verbose: bool, output: str, config: Optional[str], memory_store: str):
    """
    set_memory_store command.
    
    This command sets the memory store with the provided configuration.
    """
    try:
        if verbose:
            console.print(f"[blue]Running set_memory_store command...[/blue]")
        
        # Load configuration if provided
        config_data = {}
        if config:
            config_data = load_config(config)
            if verbose:
                console.print(f"[yellow]Loaded configuration from {config}[/yellow]")

        # Validate memory store path
        memory_store_path = Path(memory_store)
        if not memory_store_path.parent.exists():
            raise FileNotFoundError(f"Directory for memory store does not exist: {memory_store_path.parent}")

        # Prepare data to save
        result_data = {
            "feature": "set_memory_store",
            "status": "success", 
            "message": "Memory store updated successfully",
            "config_used": config_data,
            "verbose": verbose
        }

        # Save to memory store
        save_memory_store(result_data, memory_store_path)

        # Output results based on format
        if output == 'json':
            console.print_json(json.dumps(result_data, indent=2))
        elif output == 'table':
            table = Table(title=f"set_memory_store Results")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="magenta")
            
            for key, value in result_data.items():
                table.add_row(str(key), str(value))
            
            console.print(table)
        else:  # plain
            for key, value in result_data.items():
                console.print(f"{key}: {value}")
        
        if verbose:
            console.print(f"[green]✅ set_memory_store completed successfully[/green]")
            
    except Exception as e:
        console.print(f"[red]❌ set_memory_store failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)

# Export command for CLI registration
__all__ = ["set_memory_store"]