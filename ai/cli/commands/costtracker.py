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
    with open(config_path, 'r') as f:
        return json.load(f)

def calculate_costs(config):
    # Placeholder for actual cost calculation logic
    # This should be replaced with real business logic
    return {
        "total_cost": 1000,
        "cost_breakdown": {
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
def costtracker(ctx, verbose: bool, output: str, config: Optional[str]):
    """
    CostTracker command.
    This command calculates and displays cost information based on the provided configuration.
    """
    try:
        if verbose:
            console.print(f"[blue]Running CostTracker command...[/blue]")
        
        if config is None:
            raise ValueError("Configuration file must be provided.")
        
        config_data = load_config(config)
        
        if verbose:
            console.print(f"[yellow]Loaded configuration: {config_data}[/yellow]")
        
        result_data = calculate_costs(config_data)
        result_data["config_used"] = config
        result_data["verbose"] = verbose
        
        # Output results based on format
        if output == 'json':
            console.print_json(json.dumps(result_data, indent=2))
        elif output == 'table':
            table = Table(title=f"CostTracker Results")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="magenta")
            
            for key, value in result_data.items():
                table.add_row(str(key), str(value))
            
            console.print(table)
        else:  # plain
            for key, value in result_data.items():
                console.print(f"{key}: {value}")
        
        if verbose:
            console.print(f"[green]✅ CostTracker completed successfully[/green]")
            
    except FileNotFoundError as fnf_error:
        console.print(f"[red]❌ CostTracker failed: {str(fnf_error)}[/red]")
        ctx.exit(1)
    except ValueError as val_error:
        console.print(f"[red]❌ CostTracker failed: {str(val_error)}[/red]")
        ctx.exit(1)
    except Exception as e:
        console.print(f"[red]❌ CostTracker failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)

# Export command for CLI registration
__all__ = ["costtracker"]