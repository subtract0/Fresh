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

def process_tracked_collection_reference(config: dict):
    # Simulate processing logic
    if 'collection' not in config:
        raise ValueError("Configuration must include 'collection' key.")
    collection = config['collection']
    # Here you would implement the actual logic for processing the collection
    return {"processed_collection": collection, "status": "success"}

@click.command()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--output', '-o', type=click.Choice(['json', 'table', 'plain']), 
              default='table', help='Output format')
@click.option('--config', type=click.Path(exists=True), help='Configuration file')
@click.pass_context
def trackedcollectionreference(ctx, verbose: bool, output: str, config: Optional[str]):
    """
    TrackedCollectionReference command.
    Processes a tracked collection based on the provided configuration.
    """
    try:
        if verbose:
            console.print(f"[blue]Running TrackedCollectionReference command...[/blue]")
        
        if config:
            config_data = load_config(config)
        else:
            raise ValueError("Configuration file must be provided.")

        result_data = process_tracked_collection_reference(config_data)
        
        # Output results based on format
        if output == 'json':
            console.print_json(json.dumps(result_data, indent=2))
        elif output == 'table':
            table = Table(title=f"TrackedCollectionReference Results")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="magenta")
            
            for key, value in result_data.items():
                table.add_row(str(key), str(value))
            
            console.print(table)
        else:  # plain
            for key, value in result_data.items():
                console.print(f"{key}: {value}")
        
        if verbose:
            console.print(f"[green]✅ TrackedCollectionReference completed successfully[/green]")
            
    except FileNotFoundError as fnf_error:
        console.print(f"[red]❌ Error: {str(fnf_error)}[/red]")
        ctx.exit(1)
    except ValueError as val_error:
        console.print(f"[red]❌ Error: {str(val_error)}[/red]")
        ctx.exit(1)
    except Exception as e:
        console.print(f"[red]❌ TrackedCollectionReference failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)

# Export command for CLI registration
__all__ = ["trackedcollectionreference"]