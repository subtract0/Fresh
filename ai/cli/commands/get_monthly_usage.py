import click
from typing import Optional
from rich.console import Console
from rich.table import Table
from pathlib import Path
import json
import os

console = Console()

def load_config(config_path: str):
    with open(config_path, 'r') as file:
        return json.load(file)

def get_usage_data(config):
    # Simulate fetching monthly usage data based on the configuration
    # This should be replaced with actual logic to retrieve usage data
    return {
        "total_usage": 1500,  # Example usage in MB
        "usage_by_service": {
            "service_a": 800,
            "service_b": 700
        }
    }

@click.command()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--output', '-o', type=click.Choice(['json', 'table', 'plain']), 
              default='table', help='Output format')
@click.option('--config', type=click.Path(exists=True), help='Configuration file', required=True)
@click.pass_context
def get_monthly_usage(ctx, verbose: bool, output: str, config: str):
    """
    get_monthly_usage command.
    Fetches and displays the monthly usage based on the provided configuration.
    """
    try:
        if verbose:
            console.print(f"[blue]Running get_monthly_usage command...[/blue]")
        
        # Load configuration
        config_data = load_config(config)
        
        # Validate configuration
        if 'api_key' not in config_data or 'endpoint' not in config_data:
            raise ValueError("Configuration must include 'api_key' and 'endpoint'.")

        # Get usage data
        usage_data = get_usage_data(config_data)

        # Prepare result data
        result_data = {
            "feature": "get_monthly_usage",
            "status": "success", 
            "data": usage_data,
            "config_used": config,
            "verbose": verbose
        }
        
        # Output results based on format
        if output == 'json':
            console.print_json(json.dumps(result_data, indent=2))
        elif output == 'table':
            table = Table(title=f"get_monthly_usage Results")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="magenta")
            
            for key, value in result_data.items():
                if isinstance(value, dict):
                    value = json.dumps(value, indent=2)
                table.add_row(str(key), str(value))
            
            console.print(table)
        else:  # plain
            for key, value in result_data.items():
                if isinstance(value, dict):
                    value = json.dumps(value, indent=2)
                console.print(f"{key}: {value}")
        
        if verbose:
            console.print(f"[green]✅ get_monthly_usage completed successfully[/green]")
            
    except Exception as e:
        console.print(f"[red]❌ get_monthly_usage failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)

# Export command for CLI registration
__all__ = ["get_monthly_usage"]