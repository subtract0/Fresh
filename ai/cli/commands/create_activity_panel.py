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
    required_keys = ['activity_name', 'activity_type']
    for key in required_keys:
        if key not in config:
            raise ValueError(f"Missing required config key: {key}")

def create_activity(config):
    activity_name = config['activity_name']
    activity_type = config['activity_type']
    # Simulate activity creation logic
    return {
        "activity_name": activity_name,
        "activity_type": activity_type,
        "status": "created"
    }

@click.command()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--output', '-o', type=click.Choice(['json', 'table', 'plain']), 
              default='table', help='Output format')
@click.option('--config', type=click.Path(exists=True), help='Configuration file')
@click.pass_context
def create_activity_panel(ctx, verbose: bool, output: str, config: Optional[str]):
    """
    create_activity_panel command to create an activity based on the provided configuration.
    """
    try:
        if verbose:
            console.print(f"[blue]Running create_activity_panel command...[/blue]")
        
        if config:
            config_data = load_config(config)
            validate_config(config_data)
        else:
            raise ValueError("Configuration file is required.")

        result_data = create_activity(config_data)

        # Output results based on format
        if output == 'json':
            console.print_json(json.dumps(result_data, indent=2))
        elif output == 'table':
            table = Table(title=f"create_activity_panel Results")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="magenta")
            
            for key, value in result_data.items():
                table.add_row(str(key), str(value))
            
            console.print(table)
        else:  # plain
            for key, value in result_data.items():
                console.print(f"{key}: {value}")
        
        if verbose:
            console.print(f"[green]✅ create_activity_panel completed successfully[/green]")
            
    except ValueError as ve:
        console.print(f"[red]❌ create_activity_panel failed: {str(ve)}[/red]")
        ctx.exit(1)
    except Exception as e:
        console.print(f"[red]❌ create_activity_panel failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)

# Export command for CLI registration
__all__ = ["create_activity_panel"]