import click
from typing import Optional
from rich.console import Console
from rich.table import Table
from pathlib import Path
import json
import requests

console = Console()

@click.command()
@click.option('--id', '-i', required=True, type=str, help='ID of the item to retrieve')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--output', '-o', type=click.Choice(['json', 'table', 'plain']), 
              default='table', help='Output format')
@click.option('--config', type=click.Path(exists=True), help='Configuration file')
@click.pass_context
def get_by_id(ctx, id: str, verbose: bool, output: str, config: Optional[str]):
    """
    Retrieve an item by its ID.
    """
    try:
        if verbose:
            console.print(f"[blue]Running get_by_id command for ID: {id}...[/blue]")
        
        # Load configuration if provided
        api_url = "http://example.com/api/items"  # Replace with actual API URL
        if config:
            with open(config, 'r') as f:
                config_data = json.load(f)
                api_url = config_data.get("api_url", api_url)

        # Make API request to get the item by ID
        response = requests.get(f"{api_url}/{id}")
        response.raise_for_status()  # Raise an error for bad responses

        result_data = response.json()

        # Output results based on format
        if output == 'json':
            console.print_json(json.dumps(result_data, indent=2))
        elif output == 'table':
            table = Table(title=f"get_by_id Results for ID: {id}")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="magenta")
            
            for key, value in result_data.items():
                table.add_row(str(key), str(value))
            
            console.print(table)
        else:  # plain
            for key, value in result_data.items():
                console.print(f"{key}: {value}")
        
        if verbose:
            console.print(f"[green]✅ get_by_id completed successfully[/green]")
            
    except requests.HTTPError as http_err:
        console.print(f"[red]❌ HTTP error occurred: {http_err}[/red]")
        ctx.exit(1)
    except json.JSONDecodeError as json_err:
        console.print(f"[red]❌ JSON decode error: {json_err}[/red]")
        ctx.exit(1)
    except Exception as e:
        console.print(f"[red]❌ get_by_id failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)

# Export command for CLI registration
__all__ = ["get_by_id"]