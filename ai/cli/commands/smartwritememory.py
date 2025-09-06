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

def process_memory_data(config):
    # Simulate processing memory data based on the configuration
    if 'memory_limit' not in config:
        raise ValueError("Configuration must include 'memory_limit'")
    return {
        "memory_limit": config['memory_limit'],
        "used_memory": 0.75 * config['memory_limit'],  # Example calculation
        "available_memory": 0.25 * config['memory_limit']
    }

@click.command()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--output', '-o', type=click.Choice(['json', 'table', 'plain']), 
              default='table', help='Output format')
@click.option('--config', type=click.Path(exists=True), help='Configuration file', required=True)
@click.pass_context
def smartwritememory(ctx, verbose: bool, output: str, config: Optional[str]):
    """
    SmartWriteMemory command.
    This command processes memory data based on the provided configuration.
    """
    try:
        if verbose:
            console.print(f"[blue]Running SmartWriteMemory command...[/blue]")
        
        config_data = load_config(config)
        memory_data = process_memory_data(config_data)

        result_data = {
            "feature": "SmartWriteMemory",
            "status": "success", 
            "memory_data": memory_data,
            "config_used": config,
            "verbose": verbose
        }
        
        # Output results based on format
        if output == 'json':
            console.print_json(json.dumps(result_data, indent=2))
        elif output == 'table':
            table = Table(title=f"SmartWriteMemory Results")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="magenta")
            
            for key, value in result_data.items():
                if isinstance(value, dict):
                    for sub_key, sub_value in value.items():
                        table.add_row(f"{key}.{sub_key}", str(sub_value))
                else:
                    table.add_row(str(key), str(value))
            
            console.print(table)
        else:  # plain
            for key, value in result_data.items():
                if isinstance(value, dict):
                    for sub_key, sub_value in value.items():
                        console.print(f"{key}.{sub_key}: {sub_value}")
                else:
                    console.print(f"{key}: {value}")
        
        if verbose:
            console.print(f"[green]✅ SmartWriteMemory completed successfully[/green]")
            
    except FileNotFoundError as fnf_error:
        console.print(f"[red]❌ SmartWriteMemory failed: {str(fnf_error)}[/red]")
        ctx.exit(1)
    except ValueError as val_error:
        console.print(f"[red]❌ SmartWriteMemory failed: {str(val_error)}[/red]")
        ctx.exit(1)
    except Exception as e:
        console.print(f"[red]❌ SmartWriteMemory failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)

__all__ = ["smartwritememory"]