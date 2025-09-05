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

def get_status_coordinator_data(config):
    # Simulate fetching status data based on the configuration
    return {
        "feature": "StatusCoordinator",
        "status": "implemented",
        "message": "StatusCoordinator functionality is operational",
        "config_used": config,
    }

@click.command()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--output', '-o', type=click.Choice(['json', 'table', 'plain']), 
              default='table', help='Output format')
@click.option('--config', type=click.Path(exists=True), help='Configuration file')
@click.pass_context
def statuscoordinator(ctx, verbose: bool, output: str, config: Optional[str]):
    """
    StatusCoordinator command.
    Fetches and displays the status of the StatusCoordinator feature.
    """
    try:
        if verbose:
            console.print(f"[blue]Running StatusCoordinator command...[/blue]")
        
        config_data = load_config(config) if config else {}
        result_data = get_status_coordinator_data(config_data)
        
        # Output results based on format
        if output == 'json':
            console.print_json(json.dumps(result_data, indent=2))
        elif output == 'table':
            table = Table(title=f"StatusCoordinator Results")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="magenta")
            
            for key, value in result_data.items():
                table.add_row(str(key), str(value))
            
            console.print(table)
        else:  # plain
            for key, value in result_data.items():
                console.print(f"{key}: {value}")
        
        if verbose:
            console.print(f"[green]✅ StatusCoordinator completed successfully[/green]")
            
    except FileNotFoundError as fnf_error:
        console.print(f"[red]❌ StatusCoordinator failed: {str(fnf_error)}[/red]")
        ctx.exit(1)
    except json.JSONDecodeError as json_error:
        console.print(f"[red]❌ JSON decode error: {str(json_error)}[/red]")
        ctx.exit(1)
    except Exception as e:
        console.print(f"[red]❌ StatusCoordinator failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)

# Export command for CLI registration
__all__ = ["statuscoordinator"]