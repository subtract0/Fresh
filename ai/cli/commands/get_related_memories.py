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

def fetch_related_memories(config, verbose):
    # Simulated logic for fetching related memories
    if verbose:
        console.print(f"[blue]Fetching related memories using config: {config}[/blue]")
    # Here you would implement the actual logic to fetch related memories
    return [
        {"id": 1, "memory": "Memory A related to topic X"},
        {"id": 2, "memory": "Memory B related to topic Y"},
    ]

@click.command()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--output', '-o', type=click.Choice(['json', 'table', 'plain']), 
              default='table', help='Output format')
@click.option('--config', type=click.Path(exists=True), help='Configuration file')
@click.pass_context
def get_related_memories(ctx, verbose: bool, output: str, config: Optional[str]):
    """
    get_related_memories command.
    Fetch and display related memories based on the provided configuration.
    """
    try:
        if verbose:
            console.print(f"[blue]Running get_related_memories command...[/blue]")
        
        config_data = load_config(config) if config else {}
        
        related_memories = fetch_related_memories(config_data, verbose)
        
        result_data = {
            "feature": "get_related_memories",
            "status": "success", 
            "memories": related_memories,
            "config_used": config,
            "verbose": verbose
        }
        
        # Output results based on format
        if output == 'json':
            console.print_json(json.dumps(result_data, indent=2))
        elif output == 'table':
            table = Table(title=f"get_related_memories Results")
            table.add_column("ID", style="cyan")
            table.add_column("Memory", style="magenta")
            
            for memory in related_memories:
                table.add_row(str(memory["id"]), memory["memory"])
            
            console.print(table)
        else:  # plain
            for memory in related_memories:
                console.print(f"ID: {memory['id']}, Memory: {memory['memory']}")
        
        if verbose:
            console.print(f"[green]✅ get_related_memories completed successfully[/green]")
            
    except FileNotFoundError as fnf_error:
        console.print(f"[red]❌ Configuration error: {str(fnf_error)}[/red]")
        ctx.exit(1)
    except Exception as e:
        console.print(f"[red]❌ get_related_memories failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)

# Export command for CLI registration
__all__ = ["get_related_memories"]