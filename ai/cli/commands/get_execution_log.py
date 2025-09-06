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

def get_execution_log_data(config):
    log_file_path = config.get("log_file_path")
    if not log_file_path or not os.path.exists(log_file_path):
        raise FileNotFoundError("Log file not found or path not specified in the configuration.")
    
    with open(log_file_path, 'r') as f:
        return json.load(f)

@click.command()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--output', '-o', type=click.Choice(['json', 'table', 'plain']), 
              default='table', help='Output format')
@click.option('--config', type=click.Path(exists=True), help='Configuration file')
@click.pass_context
def get_execution_log(ctx, verbose: bool, output: str, config: Optional[str]):
    """
    get_execution_log command.
    Retrieves and displays the execution log based on the provided configuration.
    """
    try:
        if verbose:
            console.print(f"[blue]Running get_execution_log command...[/blue]")
        
        if not config:
            raise ValueError("Configuration file must be provided.")
        
        config_data = load_config(config)
        log_data = get_execution_log_data(config_data)
        
        # Output results based on format
        if output == 'json':
            console.print_json(json.dumps(log_data, indent=2))
        elif output == 'table':
            table = Table(title=f"Execution Log Results")
            table.add_column("Key", style="cyan")
            table.add_column("Value", style="magenta")
            
            for key, value in log_data.items():
                table.add_row(str(key), str(value))
            
            console.print(table)
        else:  # plain
            for key, value in log_data.items():
                console.print(f"{key}: {value}")
        
        if verbose:
            console.print(f"[green]✅ get_execution_log completed successfully[/green]")
            
    except FileNotFoundError as fnf_error:
        console.print(f"[red]❌ Error: {str(fnf_error)}[/red]")
        ctx.exit(1)
    except ValueError as ve:
        console.print(f"[red]❌ Error: {str(ve)}[/red]")
        ctx.exit(1)
    except Exception as e:
        console.print(f"[red]❌ get_execution_log failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)

# Export command for CLI registration
__all__ = ["get_execution_log"]