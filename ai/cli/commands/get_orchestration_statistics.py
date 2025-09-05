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

def get_statistics(config):
    # Simulated statistics retrieval logic
    return {
        "total_orchestrations": 100,
        "successful_orchestrations": 90,
        "failed_orchestrations": 10,
        "average_execution_time": "2.5s"
    }

@click.command()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--output', '-o', type=click.Choice(['json', 'table', 'plain']), 
              default='table', help='Output format')
@click.option('--config', type=click.Path(exists=True), help='Configuration file')
@click.pass_context
def get_orchestration_statistics(ctx, verbose: bool, output: str, config: Optional[str]):
    """
    get_orchestration_statistics command.
    Retrieves statistics about orchestration executions.
    """
    try:
        if verbose:
            console.print(f"[blue]Running get_orchestration_statistics command...[/blue]")
        
        if config:
            config_data = load_config(config)
            if verbose:
                console.print(f"[yellow]Loaded configuration from {config}[/yellow]")
        else:
            config_data = {}

        statistics = get_statistics(config_data)

        # Output results based on format
        if output == 'json':
            console.print_json(json.dumps(statistics, indent=2))
        elif output == 'table':
            table = Table(title=f"get_orchestration_statistics Results")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="magenta")
            
            for key, value in statistics.items():
                table.add_row(str(key), str(value))
            
            console.print(table)
        else:  # plain
            for key, value in statistics.items():
                console.print(f"{key}: {value}")
        
        if verbose:
            console.print(f"[green]✅ get_orchestration_statistics completed successfully[/green]")
            
    except FileNotFoundError:
        console.print(f"[red]❌ Configuration file not found: {config}[/red]")
        ctx.exit(1)
    except json.JSONDecodeError:
        console.print(f"[red]❌ Error decoding JSON from configuration file: {config}[/red]")
        ctx.exit(1)
    except Exception as e:
        console.print(f"[red]❌ get_orchestration_statistics failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)

# Export command for CLI registration
__all__ = ["get_orchestration_statistics"]