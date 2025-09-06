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

@click.command()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--output', '-o', type=click.Choice(['json', 'table', 'plain']), 
              default='table', help='Output format')
@click.option('--config', type=click.Path(exists=True), help='Configuration file')
@click.pass_context
def allowed_task(ctx, verbose: bool, output: str, config: Optional[str]):
    """
    allowed_task command.
    This command checks the allowed tasks based on the provided configuration.
    """
    try:
        if verbose:
            console.print(f"[blue]Running allowed_task command...[/blue]")
        
        config_data = {}
        if config:
            config_data = load_config(config)
            if verbose:
                console.print(f"[blue]Loaded configuration: {config_data}[/blue]")

        # Business logic to determine allowed tasks
        allowed_tasks = config_data.get("allowed_tasks", [])
        if not allowed_tasks:
            raise ValueError("No allowed tasks found in the configuration.")

        result_data = {
            "feature": "allowed_task",
            "status": "success", 
            "allowed_tasks": allowed_tasks,
            "config_used": config,
            "verbose": verbose
        }
        
        # Output results based on format
        if output == 'json':
            console.print_json(json.dumps(result_data, indent=2))
        elif output == 'table':
            table = Table(title=f"allowed_task Results")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="magenta")
            
            for key, value in result_data.items():
                table.add_row(str(key), str(value))
            
            console.print(table)
        else:  # plain
            for key, value in result_data.items():
                console.print(f"{key}: {value}")
        
        if verbose:
            console.print(f"[green]✅ allowed_task completed successfully[/green]")
            
    except FileNotFoundError as fnf_error:
        console.print(f"[red]❌ allowed_task failed: {str(fnf_error)}[/red]")
        ctx.exit(1)
    except ValueError as val_error:
        console.print(f"[red]❌ allowed_task failed: {str(val_error)}[/red]")
        ctx.exit(1)
    except Exception as e:
        console.print(f"[red]❌ allowed_task failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)

# Export command for CLI registration
__all__ = ["allowed_task"]