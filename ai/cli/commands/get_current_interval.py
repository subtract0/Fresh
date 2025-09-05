import click
from typing import Optional
from rich.console import Console
from rich.table import Table
from pathlib import Path
import json
import os
import datetime

console = Console()

def load_config(config_path: str):
    if config_path and Path(config_path).exists():
        with open(config_path, 'r') as f:
            return json.load(f)
    return {}

def get_current_time_interval():
    now = datetime.datetime.now()
    start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_day = now.replace(hour=23, minute=59, second=59, microsecond=999999)
    return {
        "current_time": now.isoformat(),
        "start_of_day": start_of_day.isoformat(),
        "end_of_day": end_of_day.isoformat()
    }

@click.command()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--output', '-o', type=click.Choice(['json', 'table', 'plain']), 
              default='table', help='Output format')
@click.option('--config', type=click.Path(exists=True), help='Configuration file')
@click.pass_context
def get_current_interval(ctx, verbose: bool, output: str, config: Optional[str]):
    """
    get_current_interval command.
    Retrieves the current time interval for the day.
    """
    try:
        if verbose:
            console.print(f"[blue]Running get_current_interval command...[/blue]")
        
        config_data = load_config(config)
        interval_data = get_current_time_interval()
        
        result_data = {
            "feature": "get_current_interval",
            "status": "success", 
            "data": interval_data,
            "config_used": config_data,
            "verbose": verbose
        }
        
        # Output results based on format
        if output == 'json':
            console.print_json(json.dumps(result_data, indent=2))
        elif output == 'table':
            table = Table(title=f"get_current_interval Results")
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
                if isinstance(value, dict):
                    for sub_key, sub_value in value.items():
                        console.print(f"{key}.{sub_key}: {sub_value}")
                else:
                    console.print(f"{key}: {value}")
        
        if verbose:
            console.print(f"[green]✅ get_current_interval completed successfully[/green]")
            
    except Exception as e:
        console.print(f"[red]❌ get_current_interval failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)

__all__ = ["get_current_interval"]