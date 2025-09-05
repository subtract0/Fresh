import click
from typing import Optional
from rich.console import Console
from rich.table import Table
from pathlib import Path
import json
import os

console = Console()

def load_config(config_path: str):
    if config_path and Path(config_path).exists():
        with open(config_path, 'r') as f:
            return json.load(f)
    return {}

def validate_activity_data(activity_data):
    required_fields = ['name', 'description', 'date']
    for field in required_fields:
        if field not in activity_data:
            raise ValueError(f"Missing required field: {field}")

def save_activity(activity_data):
    activities_file = 'activities.json'
    if os.path.exists(activities_file):
        with open(activities_file, 'r') as f:
            activities = json.load(f)
    else:
        activities = []

    activities.append(activity_data)

    with open(activities_file, 'w') as f:
        json.dump(activities, f, indent=2)

@click.command()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--output', '-o', type=click.Choice(['json', 'table', 'plain']), 
              default='table', help='Output format')
@click.option('--config', type=click.Path(exists=True), help='Configuration file')
@click.option('--name', required=True, help='Name of the activity')
@click.option('--description', required=True, help='Description of the activity')
@click.option('--date', required=True, help='Date of the activity (YYYY-MM-DD)')
@click.pass_context
def add_activity(ctx, verbose: bool, output: str, config: Optional[str], name: str, description: str, date: str):
    """
    Add a new activity to the list.
    """
    try:
        if verbose:
            console.print(f"[blue]Running add_activity command...[/blue]")
        
        config_data = load_config(config)
        
        activity_data = {
            "name": name,
            "description": description,
            "date": date
        }
        
        validate_activity_data(activity_data)
        save_activity(activity_data)
        
        result_data = {
            "feature": "add_activity",
            "status": "success", 
            "message": "Activity added successfully",
            "config_used": config,
            "verbose": verbose
        }
        
        if output == 'json':
            console.print_json(json.dumps(result_data, indent=2))
        elif output == 'table':
            table = Table(title=f"add_activity Results")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="magenta")
            
            for key, value in result_data.items():
                table.add_row(str(key), str(value))
            
            console.print(table)
        else:  # plain
            for key, value in result_data.items():
                console.print(f"{key}: {value}")
        
        if verbose:
            console.print(f"[green]✅ add_activity completed successfully[/green]")
            
    except ValueError as ve:
        console.print(f"[red]❌ add_activity failed: {str(ve)}[/red]")
        ctx.exit(1)
    except Exception as e:
        console.print(f"[red]❌ add_activity failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)

__all__ = ["add_activity"]