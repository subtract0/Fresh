import click
from typing import Optional
from rich.console import Console
from rich.table import Table
from pathlib import Path
import json
import os

console = Console()

def load_config(config_path: str):
    with open(config_path, 'r') as f:
        return json.load(f)

def validate_config(config):
    required_keys = ['track_name', 'track_data']
    for key in required_keys:
        if key not in config:
            raise ValueError(f"Missing required config key: {key}")

def write_track_data(track_name: str, track_data: dict):
    output_dir = Path("tracks")
    output_dir.mkdir(exist_ok=True)
    track_file = output_dir / f"{track_name}.json"
    with open(track_file, 'w') as f:
        json.dump(track_data, f, indent=2)

@click.command()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--output', '-o', type=click.Choice(['json', 'table', 'plain']), 
              default='table', help='Output format')
@click.option('--config', type=click.Path(exists=True), help='Configuration file')
@click.pass_context
def track_write(ctx, verbose: bool, output: str, config: Optional[str]):
    """
    track_write command.
    Writes track data to a file based on the provided configuration.
    """
    try:
        if verbose:
            console.print(f"[blue]Running track_write command...[/blue]")
        
        if not config:
            raise ValueError("Configuration file must be provided.")
        
        config_data = load_config(config)
        validate_config(config_data)

        track_name = config_data['track_name']
        track_data = config_data['track_data']

        write_track_data(track_name, track_data)

        result_data = {
            "feature": "track_write",
            "status": "success", 
            "message": f"Track data for '{track_name}' written successfully.",
            "config_used": config,
            "verbose": verbose
        }
        
        # Output results based on format
        if output == 'json':
            console.print_json(json.dumps(result_data, indent=2))
        elif output == 'table':
            table = Table(title=f"track_write Results")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="magenta")
            
            for key, value in result_data.items():
                table.add_row(str(key), str(value))
            
            console.print(table)
        else:  # plain
            for key, value in result_data.items():
                console.print(f"{key}: {value}")
        
        if verbose:
            console.print(f"[green]✅ track_write completed successfully[/green]")
            
    except Exception as e:
        console.print(f"[red]❌ track_write failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)

__all__ = ["track_write"]