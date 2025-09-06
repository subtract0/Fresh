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

def monitor_functionality(config):
    # Simulate monitoring logic based on the configuration
    monitored_data = {
        "cpu_usage": "20%",
        "memory_usage": "30%",
        "disk_space": "50GB free",
        "status": "running"
    }
    return monitored_data

@click.command()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--output', '-o', type=click.Choice(['json', 'table', 'plain']), 
              default='table', help='Output format')
@click.option('--config', type=click.Path(exists=True), help='Configuration file')
@click.pass_context
def cmd_monitor(ctx, verbose: bool, output: str, config: Optional[str]):
    """
    cmd_monitor command.
    Monitors system resources based on the provided configuration.
    """
    try:
        if verbose:
            console.print(f"[blue]Running cmd_monitor command...[/blue]")
        
        # Load configuration if provided
        config_data = None
        if config:
            config_data = load_config(config)
            if verbose:
                console.print(f"[yellow]Loaded configuration: {config_data}[/yellow]")
        
        # Implement actual cmd_monitor logic here
        result_data = monitor_functionality(config_data)
        result_data["config_used"] = config
        result_data["verbose"] = verbose
        
        # Output results based on format
        if output == 'json':
            console.print_json(json.dumps(result_data, indent=2))
        elif output == 'table':
            table = Table(title=f"cmd_monitor Results")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="magenta")
            
            for key, value in result_data.items():
                table.add_row(str(key), str(value))
            
            console.print(table)
        else:  # plain
            for key, value in result_data.items():
                console.print(f"{key}: {value}")
        
        if verbose:
            console.print(f"[green]✅ cmd_monitor completed successfully[/green]")
            
    except FileNotFoundError as fnf_error:
        console.print(f"[red]❌ cmd_monitor failed: {str(fnf_error)}[/red]")
        ctx.exit(1)
    except json.JSONDecodeError as json_error:
        console.print(f"[red]❌ JSON decode error: {str(json_error)}[/red]")
        ctx.exit(1)
    except Exception as e:
        console.print(f"[red]❌ cmd_monitor failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)

# Export command for CLI registration
__all__ = ["cmd_monitor"]