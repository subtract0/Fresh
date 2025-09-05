import click
from typing import Optional
from rich.console import Console
from rich.table import Table
from pathlib import Path
import json
import os

console = Console()

def load_config(config_path: str):
    if not os.path.isfile(config_path):
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    with open(config_path, 'r') as file:
        return json.load(file)

def process_data(config):
    # Simulate processing based on configuration
    if 'data' not in config:
        raise ValueError("Configuration must contain 'data' key.")
    return {
        "processed_data": config['data'],
        "status": "success"
    }

@click.command()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--output', '-o', type=click.Choice(['json', 'table', 'plain']), 
              default='table', help='Output format')
@click.option('--config', type=click.Path(exists=True), help='Configuration file', required=True)
@click.pass_context
def callmcptool(ctx, verbose: bool, output: str, config: Optional[str]):
    """
    CallMCPTool command.
    This command processes data based on the provided configuration file.
    """
    try:
        if verbose:
            console.print(f"[blue]Running CallMCPTool command...[/blue]")
        
        config_data = load_config(config)
        result_data = process_data(config_data)
        
        # Output results based on format
        if output == 'json':
            console.print_json(json.dumps(result_data, indent=2))
        elif output == 'table':
            table = Table(title=f"CallMCPTool Results")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="magenta")
            
            for key, value in result_data.items():
                table.add_row(str(key), str(value))
            
            console.print(table)
        else:  # plain
            for key, value in result_data.items():
                console.print(f"{key}: {value}")
        
        if verbose:
            console.print(f"[green]✅ CallMCPTool completed successfully[/green]")
            
    except FileNotFoundError as fnf_error:
        console.print(f"[red]❌ CallMCPTool failed: {str(fnf_error)}[/red]")
        ctx.exit(1)
    except ValueError as val_error:
        console.print(f"[red]❌ CallMCPTool failed: {str(val_error)}[/red]")
        ctx.exit(1)
    except Exception as e:
        console.print(f"[red]❌ CallMCPTool failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)

# Export command for CLI registration
__all__ = ["callmcptool"]