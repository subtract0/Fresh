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

def calculate_cost_summary(config):
    # Placeholder for actual cost calculation logic
    # This should be replaced with real calculations based on the config
    return {
        "total_cost": 1000,
        "breakdown": {
            "item1": 400,
            "item2": 600
        }
    }

@click.command()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--output', '-o', type=click.Choice(['json', 'table', 'plain']), 
              default='table', help='Output format')
@click.option('--config', type=click.Path(exists=True), help='Configuration file')
@click.pass_context
def quick_cost_summary(ctx, verbose: bool, output: str, config: Optional[str]):
    """
    quick_cost_summary command.
    Generates a quick cost summary based on the provided configuration.
    """
    try:
        if verbose:
            console.print(f"[blue]Running quick_cost_summary command...[/blue]")
        
        if config is None:
            raise ValueError("Configuration file must be provided.")
        
        config_data = load_config(config)
        
        if verbose:
            console.print(f"[blue]Loaded configuration: {config_data}[/blue]")
        
        result_data = calculate_cost_summary(config_data)
        
        # Output results based on format
        if output == 'json':
            console.print_json(json.dumps(result_data, indent=2))
        elif output == 'table':
            table = Table(title=f"Quick Cost Summary Results")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="magenta")
            
            for key, value in result_data.items():
                if isinstance(value, dict):
                    for sub_key, sub_value in value.items():
                        table.add_row(f"{key} - {sub_key}", str(sub_value))
                else:
                    table.add_row(str(key), str(value))
            
            console.print(table)
        else:  # plain
            for key, value in result_data.items():
                if isinstance(value, dict):
                    for sub_key, sub_value in value.items():
                        console.print(f"{key} - {sub_key}: {sub_value}")
                else:
                    console.print(f"{key}: {value}")
        
        if verbose:
            console.print(f"[green]✅ quick_cost_summary completed successfully[/green]")
            
    except Exception as e:
        console.print(f"[red]❌ quick_cost_summary failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)

# Export command for CLI registration
__all__ = ["quick_cost_summary"]