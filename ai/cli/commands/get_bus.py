import click
from typing import Optional
from rich.console import Console
from rich.table import Table
from pathlib import Path
import json
import requests

console = Console()

@click.command()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--output', '-o', type=click.Choice(['json', 'table', 'plain']), 
              default='table', help='Output format')
@click.option('--config', type=click.Path(exists=True), help='Configuration file')
@click.pass_context
def get_bus(ctx, verbose: bool, output: Optional[str], config: Optional[str]):
    """
    get_bus command.
    
    Fetches bus information from the configured API endpoint.
    """
    try:
        if verbose:
            console.print(f"[blue]Running get_bus command...[/blue]")
        
        # Load configuration if provided
        api_url = "https://api.example.com/bus"  # Default API URL
        if config:
            with open(config, 'r') as f:
                config_data = json.load(f)
                api_url = config_data.get("api_url", api_url)

        # Fetch bus data from the API
        response = requests.get(api_url)
        response.raise_for_status()  # Raise an error for bad responses
        bus_data = response.json()

        # Prepare result data
        result_data = {
            "feature": "get_bus",
            "status": "success", 
            "data": bus_data,
            "config_used": config,
            "verbose": verbose
        }
        
        # Output results based on format
        if output == 'json':
            console.print_json(json.dumps(result_data, indent=2))
        elif output == 'table':
            table = Table(title=f"get_bus Results")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="magenta")
            
            for key, value in result_data.items():
                if key != "data":  # Skip data for table output
                    table.add_row(str(key), str(value))
            console.print(table)
        else:  # plain
            for key, value in result_data.items():
                if key != "data":  # Skip data for plain output
                    console.print(f"{key}: {value}")
        
        if verbose:
            console.print(f"[green]✅ get_bus completed successfully[/green]")
            
    except requests.exceptions.RequestException as e:
        console.print(f"[red]❌ get_bus failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)
    except json.JSONDecodeError as e:
        console.print(f"[red]❌ Failed to decode JSON: {str(e)}[/red]")
        ctx.exit(1)
    except Exception as e:
        console.print(f"[red]❌ get_bus failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)

__all__ = ["get_bus"]