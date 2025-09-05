import click
from typing import Optional
from rich.console import Console
from rich.table import Table
from pathlib import Path
import json
import os
import requests

console = Console()

@click.command()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--output', '-o', type=click.Choice(['json', 'table', 'plain']), 
              default='table', help='Output format')
@click.option('--config', type=click.Path(exists=True), help='Configuration file')
@click.pass_context
def serve_status_api(ctx, verbose: bool, output: str, config: Optional[str]):
    """
    serve_status_api command.
    Fetches the status of the serve_status_api and displays it in the specified format.
    """
    try:
        if verbose:
            console.print(f"[blue]Running serve_status_api command...[/blue]")
        
        # Load configuration if provided
        api_url = None
        if config:
            with open(config, 'r') as f:
                config_data = json.load(f)
                api_url = config_data.get("api_url")
                if not api_url:
                    raise ValueError("API URL not found in configuration file.")
        else:
            raise ValueError("Configuration file is required.")

        # Fetch the status from the API
        response = requests.get(api_url)
        response.raise_for_status()  # Raise an error for bad responses
        result_data = response.json()

        # Output results based on format
        if output == 'json':
            console.print_json(json.dumps(result_data, indent=2))
        elif output == 'table':
            table = Table(title=f"serve_status_api Results")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="magenta")
            
            for key, value in result_data.items():
                table.add_row(str(key), str(value))
            
            console.print(table)
        else:  # plain
            for key, value in result_data.items():
                console.print(f"{key}: {value}")
        
        if verbose:
            console.print(f"[green]✅ serve_status_api completed successfully[/green]")
            
    except requests.exceptions.RequestException as e:
        console.print(f"[red]❌ serve_status_api failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)
    except ValueError as ve:
        console.print(f"[red]❌ Configuration error: {str(ve)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)
    except Exception as e:
        console.print(f"[red]❌ serve_status_api failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)

# Export command for CLI registration
__all__ = ["serve_status_api"]