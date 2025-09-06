import click
from typing import Optional
from rich.console import Console
from rich.table import Table
from pathlib import Path
import json
import yaml

console = Console()

def load_config(config_path: str):
    with open(config_path, 'r') as file:
        return yaml.safe_load(file)

def fetch_production_data(config):
    # Simulated data fetching logic
    if 'production_data' not in config:
        raise ValueError("Configuration must include 'production_data' key.")
    return config['production_data']

@click.command()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--output', '-o', type=click.Choice(['json', 'table', 'plain']), 
              default='table', help='Output format')
@click.option('--config', type=click.Path(exists=True), help='Configuration file')
@click.pass_context
def get_production_analytics(ctx, verbose: bool, output: str, config: Optional[str]):
    """
    get_production_analytics command.
    Fetch and display production analytics based on the provided configuration.
    """
    try:
        if verbose:
            console.print(f"[blue]Running get_production_analytics command...[/blue]")
        
        if config is None:
            raise ValueError("Configuration file must be provided.")
        
        config_data = load_config(config)
        production_data = fetch_production_data(config_data)

        result_data = {
            "feature": "get_production_analytics",
            "status": "success", 
            "data": production_data,
            "config_used": config,
            "verbose": verbose
        }
        
        # Output results based on format
        if output == 'json':
            console.print_json(json.dumps(result_data, indent=2))
        elif output == 'table':
            table = Table(title=f"get_production_analytics Results")
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
                console.print(f"{key}: {value}")
        
        if verbose:
            console.print(f"[green]✅ get_production_analytics completed successfully[/green]")
            
    except Exception as e:
        console.print(f"[red]❌ get_production_analytics failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)

__all__ = ["get_production_analytics"]