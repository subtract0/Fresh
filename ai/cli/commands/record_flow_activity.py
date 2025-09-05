import click
from typing import Optional
from rich.console import Console
from rich.table import Table
from pathlib import Path
import json
import os

console = Console()

def load_config(config_path: str):
    if config_path and Path(config_path).exists():
        with open(config_path, 'r') as f:
            return json.load(f)
    else:
        raise FileNotFoundError(f"Configuration file not found: {config_path}")

def validate_config(config):
    required_keys = ['api_endpoint', 'api_key']
    for key in required_keys:
        if key not in config:
            raise ValueError(f"Missing required configuration key: {key}")

def record_activity_to_api(activity_data, api_endpoint, api_key):
    import requests
    headers = {'Authorization': f'Bearer {api_key}', 'Content-Type': 'application/json'}
    response = requests.post(api_endpoint, headers=headers, json=activity_data)
    response.raise_for_status()
    return response.json()

@click.command()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--output', '-o', type=click.Choice(['json', 'table', 'plain']), 
              default='table', help='Output format')
@click.option('--config', type=click.Path(exists=True), help='Configuration file')
@click.pass_context
def record_flow_activity(ctx, verbose: bool, output: str, config: Optional[str]):
    """
    record_flow_activity command.
    Records flow activity to an external service.
    """
    try:
        if verbose:
            console.print(f"[blue]Running record_flow_activity command...[/blue]")
        
        config_data = load_config(config)
        validate_config(config_data)

        activity_data = {
            "feature": "record_flow_activity",
            "status": "success",
            "message": "Recording flow activity",
            "config_used": config,
            "verbose": verbose
        }

        api_response = record_activity_to_api(activity_data, config_data['api_endpoint'], config_data['api_key'])

        result_data = {
            "feature": "record_flow_activity",
            "status": "success",
            "api_response": api_response,
            "config_used": config,
            "verbose": verbose
        }
        
        if output == 'json':
            console.print_json(json.dumps(result_data, indent=2))
        elif output == 'table':
            table = Table(title=f"record_flow_activity Results")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="magenta")
            
            for key, value in result_data.items():
                table.add_row(str(key), str(value))
            
            console.print(table)
        else:  # plain
            for key, value in result_data.items():
                console.print(f"{key}: {value}")
        
        if verbose:
            console.print(f"[green]✅ record_flow_activity completed successfully[/green]")
            
    except FileNotFoundError as fnf_error:
        console.print(f"[red]❌ record_flow_activity failed: {str(fnf_error)}[/red]")
        ctx.exit(1)
    except ValueError as val_error:
        console.print(f"[red]❌ record_flow_activity failed: {str(val_error)}[/red]")
        ctx.exit(1)
    except Exception as e:
        console.print(f"[red]❌ record_flow_activity failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)

__all__ = ["record_flow_activity"]