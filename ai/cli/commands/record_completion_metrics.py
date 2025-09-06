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

def validate_config(config):
    required_keys = ['metric_name', 'metric_value']
    for key in required_keys:
        if key not in config:
            raise ValueError(f"Missing required config key: {key}")

def record_metrics(metric_name: str, metric_value: float):
    # Simulate recording metrics (e.g., to a database or a file)
    console.print(f"Recording metric: {metric_name} with value: {metric_value}")

@click.command()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--output', '-o', type=click.Choice(['json', 'table', 'plain']), 
              default='table', help='Output format')
@click.option('--config', type=click.Path(exists=True), help='Configuration file')
@click.pass_context
def record_completion_metrics(ctx, verbose: bool, output: str, config: Optional[str]):
    """
    record_completion_metrics command.
    Records completion metrics based on provided configuration.
    """
    try:
        if verbose:
            console.print(f"[blue]Running record_completion_metrics command...[/blue]")
        
        if config:
            config_data = load_config(config)
            validate_config(config_data)
            metric_name = config_data['metric_name']
            metric_value = config_data['metric_value']
        else:
            raise ValueError("Configuration file is required.")

        record_metrics(metric_name, metric_value)

        result_data = {
            "feature": "record_completion_metrics",
            "status": "success", 
            "message": "Metrics recorded successfully",
            "config_used": config,
            "metric_name": metric_name,
            "metric_value": metric_value,
            "verbose": verbose
        }
        
        # Output results based on format
        if output == 'json':
            console.print_json(json.dumps(result_data, indent=2))
        elif output == 'table':
            table = Table(title=f"record_completion_metrics Results")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="magenta")
            
            for key, value in result_data.items():
                table.add_row(str(key), str(value))
            
            console.print(table)
        else:  # plain
            for key, value in result_data.items():
                console.print(f"{key}: {value}")
        
        if verbose:
            console.print(f"[green]✅ record_completion_metrics completed successfully[/green]")
            
    except Exception as e:
        console.print(f"[red]❌ record_completion_metrics failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)

__all__ = ["record_completion_metrics"]