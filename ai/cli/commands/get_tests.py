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

def fetch_tests(config):
    # Simulated fetching of tests based on the configuration
    # In a real implementation, this would interact with a database or an API
    return [
        {"id": 1, "name": "Test A", "status": "passed"},
        {"id": 2, "name": "Test B", "status": "failed"},
        {"id": 3, "name": "Test C", "status": "skipped"},
    ]

@click.command()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--output', '-o', type=click.Choice(['json', 'table', 'plain']), 
              default='table', help='Output format')
@click.option('--config', type=click.Path(exists=True), help='Configuration file')
@click.pass_context
def get_tests(ctx, verbose: bool, output: str, config: Optional[str]):
    """
    get_tests command.
    
    Fetch and display test results based on the provided configuration.
    """
    try:
        if verbose:
            console.print(f"[blue]Running get_tests command...[/blue]")
        
        if config is None:
            raise ValueError("Configuration file must be provided.")
        
        config_data = load_config(config)
        
        if verbose:
            console.print(f"[blue]Loaded configuration: {config_data}[/blue]")
        
        result_data = fetch_tests(config_data)
        
        # Output results based on format
        if output == 'json':
            console.print_json(json.dumps(result_data, indent=2))
        elif output == 'table':
            table = Table(title=f"get_tests Results")
            table.add_column("ID", style="cyan")
            table.add_column("Name", style="magenta")
            table.add_column("Status", style="green")
            
            for test in result_data:
                table.add_row(str(test["id"]), test["name"], test["status"])
            
            console.print(table)
        else:  # plain
            for test in result_data:
                console.print(f"ID: {test['id']}, Name: {test['name']}, Status: {test['status']}")
        
        if verbose:
            console.print(f"[green]✅ get_tests completed successfully[/green]")
            
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
        console.print(f"[red]❌ get_tests failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)

# Export command for CLI registration
__all__ = ["get_tests"]