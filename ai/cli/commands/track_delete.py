import click
from typing import Optional
from rich.console import Console
from rich.table import Table
from pathlib import Path
import json
import os

console = Console()

def delete_track(track_id: str, config_path: Optional[str]) -> dict:
    if not track_id:
        raise ValueError("Track ID must be provided.")
    
    if config_path and not Path(config_path).exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")

    # Simulate deletion logic
    # In a real implementation, this would interact with a database or file system
    # Here we just simulate success or failure based on the track_id
    if track_id == "invalid":
        raise Exception("Failed to delete track: Invalid track ID.")
    
    return {"track_id": track_id, "status": "deleted"}

@click.command()
@click.option('--track-id', '-t', required=True, help='ID of the track to delete')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--output', '-o', type=click.Choice(['json', 'table', 'plain']), 
              default='table', help='Output format')
@click.option('--config', type=click.Path(exists=True), help='Configuration file')
@click.pass_context
def track_delete(ctx, track_id: str, verbose: bool, output: str, config: Optional[str]):
    """
    Delete a track by its ID.
    """
    try:
        if verbose:
            console.print(f"[blue]Running track_delete command for track ID: {track_id}...[/blue]")
        
        result = delete_track(track_id, config)
        
        # Output results based on format
        if output == 'json':
            console.print_json(json.dumps(result, indent=2))
        elif output == 'table':
            table = Table(title=f"track_delete Results")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="magenta")
            
            for key, value in result.items():
                table.add_row(str(key), str(value))
            
            console.print(table)
        else:  # plain
            for key, value in result.items():
                console.print(f"{key}: {value}")
        
        if verbose:
            console.print(f"[green]✅ track_delete completed successfully[/green]")
            
    except Exception as e:
        console.print(f"[red]❌ track_delete failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)

# Export command for CLI registration
__all__ = ["track_delete"]