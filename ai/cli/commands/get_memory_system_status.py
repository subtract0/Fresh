import click
from typing import Optional
from rich.console import Console
from rich.table import Table
from pathlib import Path
import json
import os

console = Console()

def read_config(config_path: str):
    with open(config_path, 'r') as file:
        return json.load(file)

def get_memory_status():
    # Simulated memory status retrieval logic
    memory_info = {
        "total_memory": os.sysconf('SC_PAGE_SIZE') * os.sysconf('SC_PHYS_PAGES'),
        "available_memory": os.sysconf('SC_PAGE_SIZE') * os.sysconf('SC_AVPHYS_PAGES'),
        "used_memory": os.sysconf('SC_PAGE_SIZE') * (os.sysconf('SC_PHYS_PAGES') - os.sysconf('SC_AVPHYS_PAGES')),
    }
    return memory_info

@click.command()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--output', '-o', type=click.Choice(['json', 'table', 'plain']), 
              default='table', help='Output format')
@click.option('--config', type=click.Path(exists=True), help='Configuration file')
@click.pass_context
def get_memory_system_status(ctx, verbose: bool, output: str, config: Optional[str]):
    """
    Get memory system status command.
    Retrieves and displays the current memory status of the system.
    """
    try:
        if verbose:
            console.print(f"[blue]Running get_memory_system_status command...[/blue]")
        
        # Load configuration if provided
        config_data = {}
        if config:
            config_data = read_config(config)

        # Get memory status
        memory_status = get_memory_status()
        result_data = {
            "feature": "get_memory_system_status",
            "status": "success", 
            "memory_info": memory_status,
            "config_used": config_data,
            "verbose": verbose
        }
        
        # Output results based on format
        if output == 'json':
            console.print_json(json.dumps(result_data, indent=2))
        elif output == 'table':
            table = Table(title=f"get_memory_system_status Results")
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
            console.print(f"[green]✅ get_memory_system_status completed successfully[/green]")
            
    except FileNotFoundError as fnf_error:
        console.print(f"[red]❌ Configuration file not found: {str(fnf_error)}[/red]")
        ctx.exit(1)
    except json.JSONDecodeError as json_error:
        console.print(f"[red]❌ Error decoding JSON from configuration: {str(json_error)}[/red]")
        ctx.exit(1)
    except Exception as e:
        console.print(f"[red]❌ get_memory_system_status failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)

# Export command for CLI registration
__all__ = ["get_memory_system_status"]