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

def check_status(config):
    # Simulated status check logic
    return {
        "service": "example_service",
        "status": "running",
        "uptime": "24 hours",
        "last_checked": "2023-10-01T12:00:00Z"
    }

@click.command()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--output', '-o', type=click.Choice(['json', 'table', 'plain']), 
              default='table', help='Output format')
@click.option('--config', type=click.Path(exists=True), help='Configuration file')
@click.pass_context
def status(ctx, verbose: bool, output: str, config: Optional[str]):
    """
    status command.
    Checks the status of the application or service.
    """
    try:
        if verbose:
            console.print(f"[blue]Running status command...[/blue]")
        
        config_data = {}
        if config:
            config_data = load_config(config)
            if verbose:
                console.print(f"[yellow]Loaded configuration from {config}[/yellow]")
        
        status_data = check_status(config_data)
        
        # Output results based on format
        if output == 'json':
            console.print_json(json.dumps(status_data, indent=2))
        elif output == 'table':
            table = Table(title=f"Status Results")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="magenta")
            
            for key, value in status_data.items():
                table.add_row(str(key), str(value))
            
            console.print(table)
        else:  # plain
            for key, value in status_data.items():
                console.print(f"{key}: {value}")
        
        if verbose:
            console.print(f"[green]✅ Status completed successfully[/green]")
            
    except FileNotFoundError:
        console.print(f"[red]❌ Configuration file not found: {config}[/red]")
        ctx.exit(1)
    except json.JSONDecodeError:
        console.print(f"[red]❌ Error decoding JSON from configuration file: {config}[/red]")
        ctx.exit(1)
    except Exception as e:
        console.print(f"[red]❌ Status command failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)

# Export command for CLI registration
__all__ = ["status"]