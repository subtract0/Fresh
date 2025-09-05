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

def fetch_recent_activity(config):
    # Simulated fetching of recent activity based on configuration
    # In a real implementation, this would interface with a database or API
    return [
        {"timestamp": "2023-10-01T12:00:00Z", "activity": "User logged in"},
        {"timestamp": "2023-10-01T12:05:00Z", "activity": "User updated profile"},
        {"timestamp": "2023-10-01T12:10:00Z", "activity": "User logged out"},
    ]

@click.command()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--output', '-o', type=click.Choice(['json', 'table', 'plain']), 
              default='table', help='Output format')
@click.option('--config', type=click.Path(exists=True), help='Configuration file')
@click.pass_context
def create_recent_activity_panel(ctx, verbose: bool, output: str, config: Optional[str]):
    """
    create_recent_activity_panel command.
    Fetch and display recent user activity based on the provided configuration.
    """
    try:
        if verbose:
            console.print(f"[blue]Running create_recent_activity_panel command...[/blue]")
        
        if config is None:
            raise ValueError("Configuration file must be provided.")

        config_data = load_config(config)
        
        if verbose:
            console.print(f"[blue]Loaded configuration: {config_data}[/blue]")

        recent_activity = fetch_recent_activity(config_data)

        result_data = {
            "feature": "create_recent_activity_panel",
            "status": "success", 
            "recent_activity": recent_activity,
            "config_used": config,
            "verbose": verbose
        }
        
        # Output results based on format
        if output == 'json':
            console.print_json(json.dumps(result_data, indent=2))
        elif output == 'table':
            table = Table(title=f"Recent Activity")
            table.add_column("Timestamp", style="cyan")
            table.add_column("Activity", style="magenta")
            
            for activity in recent_activity:
                table.add_row(activity["timestamp"], activity["activity"])
            
            console.print(table)
        else:  # plain
            for activity in recent_activity:
                console.print(f"{activity['timestamp']}: {activity['activity']}")
        
        if verbose:
            console.print(f"[green]✅ create_recent_activity_panel completed successfully[/green]")
            
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
        console.print(f"[red]❌ create_recent_activity_panel failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)

__all__ = ["create_recent_activity_panel"]