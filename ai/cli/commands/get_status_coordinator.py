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

def get_status():
    # Simulate fetching status from a service or database
    return {
        "service": "example_service",
        "status": "running",
        "uptime": "24 days",
        "last_checked": "2023-10-01T12:00:00Z"
    }

@click.command()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--output', '-o', type=click.Choice(['json', 'table', 'plain']), 
              default='table', help='Output format')
@click.option('--config', type=click.Path(exists=True), help='Configuration file')
@click.pass_context
def get_status_coordinator(ctx, verbose: bool, output: str, config: Optional[str]):
    """
    get_status_coordinator command.
    Fetches the status of the coordinator service and displays it.
    """
    try:
        if verbose:
            console.print(f"[blue]Running get_status_coordinator command...[/blue]")
        
        config_data = load_config(config) if config else {}
        
        status_data = get_status()
        result_data = {
            "feature": "get_status_coordinator",
            "status": status_data["status"],
            "service": status_data["service"],
            "uptime": status_data["uptime"],
            "last_checked": status_data["last_checked"],
            "config_used": config_data,
            "verbose": verbose
        }
        
        # Output results based on format
        if output == 'json':
            console.print_json(json.dumps(result_data, indent=2))
        elif output == 'table':
            table = Table(title=f"get_status_coordinator Results")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="magenta")
            
            for key, value in result_data.items():
                table.add_row(str(key), str(value))
            
            console.print(table)
        else:  # plain
            for key, value in result_data.items():
                console.print(f"{key}: {value}")
        
        if verbose:
            console.print(f"[green]✅ get_status_coordinator completed successfully[/green]")
            
    except FileNotFoundError as fnf_error:
        console.print(f"[red]❌ {str(fnf_error)}[/red]")
        ctx.exit(1)
    except Exception as e:
        console.print(f"[red]❌ get_status_coordinator failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)

# Export command for CLI registration
__all__ = ["get_status_coordinator"]