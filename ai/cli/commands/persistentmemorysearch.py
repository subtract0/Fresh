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

def perform_search(query: str, config: dict):
    # Placeholder for actual search logic
    # This should interact with a persistent memory store or database
    if not query:
        raise ValueError("Search query cannot be empty.")
    
    # Simulated search result
    return {
        "query": query,
        "results": ["result1", "result2", "result3"],
        "config": config
    }

@click.command()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--output', '-o', type=click.Choice(['json', 'table', 'plain']), 
              default='table', help='Output format')
@click.option('--config', type=click.Path(exists=True), help='Configuration file', required=True)
@click.argument('query', type=str)
@click.pass_context
def persistentmemorysearch(ctx, verbose: bool, output: str, config: Optional[str], query: str):
    """
    PersistentMemorySearch command.
    
    This command searches for data in persistent memory based on the provided query.
    """
    try:
        if verbose:
            console.print(f"[blue]Running PersistentMemorySearch command...[/blue]")
        
        config_data = load_config(config)
        
        if verbose:
            console.print(f"[yellow]Using configuration: {config_data}[/yellow]")
        
        search_results = perform_search(query, config_data)
        
        # Output results based on format
        if output == 'json':
            console.print_json(json.dumps(search_results, indent=2))
        elif output == 'table':
            table = Table(title=f"PersistentMemorySearch Results")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="magenta")
            
            for key, value in search_results.items():
                table.add_row(str(key), str(value))
            
            console.print(table)
        else:  # plain
            for key, value in search_results.items():
                console.print(f"{key}: {value}")
        
        if verbose:
            console.print(f"[green]✅ PersistentMemorySearch completed successfully[/green]")
            
    except FileNotFoundError as fnf_error:
        console.print(f"[red]❌ Error: {str(fnf_error)}[/red]")
        ctx.exit(1)
    except ValueError as val_error:
        console.print(f"[red]❌ Error: {str(val_error)}[/red]")
        ctx.exit(1)
    except Exception as e:
        console.print(f"[red]❌ PersistentMemorySearch failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)

# Export command for CLI registration
__all__ = ["persistentmemorysearch"]