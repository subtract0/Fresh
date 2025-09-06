import click
from typing import Optional
from rich.console import Console
from rich.table import Table
from pathlib import Path
import json
import os

console = Console()

def load_config(config_path: str):
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    with open(config_path, 'r') as file:
        return json.load(file)

def fetch_cost_data(config):
    # Simulated fetching cost data based on configuration
    if 'cost_data_source' not in config:
        raise ValueError("Configuration must include 'cost_data_source'")
    
    # Here you would implement the actual logic to fetch cost data
    return {
        "total_cost": 1500,
        "currency": "USD",
        "details": [
            {"item": "Service A", "cost": 500},
            {"item": "Service B", "cost": 1000}
        ]
    }

@click.command()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--output', '-o', type=click.Choice(['json', 'table', 'plain']), 
              default='table', help='Output format')
@click.option('--config', type=click.Path(exists=True), help='Configuration file')
@click.pass_context
def get_cost_tracker(ctx, verbose: bool, output: str, config: Optional[str]):
    """
    get_cost_tracker command.
    Fetches and displays cost tracking information based on the provided configuration.
    """
    try:
        if verbose:
            console.print(f"[blue]Running get_cost_tracker command...[/blue]")
        
        if config is None:
            raise ValueError("Configuration file must be provided using --config option.")
        
        config_data = load_config(config)
        cost_data = fetch_cost_data(config_data)
        
        # Output results based on format
        if output == 'json':
            console.print_json(json.dumps(cost_data, indent=2))
        elif output == 'table':
            table = Table(title=f"Cost Tracker Results")
            table.add_column("Item", style="cyan")
            table.add_column("Cost", style="magenta")
            
            for detail in cost_data['details']:
                table.add_row(detail['item'], f"{detail['cost']} {cost_data['currency']}")
            
            console.print(table)
            console.print(f"[bold]Total Cost: {cost_data['total_cost']} {cost_data['currency']}[/bold]")
        else:  # plain
            console.print(f"Total Cost: {cost_data['total_cost']} {cost_data['currency']}")
            for detail in cost_data['details']:
                console.print(f"{detail['item']}: {detail['cost']} {cost_data['currency']}")
        
        if verbose:
            console.print(f"[green]✅ get_cost_tracker completed successfully[/green]")
            
    except Exception as e:
        console.print(f"[red]❌ get_cost_tracker failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)

# Export command for CLI registration
__all__ = ["get_cost_tracker"]