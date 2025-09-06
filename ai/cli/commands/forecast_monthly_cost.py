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

def calculate_forecast_monthly_cost(config):
    # Placeholder for actual cost calculation logic
    # This should be replaced with real business logic
    monthly_cost = config.get('base_cost', 0) + config.get('additional_cost', 0)
    return monthly_cost

@click.command()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--output', '-o', type=click.Choice(['json', 'table', 'plain']), 
              default='table', help='Output format')
@click.option('--config', type=click.Path(exists=True), help='Configuration file')
@click.pass_context
def forecast_monthly_cost(ctx, verbose: bool, output: str, config: Optional[str]):
    """
    forecast_monthly_cost command.
    This command forecasts the monthly cost based on the provided configuration.
    """
    try:
        if verbose:
            console.print(f"[blue]Running forecast_monthly_cost command...[/blue]")
        
        if not config:
            raise ValueError("Configuration file is required.")
        
        config_data = load_config(config)
        
        if 'base_cost' not in config_data or 'additional_cost' not in config_data:
            raise ValueError("Configuration must contain 'base_cost' and 'additional_cost'.")

        monthly_cost = calculate_forecast_monthly_cost(config_data)
        
        result_data = {
            "feature": "forecast_monthly_cost",
            "status": "success", 
            "monthly_cost": monthly_cost,
            "config_used": config,
            "verbose": verbose
        }
        
        # Output results based on format
        if output == 'json':
            console.print_json(json.dumps(result_data, indent=2))
        elif output == 'table':
            table = Table(title=f"forecast_monthly_cost Results")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="magenta")
            
            for key, value in result_data.items():
                table.add_row(str(key), str(value))
            
            console.print(table)
        else:  # plain
            for key, value in result_data.items():
                console.print(f"{key}: {value}")
        
        if verbose:
            console.print(f"[green]✅ forecast_monthly_cost completed successfully[/green]")
            
    except Exception as e:
        console.print(f"[red]❌ forecast_monthly_cost failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)

# Export command for CLI registration
__all__ = ["forecast_monthly_cost"]