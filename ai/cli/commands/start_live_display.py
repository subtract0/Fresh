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

def start_live_display_logic(config):
    # Placeholder for actual business logic
    # Simulate some processing based on the configuration
    if 'display' not in config:
        raise ValueError("Configuration must include 'display' key.")
    return {
        "feature": "start_live_display",
        "status": "success",
        "message": f"Live display started with configuration: {config['display']}"
    }

@click.command()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--output', '-o', type=click.Choice(['json', 'table', 'plain']), 
              default='table', help='Output format')
@click.option('--config', type=click.Path(exists=True), help='Configuration file')
@click.pass_context
def start_live_display(ctx, verbose: bool, output: str, config: Optional[str]):
    """
    Start live display command.
    This command initializes the live display based on the provided configuration.
    """
    try:
        if verbose:
            console.print(f"[blue]Running start_live_display command...[/blue]")
        
        config_data = load_config(config) if config else {}
        result_data = start_live_display_logic(config_data)
        
        # Output results based on format
        if output == 'json':
            console.print_json(json.dumps(result_data, indent=2))
        elif output == 'table':
            table = Table(title=f"start_live_display Results")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="magenta")
            
            for key, value in result_data.items():
                table.add_row(str(key), str(value))
            
            console.print(table)
        else:  # plain
            for key, value in result_data.items():
                console.print(f"{key}: {value}")
        
        if verbose:
            console.print(f"[green]✅ start_live_display completed successfully[/green]")
            
    except FileNotFoundError as fnf_error:
        console.print(f"[red]❌ start_live_display failed: {str(fnf_error)}[/red]")
        ctx.exit(1)
    except ValueError as val_error:
        console.print(f"[red]❌ start_live_display failed: {str(val_error)}[/red]")
        ctx.exit(1)
    except Exception as e:
        console.print(f"[red]❌ start_live_display failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)

# Export command for CLI registration
__all__ = ["start_live_display"]