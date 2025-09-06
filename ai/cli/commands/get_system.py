import click
from typing import Optional
from rich.console import Console
from rich.table import Table
from pathlib import Path
import json
import os
import platform
import socket

console = Console()


@click.command()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--output', '-o', type=click.Choice(['json', 'table', 'plain']), 
              default='table', help='Output format')
@click.option('--config', type=click.Path(exists=True), help='Configuration file')
@click.pass_context
def get_system(ctx, verbose: bool, output: str, config: Optional[str]):
    """
    get_system command.
    Retrieves system information such as OS, hostname, and more.
    """
    try:
        if verbose:
            console.print(f"[blue]Running get_system command...[/blue]")
        
        # Load configuration if provided
        config_data = {}
        if config:
            with open(config, 'r') as f:
                config_data = json.load(f)
        
        # Gather system information
        system_info = {
            "OS": platform.system(),
            "OS Version": platform.version(),
            "Architecture": platform.architecture()[0],
            "Hostname": socket.gethostname(),
            "IP Address": socket.gethostbyname(socket.gethostname()),
            "Config Used": config_data if config_data else "None",
            "Verbose": verbose
        }
        
        # Output results based on format
        if output == 'json':
            console.print_json(json.dumps(system_info, indent=2))
        elif output == 'table':
            table = Table(title=f"get_system Results")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="magenta")
            
            for key, value in system_info.items():
                table.add_row(str(key), str(value))
            
            console.print(table)
        else:  # plain
            for key, value in system_info.items():
                console.print(f"{key}: {value}")
        
        if verbose:
            console.print(f"[green]✅ get_system completed successfully[/green]")
            
    except FileNotFoundError as fnf_error:
        console.print(f"[red]❌ Configuration file not found: {str(fnf_error)}[/red]")
        ctx.exit(1)
    except json.JSONDecodeError as json_error:
        console.print(f"[red]❌ Error decoding JSON from configuration file: {str(json_error)}[/red]")
        ctx.exit(1)
    except Exception as e:
        console.print(f"[red]❌ get_system failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)


# Export command for CLI registration
__all__ = ["get_system"]