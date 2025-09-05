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

def get_progress_data(config):
    # Simulated progress data based on configuration
    return {
        "total_tasks": config.get("total_tasks", 0),
        "completed_tasks": config.get("completed_tasks", 0),
        "pending_tasks": config.get("total_tasks", 0) - config.get("completed_tasks", 0),
        "status": "in_progress" if config.get("completed_tasks", 0) < config.get("total_tasks", 0) else "completed"
    }

@click.command()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--output', '-o', type=click.Choice(['json', 'table', 'plain']), 
              default='table', help='Output format')
@click.option('--config', type=click.Path(exists=True), help='Configuration file')
@click.pass_context
def show_progress(ctx, verbose: bool, output: str, config: Optional[str]):
    """
    show_progress command.
    Displays the progress of tasks based on the provided configuration.
    """
    try:
        if verbose:
            console.print(f"[blue]Running show_progress command...[/blue]")
        
        if config is None:
            raise ValueError("Configuration file must be provided.")
        
        config_data = load_config(config)
        progress_data = get_progress_data(config_data)
        
        # Output results based on format
        if output == 'json':
            console.print_json(json.dumps(progress_data, indent=2))
        elif output == 'table':
            table = Table(title=f"show_progress Results")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="magenta")
            
            for key, value in progress_data.items():
                table.add_row(str(key), str(value))
            
            console.print(table)
        else:  # plain
            for key, value in progress_data.items():
                console.print(f"{key}: {value}")
        
        if verbose:
            console.print(f"[green]✅ show_progress completed successfully[/green]")
            
    except FileNotFoundError as fnf_error:
        console.print(f"[red]❌ show_progress failed: {str(fnf_error)}[/red]")
        ctx.exit(1)
    except ValueError as ve:
        console.print(f"[red]❌ show_progress failed: {str(ve)}[/red]")
        ctx.exit(1)
    except Exception as e:
        console.print(f"[red]❌ show_progress failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)

# Export command for CLI registration
__all__ = ["show_progress"]