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
    required_keys = ['api_endpoint', 'api_key']
    for key in required_keys:
        if key not in config:
            raise ValueError(f"Missing required config key: {key}")

def fetch_data_from_api(api_endpoint: str, api_key: str):
    import requests
    headers = {'Authorization': f'Bearer {api_key}'}
    response = requests.get(api_endpoint, headers=headers)
    response.raise_for_status()
    return response.json()

@click.command()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--output', '-o', type=click.Choice(['json', 'table', 'plain']), 
              default='table', help='Output format')
@click.option('--config', type=click.Path(exists=True), help='Configuration file')
@click.pass_context
def handle_export_api(ctx, verbose: bool, output: str, config: Optional[str]):
    """
    handle_export_api command.
    Fetch data from an external API and display it in the specified format.
    """
    try:
        if verbose:
            console.print(f"[blue]Running handle_export_api command...[/blue]")
        
        if not config:
            raise ValueError("Configuration file must be provided.")
        
        config_data = load_config(config)
        validate_config(config_data)

        api_endpoint = config_data['api_endpoint']
        api_key = config_data['api_key']
        
        result_data = fetch_data_from_api(api_endpoint, api_key)

        # Output results based on format
        if output == 'json':
            console.print_json(json.dumps(result_data, indent=2))
        elif output == 'table':
            table = Table(title=f"handle_export_api Results")
            table.add_column("Key", style="cyan")
            table.add_column("Value", style="magenta")
            
            for key, value in result_data.items():
                table.add_row(str(key), str(value))
            
            console.print(table)
        else:  # plain
            for key, value in result_data.items():
                console.print(f"{key}: {value}")
        
        if verbose:
            console.print(f"[green]✅ handle_export_api completed successfully[/green]")
            
    except Exception as e:
        console.print(f"[red]❌ handle_export_api failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)

__all__ = ["handle_export_api"]