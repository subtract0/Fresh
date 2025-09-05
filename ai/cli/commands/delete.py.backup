import click
from typing import Optional
from rich.console import Console
from rich.table import Table
from pathlib import Path
import json
import os

console = Console()

@click.command()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--output', '-o', type=click.Choice(['json', 'table', 'plain']), 
              default='table', help='Output format')
@click.option('--config', type=click.Path(exists=True), help='Configuration file')
@click.argument('target', type=click.Path(exists=True))
@click.pass_context
def delete(ctx, verbose: bool, output: str, config: Optional[str], target: str):
    """
    Delete a specified target file or directory.
    
    TARGET: The file or directory to delete.
    """
    try:
        if verbose:
            console.print(f"[blue]Running delete command on: {target}...[/blue]")
        
        # Validate target
        if not os.path.exists(target):
            raise FileNotFoundError(f"Target '{target}' does not exist.")
        
        # Perform delete operation
        if os.path.isdir(target):
            os.rmdir(target)
            action = "directory"
        else:
            os.remove(target)
            action = "file"
        
        result_data = {
            "feature": "delete",
            "status": "success", 
            "message": f"{action.capitalize()} '{target}' deleted successfully.",
            "config_used": config,
            "verbose": verbose
        }
        
        # Output results based on format
        if output == 'json':
            console.print_json(json.dumps(result_data, indent=2))
        elif output == 'table':
            table = Table(title=f"Delete Results")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="magenta")
            
            for key, value in result_data.items():
                table.add_row(str(key), str(value))
            
            console.print(table)
        else:  # plain
            for key, value in result_data.items():
                console.print(f"{key}: {value}")
        
        if verbose:
            console.print(f"[green]✅ Delete completed successfully[/green]")
            
    except FileNotFoundError as fnf_error:
        console.print(f"[red]❌ Delete failed: {str(fnf_error)}[/red]")
        ctx.exit(1)
    except PermissionError:
        console.print(f"[red]❌ Delete failed: Permission denied for '{target}'[/red]")
        ctx.exit(1)
    except Exception as e:
        console.print(f"[red]❌ Delete failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)

# Export command for CLI registration
__all__ = ["delete"]