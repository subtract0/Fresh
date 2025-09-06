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

def get_activity_detector_logic(config):
    # Placeholder for actual logic to get activity detector data
    # This should be replaced with the real implementation
    return {
        "detector_name": config.get("detector_name", "default_detector"),
        "activity_threshold": config.get("activity_threshold", 0.5),
        "status": "active"
    }

@click.command()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--output', '-o', type=click.Choice(['json', 'table', 'plain']), 
              default='table', help='Output format')
@click.option('--config', type=click.Path(exists=True), help='Configuration file', required=True)
@click.pass_context
def get_activity_detector(ctx, verbose: bool, output: str, config: Optional[str]):
    """
    get_activity_detector command.
    Retrieves the activity detector configuration and status.
    """
    try:
        if verbose:
            console.print(f"[blue]Running get_activity_detector command...[/blue]")
        
        if not os.path.isfile(config):
            raise FileNotFoundError(f"Configuration file not found: {config}")
        
        config_data = load_config(config)
        
        result_data = get_activity_detector_logic(config_data)
        
        # Output results based on format
        if output == 'json':
            console.print_json(json.dumps(result_data, indent=2))
        elif output == 'table':
            table = Table(title=f"get_activity_detector Results")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="magenta")
            
            for key, value in result_data.items():
                table.add_row(str(key), str(value))
            
            console.print(table)
        else:  # plain
            for key, value in result_data.items():
                console.print(f"{key}: {value}")
        
        if verbose:
            console.print(f"[green]✅ get_activity_detector completed successfully[/green]")
            
    except FileNotFoundError as fnf_error:
        console.print(f"[red]❌ Error: {str(fnf_error)}[/red]")
        ctx.exit(1)
    except json.JSONDecodeError as json_error:
        console.print(f"[red]❌ JSON decode error: {str(json_error)}[/red]")
        ctx.exit(1)
    except Exception as e:
        console.print(f"[red]❌ get_activity_detector failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)

# Export command for CLI registration
__all__ = ["get_activity_detector"]