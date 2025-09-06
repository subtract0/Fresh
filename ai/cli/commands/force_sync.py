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

def sync_files(source: str, destination: str):
    if not os.path.exists(source):
        raise FileNotFoundError(f"Source path '{source}' does not exist.")
    if not os.path.exists(destination):
        os.makedirs(destination)

    for item in os.listdir(source):
        s = os.path.join(source, item)
        d = os.path.join(destination, item)
        if os.path.isdir(s):
            sync_files(s, d)
        else:
            if os.path.exists(d):
                os.remove(d)
            os.link(s, d)

@click.command()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--output', '-o', type=click.Choice(['json', 'table', 'plain']), 
              default='table', help='Output format')
@click.option('--config', type=click.Path(exists=True), help='Configuration file')
@click.pass_context
def force_sync(ctx, verbose: bool, output: str, config: Optional[str]):
    """
    force_sync command to synchronize files from a source to a destination.
    """
    try:
        if verbose:
            console.print(f"[blue]Running force_sync command...[/blue]")
        
        if not config:
            raise ValueError("Configuration file must be provided.")

        config_data = load_config(config)
        source = config_data.get("source")
        destination = config_data.get("destination")

        if not source or not destination:
            raise ValueError("Source and destination must be specified in the configuration.")

        sync_files(source, destination)

        result_data = {
            "feature": "force_sync",
            "status": "success", 
            "message": "Files synchronized successfully.",
            "config_used": config,
            "verbose": verbose
        }
        
        # Output results based on format
        if output == 'json':
            console.print_json(json.dumps(result_data, indent=2))
        elif output == 'table':
            table = Table(title=f"force_sync Results")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="magenta")
            
            for key, value in result_data.items():
                table.add_row(str(key), str(value))
            
            console.print(table)
        else:  # plain
            for key, value in result_data.items():
                console.print(f"{key}: {value}")
        
        if verbose:
            console.print(f"[green]✅ force_sync completed successfully[/green]")
            
    except Exception as e:
        console.print(f"[red]❌ force_sync failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)

__all__ = ["force_sync"]