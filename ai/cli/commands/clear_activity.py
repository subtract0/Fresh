import click
from typing import Optional
from rich.console import Console
from rich.table import Table
from pathlib import Path
import json
import os

console = Console()

def clear_activity_logic(config_path: str):
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    
    with open(config_path, 'r') as config_file:
        config_data = json.load(config_file)
    
    # Simulate clearing activity based on config
    # Here you would implement the actual logic to clear activities
    # For demonstration, we will just return a success message
    return {
        "feature": "clear_activity",
        "status": "success",
        "message": "Activity cleared successfully",
        "config_used": config_path
    }

@click.command()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--output', '-o', type=click.Choice(['json', 'table', 'plain']), 
              default='table', help='Output format')
@click.option('--config', type=click.Path(exists=True), required=True, help='Configuration file')
@click.pass_context
def clear_activity(ctx, verbose: bool, output: str, config: str):
    """
    clear_activity command.
    
    Clears activities based on the provided configuration file.
    """
    try:
        if verbose:
            console.print(f"[blue]Running clear_activity command...[/blue]")
        
        result_data = clear_activity_logic(config)
        
        # Output results based on format
        if output == 'json':
            console.print_json(json.dumps(result_data, indent=2))
        elif output == 'table':
            table = Table(title=f"clear_activity Results")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="magenta")
            
            for key, value in result_data.items():
                table.add_row(str(key), str(value))
            
            console.print(table)
        else:  # plain
            for key, value in result_data.items():
                console.print(f"{key}: {value}")
        
        if verbose:
            console.print(f"[green]✅ clear_activity completed successfully[/green]")
            
    except FileNotFoundError as fnf_error:
        console.print(f"[red]❌ clear_activity failed: {str(fnf_error)}[/red]")
        ctx.exit(1)
    except json.JSONDecodeError as json_error:
        console.print(f"[red]❌ clear_activity failed: Invalid JSON in configuration file - {str(json_error)}[/red]")
        ctx.exit(1)
    except Exception as e:
        console.print(f"[red]❌ clear_activity failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)

# Export command for CLI registration
__all__ = ["clear_activity"]