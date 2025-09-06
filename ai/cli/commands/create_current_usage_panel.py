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

def get_current_usage(config):
    # Simulate fetching current usage data based on the provided configuration
    # This should be replaced with actual logic to gather usage data
    return {
        "cpu_usage": "20%",
        "memory_usage": "30%",
        "disk_usage": "40%",
        "network_usage": "10%"
    }

@click.command()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--output', '-o', type=click.Choice(['json', 'table', 'plain']), 
              default='table', help='Output format')
@click.option('--config', type=click.Path(exists=True), help='Configuration file')
@click.pass_context
def create_current_usage_panel(ctx, verbose: bool, output: str, config: Optional[str]):
    """
    create_current_usage_panel command.
    Fetches and displays the current usage statistics based on the provided configuration.
    """
    try:
        if verbose:
            console.print(f"[blue]Running create_current_usage_panel command...[/blue]")
        
        if config is None:
            raise ValueError("Configuration file must be provided.")
        
        config_data = load_config(config)
        
        if verbose:
            console.print(f"[blue]Loaded configuration: {config_data}[/blue]")
        
        usage_data = get_current_usage(config_data)
        
        # Output results based on format
        if output == 'json':
            console.print_json(json.dumps(usage_data, indent=2))
        elif output == 'table':
            table = Table(title=f"Current Usage Panel Results")
            table.add_column("Metric", style="cyan")
            table.add_column("Value", style="magenta")
            
            for key, value in usage_data.items():
                table.add_row(str(key), str(value))
            
            console.print(table)
        else:  # plain
            for key, value in usage_data.items():
                console.print(f"{key}: {value}")
        
        if verbose:
            console.print(f"[green]✅ create_current_usage_panel completed successfully[/green]")
            
    except FileNotFoundError:
        console.print(f"[red]❌ Configuration file not found: {config}[/red]")
        ctx.exit(1)
    except json.JSONDecodeError:
        console.print(f"[red]❌ Error decoding JSON from configuration file: {config}[/red]")
        ctx.exit(1)
    except ValueError as ve:
        console.print(f"[red]❌ {str(ve)}[/red]")
        ctx.exit(1)
    except Exception as e:
        console.print(f"[red]❌ create_current_usage_panel failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)

# Export command for CLI registration
__all__ = ["create_current_usage_panel"]