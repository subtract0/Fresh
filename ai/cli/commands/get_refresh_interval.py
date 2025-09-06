import click
from typing import Optional
from rich.console import Console
from rich.table import Table
from pathlib import Path
import json
import os

console = Console()

def load_config(config_path: str) -> dict:
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    with open(config_path, 'r') as file:
        return json.load(file)

def get_refresh_interval_value(config: dict) -> int:
    return config.get("refresh_interval", 60)  # Default to 60 seconds if not specified

@click.command()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--output', '-o', type=click.Choice(['json', 'table', 'plain']), 
              default='table', help='Output format')
@click.option('--config', type=click.Path(exists=True), help='Configuration file')
@click.pass_context
def get_refresh_interval(ctx, verbose: bool, output: str, config: Optional[str]):
    """
    get_refresh_interval command.
    Retrieves the refresh interval from the configuration file.
    """
    try:
        if verbose:
            console.print(f"[blue]Running get_refresh_interval command...[/blue]")
        
        if config:
            config_data = load_config(config)
            refresh_interval = get_refresh_interval_value(config_data)
        else:
            refresh_interval = 60  # Default value if no config is provided
        
        result_data = {
            "feature": "get_refresh_interval",
            "status": "success", 
            "refresh_interval": refresh_interval,
            "config_used": config,
            "verbose": verbose
        }
        
        # Output results based on format
        if output == 'json':
            console.print_json(json.dumps(result_data, indent=2))
        elif output == 'table':
            table = Table(title=f"get_refresh_interval Results")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="magenta")
            
            for key, value in result_data.items():
                table.add_row(str(key), str(value))
            
            console.print(table)
        else:  # plain
            for key, value in result_data.items():
                console.print(f"{key}: {value}")
        
        if verbose:
            console.print(f"[green]✅ get_refresh_interval completed successfully[/green]")
            
    except FileNotFoundError as fnf_error:
        console.print(f"[red]❌ Error: {str(fnf_error)}[/red]")
        ctx.exit(1)
    except json.JSONDecodeError as json_error:
        console.print(f"[red]❌ JSON decode error: {str(json_error)}[/red]")
        ctx.exit(1)
    except Exception as e:
        console.print(f"[red]❌ get_refresh_interval failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)

# Export command for CLI registration
__all__ = ["get_refresh_interval"]