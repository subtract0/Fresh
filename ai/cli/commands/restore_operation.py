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

def restore_data(config):
    # Simulate restore operation logic
    if 'backup_path' not in config:
        raise ValueError("Configuration must include 'backup_path'")
    
    backup_path = config['backup_path']
    if not os.path.exists(backup_path):
        raise FileNotFoundError(f"Backup path '{backup_path}' does not exist.")
    
    # Simulated restore operation
    return {"status": "success", "restored_files": ["file1.txt", "file2.txt"]}

@click.command()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--output', '-o', type=click.Choice(['json', 'table', 'plain']), 
              default='table', help='Output format')
@click.option('--config', type=click.Path(exists=True), help='Configuration file', required=True)
@click.pass_context
def restore_operation(ctx, verbose: bool, output: str, config: Optional[str]):
    """
    restore_operation command.
    This command restores data from a backup based on the provided configuration.
    """
    try:
        if verbose:
            console.print(f"[blue]Running restore_operation command...[/blue]")
        
        config_data = load_config(config)
        result_data = restore_data(config_data)
        
        # Output results based on format
        if output == 'json':
            console.print_json(json.dumps(result_data, indent=2))
        elif output == 'table':
            table = Table(title=f"restore_operation Results")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="magenta")
            
            for key, value in result_data.items():
                table.add_row(str(key), str(value))
            
            console.print(table)
        else:  # plain
            for key, value in result_data.items():
                console.print(f"{key}: {value}")
        
        if verbose:
            console.print(f"[green]✅ restore_operation completed successfully[/green]")
            
    except FileNotFoundError as fnf_error:
        console.print(f"[red]❌ restore_operation failed: {str(fnf_error)}[/red]")
        ctx.exit(1)
    except ValueError as val_error:
        console.print(f"[red]❌ restore_operation failed: {str(val_error)}[/red]")
        ctx.exit(1)
    except Exception as e:
        console.print(f"[red]❌ restore_operation failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)

# Export command for CLI registration
__all__ = ["restore_operation"]