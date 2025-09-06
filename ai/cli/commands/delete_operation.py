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
@click.argument('resource_id', type=str)
@click.pass_context
def delete_operation(ctx, verbose: bool, output: str, config: Optional[str], resource_id: str):
    """
    delete_operation command.
    
    Deletes a resource identified by resource_id.
    """
    try:
        if verbose:
            console.print(f"[blue]Running delete_operation command for resource_id: {resource_id}...[/blue]")
        
        # Load configuration if provided
        config_data = {}
        if config:
            with open(config, 'r') as f:
                config_data = json.load(f)
        
        # Validate resource_id
        if not resource_id:
            raise ValueError("resource_id must be provided.")
        
        # Simulate delete operation (replace with actual delete logic)
        resource_path = Path(config_data.get("resource_directory", ".")) / resource_id
        if not resource_path.exists():
            raise FileNotFoundError(f"Resource '{resource_id}' not found.")
        
        os.remove(resource_path)
        
        result_data = {
            "feature": "delete_operation",
            "status": "success", 
            "message": f"Resource '{resource_id}' deleted successfully.",
            "config_used": config,
            "verbose": verbose
        }
        
        # Output results based on format
        if output == 'json':
            console.print_json(json.dumps(result_data, indent=2))
        elif output == 'table':
            table = Table(title=f"delete_operation Results")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="magenta")
            
            for key, value in result_data.items():
                table.add_row(str(key), str(value))
            
            console.print(table)
        else:  # plain
            for key, value in result_data.items():
                console.print(f"{key}: {value}")
        
        if verbose:
            console.print(f"[green]✅ delete_operation completed successfully[/green]")
            
    except Exception as e:
        console.print(f"[red]❌ delete_operation failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)

# Export command for CLI registration
__all__ = ["delete_operation"]