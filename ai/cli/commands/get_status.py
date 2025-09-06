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
    return {}

def check_service_status():
    # Simulate checking service status
    return {
        "service_1": "running",
        "service_2": "stopped",
        "service_3": "running"
    }

@click.command()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--output', '-o', type=click.Choice(['json', 'table', 'plain']), 
              default='table', help='Output format')
@click.option('--config', type=click.Path(exists=True), help='Configuration file')
@click.pass_context
def get_status(ctx, verbose: bool, output: str, config: Optional[str]):
    """
    get_status command.
    Retrieves the status of services and outputs in the specified format.
    """
    try:
        if verbose:
            console.print(f"[blue]Running get_status command...[/blue]")
        
        config_data = load_config(config)
        service_status = check_service_status()
        
        result_data = {
            "feature": "get_status",
            "status": "success", 
            "services": service_status,
            "config_used": config_data,
            "verbose": verbose
        }
        
        # Output results based on format
        if output == 'json':
            console.print_json(json.dumps(result_data, indent=2))
        elif output == 'table':
            table = Table(title=f"get_status Results")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="magenta")
            
            for key, value in result_data.items():
                if isinstance(value, dict):
                    for sub_key, sub_value in value.items():
                        table.add_row(f"{key}.{sub_key}", str(sub_value))
                else:
                    table.add_row(str(key), str(value))
            
            console.print(table)
        else:  # plain
            for key, value in result_data.items():
                if isinstance(value, dict):
                    for sub_key, sub_value in value.items():
                        console.print(f"{key}.{sub_key}: {sub_value}")
                else:
                    console.print(f"{key}: {value}")
        
        if verbose:
            console.print(f"[green]✅ get_status completed successfully[/green]")
            
    except FileNotFoundError as fnf_error:
        console.print(f"[red]❌ Configuration file not found: {str(fnf_error)}[/red]")
        ctx.exit(1)
    except json.JSONDecodeError as json_error:
        console.print(f"[red]❌ Error parsing configuration file: {str(json_error)}[/red]")
        ctx.exit(1)
    except Exception as e:
        console.print(f"[red]❌ get_status failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)

__all__ = ["get_status"]