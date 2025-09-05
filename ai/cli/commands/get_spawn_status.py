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

def check_spawn_status(config):
    # Simulated logic for checking spawn status
    # In a real implementation, this would interface with the actual system
    return {
        "spawn_id": config.get("spawn_id", "unknown"),
        "status": "active",
        "details": "Spawn is currently active and operational."
    }

@click.command()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--output', '-o', type=click.Choice(['json', 'table', 'plain']), 
              default='table', help='Output format')
@click.option('--config', type=click.Path(exists=True), help='Configuration file', required=True)
@click.pass_context
def get_spawn_status(ctx, verbose: bool, output: str, config: Optional[str]):
    """
    get_spawn_status command.
    Retrieves the current status of the spawn based on the provided configuration.
    """
    try:
        if verbose:
            console.print(f"[blue]Running get_spawn_status command...[/blue]")
        
        # Load configuration
        config_data = load_config(config)
        
        # Validate required fields in config
        if 'spawn_id' not in config_data:
            raise ValueError("Configuration must include 'spawn_id'.")

        # Get spawn status
        result_data = check_spawn_status(config_data)
        
        # Output results based on format
        if output == 'json':
            console.print_json(json.dumps(result_data, indent=2))
        elif output == 'table':
            table = Table(title=f"get_spawn_status Results")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="magenta")
            
            for key, value in result_data.items():
                table.add_row(str(key), str(value))
            
            console.print(table)
        else:  # plain
            for key, value in result_data.items():
                console.print(f"{key}: {value}")
        
        if verbose:
            console.print(f"[green]✅ get_spawn_status completed successfully[/green]")
            
    except FileNotFoundError:
        console.print(f"[red]❌ Configuration file not found: {config}[/red]")
        ctx.exit(1)
    except json.JSONDecodeError:
        console.print(f"[red]❌ Error decoding JSON from configuration file: {config}[/red]")
        ctx.exit(1)
    except ValueError as ve:
        console.print(f"[red]❌ Configuration error: {str(ve)}[/red]")
        ctx.exit(1)
    except Exception as e:
        console.print(f"[red]❌ get_spawn_status failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)

# Export command for CLI registration
__all__ = ["get_spawn_status"]