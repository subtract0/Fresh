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

def validate_config(config):
    required_keys = ['metric_name', 'spawn_rate', 'duration']
    for key in required_keys:
        if key not in config:
            raise ValueError(f"Missing required config key: {key}")

def record_metrics(metric_name: str, spawn_rate: int, duration: int):
    # Simulate recording metrics (this would be replaced with actual logic)
    return {
        "metric_name": metric_name,
        "spawn_rate": spawn_rate,
        "duration": duration,
        "success": True,
        "message": "Metrics recorded successfully"
    }

@click.command()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--output', '-o', type=click.Choice(['json', 'table', 'plain']), 
              default='table', help='Output format')
@click.option('--config', type=click.Path(exists=True), help='Configuration file')
@click.pass_context
def record_spawn_metrics(ctx, verbose: bool, output: str, config: Optional[str]):
    """
    record_spawn_metrics command.
    Records metrics related to spawn events based on provided configuration.
    """
    try:
        if verbose:
            console.print(f"[blue]Running record_spawn_metrics command...[/blue]")
        
        if config:
            config_data = load_config(config)
            validate_config(config_data)
            metric_name = config_data['metric_name']
            spawn_rate = config_data['spawn_rate']
            duration = config_data['duration']
        else:
            raise ValueError("Configuration file is required.")

        result_data = record_metrics(metric_name, spawn_rate, duration)

        # Output results based on format
        if output == 'json':
            console.print_json(json.dumps(result_data, indent=2))
        elif output == 'table':
            table = Table(title=f"record_spawn_metrics Results")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="magenta")
            
            for key, value in result_data.items():
                table.add_row(str(key), str(value))
            
            console.print(table)
        else:  # plain
            for key, value in result_data.items():
                console.print(f"{key}: {value}")
        
        if verbose:
            console.print(f"[green]✅ record_spawn_metrics completed successfully[/green]")
            
    except Exception as e:
        console.print(f"[red]❌ record_spawn_metrics failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)

# Export command for CLI registration
__all__ = ["record_spawn_metrics"]