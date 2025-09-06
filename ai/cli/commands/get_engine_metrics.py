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

def collect_engine_metrics(config):
    # Simulated metrics collection logic
    metrics = {
        "cpu_usage": "20%",
        "memory_usage": "512MB",
        "disk_io": "100MB/s",
        "network_io": "50MB/s",
        "uptime": "72 hours"
    }
    return metrics

@click.command()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--output', '-o', type=click.Choice(['json', 'table', 'plain']), 
              default='table', help='Output format')
@click.option('--config', type=click.Path(exists=True), help='Configuration file')
@click.pass_context
def get_engine_metrics(ctx, verbose: bool, output: str, config: Optional[str]):
    """
    get_engine_metrics command.
    Collect and display engine metrics based on the provided configuration.
    """
    try:
        if verbose:
            console.print(f"[blue]Running get_engine_metrics command...[/blue]")
        
        if config:
            config_data = load_config(config)
            if verbose:
                console.print(f"[yellow]Loaded configuration: {config_data}[/yellow]")
        else:
            config_data = {}

        metrics = collect_engine_metrics(config_data)

        result_data = {
            "feature": "get_engine_metrics",
            "status": "success", 
            "metrics": metrics,
            "config_used": config,
            "verbose": verbose
        }
        
        # Output results based on format
        if output == 'json':
            console.print_json(json.dumps(result_data, indent=2))
        elif output == 'table':
            table = Table(title=f"get_engine_metrics Results")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="magenta")
            
            for key, value in result_data.items():
                if key == "metrics":
                    for metric_key, metric_value in value.items():
                        table.add_row(metric_key, metric_value)
                else:
                    table.add_row(str(key), str(value))
            
            console.print(table)
        else:  # plain
            for key, value in result_data.items():
                if key == "metrics":
                    for metric_key, metric_value in value.items():
                        console.print(f"{metric_key}: {metric_value}")
                else:
                    console.print(f"{key}: {value}")
        
        if verbose:
            console.print(f"[green]✅ get_engine_metrics completed successfully[/green]")
            
    except FileNotFoundError:
        console.print(f"[red]❌ Configuration file not found: {config}[/red]")
        ctx.exit(1)
    except json.JSONDecodeError:
        console.print(f"[red]❌ Error decoding JSON from configuration file: {config}[/red]")
        ctx.exit(1)
    except Exception as e:
        console.print(f"[red]❌ get_engine_metrics failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)

__all__ = ["get_engine_metrics"]