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

def get_execution_status_logic(config):
    # Simulated logic for getting execution status
    # In a real implementation, this would interact with the system or service
    return {
        "execution_id": "12345",
        "status": "running",
        "start_time": "2023-10-01T12:00:00Z",
        "end_time": None,
        "details": "Execution is currently in progress."
    }

@click.command()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--output', '-o', type=click.Choice(['json', 'table', 'plain']), 
              default='table', help='Output format')
@click.option('--config', type=click.Path(exists=True), help='Configuration file')
@click.pass_context
def get_execution_status(ctx, verbose: bool, output: str, config: Optional[str]):
    """
    get_execution_status command.
    Retrieves the execution status of a process based on the provided configuration.
    """
    try:
        if verbose:
            console.print(f"[blue]Running get_execution_status command...[/blue]")
        
        if config:
            config_data = load_config(config)
        else:
            console.print(f"[red]❌ Configuration file is required.[/red]")
            ctx.exit(1)

        result_data = get_execution_status_logic(config_data)

        # Output results based on format
        if output == 'json':
            console.print_json(json.dumps(result_data, indent=2))
        elif output == 'table':
            table = Table(title=f"get_execution_status Results")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="magenta")
            
            for key, value in result_data.items():
                table.add_row(str(key), str(value))
            
            console.print(table)
        else:  # plain
            for key, value in result_data.items():
                console.print(f"{key}: {value}")
        
        if verbose:
            console.print(f"[green]✅ get_execution_status completed successfully[/green]")
            
    except FileNotFoundError:
        console.print(f"[red]❌ Configuration file not found: {config}[/red]")
        ctx.exit(1)
    except json.JSONDecodeError:
        console.print(f"[red]❌ Error decoding JSON from configuration file.[/red]")
        ctx.exit(1)
    except Exception as e:
        console.print(f"[red]❌ get_execution_status failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)

# Export command for CLI registration
__all__ = ["get_execution_status"]