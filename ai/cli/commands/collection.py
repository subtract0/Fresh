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

def perform_collection(config):
    # Simulated collection logic based on configuration
    if 'data_source' not in config:
        raise ValueError("Configuration must include 'data_source'")
    
    # Here you would implement the actual data collection logic
    return {
        "data_source": config['data_source'],
        "collected_data": ["data1", "data2", "data3"],  # Simulated data
        "status": "success"
    }

@click.command()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--output', '-o', type=click.Choice(['json', 'table', 'plain']), 
              default='table', help='Output format')
@click.option('--config', type=click.Path(exists=True), help='Configuration file')
@click.pass_context
def collection(ctx, verbose: bool, output: str, config: Optional[str]):
    """
    collection command.
    Collects data based on the provided configuration.
    """
    try:
        if verbose:
            console.print(f"[blue]Running collection command...[/blue]")
        
        if config:
            config_data = load_config(config)
        else:
            raise ValueError("Configuration file must be provided.")
        
        result_data = perform_collection(config_data)
        
        # Output results based on format
        if output == 'json':
            console.print_json(json.dumps(result_data, indent=2))
        elif output == 'table':
            table = Table(title=f"Collection Results")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="magenta")
            
            for key, value in result_data.items():
                table.add_row(str(key), str(value))
            
            console.print(table)
        else:  # plain
            for key, value in result_data.items():
                console.print(f"{key}: {value}")
        
        if verbose:
            console.print(f"[green]✅ Collection completed successfully[/green]")
            
    except FileNotFoundError as fnf_error:
        console.print(f"[red]❌ Collection failed: {str(fnf_error)}[/red]")
        ctx.exit(1)
    except ValueError as val_error:
        console.print(f"[red]❌ Collection failed: {str(val_error)}[/red]")
        ctx.exit(1)
    except Exception as e:
        console.print(f"[red]❌ Collection failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)

# Export command for CLI registration
__all__ = ["collection"]