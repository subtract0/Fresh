import click
from typing import Optional
from rich.console import Console
from rich.table import Table
from pathlib import Path
import json
import yaml

console = Console()

def load_config(config_path: str):
    if config_path.endswith('.json'):
        with open(config_path, 'r') as f:
            return json.load(f)
    elif config_path.endswith('.yaml') or config_path.endswith('.yml'):
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    else:
        raise ValueError("Unsupported config file format. Use JSON or YAML.")

def calculate_run_cost(config):
    # Placeholder for actual cost calculation logic
    # This should be replaced with the real implementation
    return {
        "total_cost": 1000,
        "cost_breakdown": {
            "resource_a": 500,
            "resource_b": 300,
            "resource_c": 200
        }
    }

@click.command()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--output', '-o', type=click.Choice(['json', 'table', 'plain']), 
              default='table', help='Output format')
@click.option('--config', type=click.Path(exists=True), help='Configuration file', required=True)
@click.pass_context
def run_cost_dashboard(ctx, verbose: bool, output: str, config: str):
    """
    run_cost_dashboard command.
    This command calculates and displays the run cost based on the provided configuration.
    """
    try:
        if verbose:
            console.print(f"[blue]Running run_cost_dashboard command...[/blue]")
        
        config_data = load_config(config)
        
        if verbose:
            console.print(f"[blue]Loaded configuration: {config_data}[/blue]")
        
        result_data = calculate_run_cost(config_data)
        result_data["config_used"] = config
        result_data["verbose"] = verbose
        
        # Output results based on format
        if output == 'json':
            console.print_json(json.dumps(result_data, indent=2))
        elif output == 'table':
            table = Table(title=f"Run Cost Dashboard Results")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="magenta")
            
            for key, value in result_data.items():
                if isinstance(value, dict):
                    value = json.dumps(value, indent=2)
                table.add_row(str(key), str(value))
            
            console.print(table)
        else:  # plain
            for key, value in result_data.items():
                console.print(f"{key}: {value}")
        
        if verbose:
            console.print(f"[green]✅ run_cost_dashboard completed successfully[/green]")
            
    except ValueError as ve:
        console.print(f"[red]❌ Configuration error: {str(ve)}[/red]")
        ctx.exit(1)
    except Exception as e:
        console.print(f"[red]❌ run_cost_dashboard failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)

__all__ = ["run_cost_dashboard"]