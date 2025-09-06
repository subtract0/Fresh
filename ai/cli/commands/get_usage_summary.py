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

def get_usage_data(config):
    # Simulated data retrieval logic
    return {
        "total_usage": 1500,
        "active_users": 300,
        "feature_usage": {
            "feature_a": 500,
            "feature_b": 1000
        }
    }

@click.command()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--output', '-o', type=click.Choice(['json', 'table', 'plain']), 
              default='table', help='Output format')
@click.option('--config', type=click.Path(exists=True), help='Configuration file')
@click.pass_context
def get_usage_summary(ctx, verbose: bool, output: str, config: Optional[str]):
    """
    get_usage_summary command.
    Generates a summary of usage statistics based on the provided configuration.
    """
    try:
        if verbose:
            console.print(f"[blue]Running get_usage_summary command...[/blue]")
        
        if config is None:
            raise ValueError("Configuration file must be provided.")
        
        config_data = load_config(config)
        
        if verbose:
            console.print(f"[blue]Loaded configuration: {config_data}[/blue]")
        
        usage_data = get_usage_data(config_data)
        
        # Output results based on format
        if output == 'json':
            console.print_json(json.dumps(usage_data, indent=2))
        elif output == 'table':
            table = Table(title=f"Usage Summary Results")
            table.add_column("Metric", style="cyan")
            table.add_column("Value", style="magenta")
            
            for key, value in usage_data.items():
                if isinstance(value, dict):
                    for sub_key, sub_value in value.items():
                        table.add_row(f"{key} - {sub_key}", str(sub_value))
                else:
                    table.add_row(key, str(value))
            
            console.print(table)
        else:  # plain
            for key, value in usage_data.items():
                if isinstance(value, dict):
                    for sub_key, sub_value in value.items():
                        console.print(f"{key} - {sub_key}: {sub_value}")
                else:
                    console.print(f"{key}: {value}")
        
        if verbose:
            console.print(f"[green]✅ get_usage_summary completed successfully[/green]")
            
    except FileNotFoundError:
        console.print(f"[red]❌ Configuration file not found: {config}[/red]")
        ctx.exit(1)
    except json.JSONDecodeError:
        console.print(f"[red]❌ Error decoding JSON from configuration file: {config}[/red]")
        ctx.exit(1)
    except ValueError as ve:
        console.print(f"[red]❌ {str(ve)}[/red]")
        ctx.exit(1)
    except Exception as e:
        console.print(f"[red]❌ get_usage_summary failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)

__all__ = ["get_usage_summary"]