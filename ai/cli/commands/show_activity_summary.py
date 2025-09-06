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

def get_activity_summary(config):
    # Simulated activity summary based on configuration
    return {
        "total_activities": 42,
        "completed_activities": 30,
        "pending_activities": 12,
        "last_activity": "2023-10-01"
    }

@click.command()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--output', '-o', type=click.Choice(['json', 'table', 'plain']), 
              default='table', help='Output format')
@click.option('--config', type=click.Path(exists=True), help='Configuration file')
@click.pass_context
def show_activity_summary(ctx, verbose: bool, output: str, config: Optional[str]):
    """
    show_activity_summary command.
    Displays a summary of activities based on the provided configuration.
    """
    try:
        if verbose:
            console.print(f"[blue]Running show_activity_summary command...[/blue]")
        
        if config:
            config_data = load_config(config)
        else:
            raise ValueError("Configuration file must be provided.")

        summary = get_activity_summary(config_data)

        # Output results based on format
        if output == 'json':
            console.print_json(json.dumps(summary, indent=2))
        elif output == 'table':
            table = Table(title=f"Activity Summary")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="magenta")
            
            for key, value in summary.items():
                table.add_row(str(key), str(value))
            
            console.print(table)
        else:  # plain
            for key, value in summary.items():
                console.print(f"{key}: {value}")
        
        if verbose:
            console.print(f"[green]✅ show_activity_summary completed successfully[/green]")
            
    except FileNotFoundError as fnf_error:
        console.print(f"[red]❌ show_activity_summary failed: {str(fnf_error)}[/red]")
        ctx.exit(1)
    except ValueError as val_error:
        console.print(f"[red]❌ show_activity_summary failed: {str(val_error)}[/red]")
        ctx.exit(1)
    except Exception as e:
        console.print(f"[red]❌ show_activity_summary failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)

# Export command for CLI registration
__all__ = ["show_activity_summary"]