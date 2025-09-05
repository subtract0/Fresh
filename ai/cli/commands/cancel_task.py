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

def cancel_task_logic(task_id: str, config: dict):
    # Simulate task cancellation logic
    if task_id not in config['tasks']:
        raise ValueError(f"Task ID {task_id} not found.")
    config['tasks'].remove(task_id)
    return {"task_id": task_id, "status": "cancelled"}

@click.command()
@click.option('--task-id', required=True, help='ID of the task to cancel')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--output', '-o', type=click.Choice(['json', 'table', 'plain']), 
              default='table', help='Output format')
@click.option('--config', type=click.Path(exists=True), help='Configuration file')
@click.pass_context
def cancel_task(ctx, task_id: str, verbose: bool, output: str, config: Optional[str]):
    """
    cancel_task command to cancel a specified task by ID.
    """
    try:
        if verbose:
            console.print(f"[blue]Running cancel_task command for task ID: {task_id}...[/blue]")
        
        if config is None:
            raise ValueError("Configuration file must be provided.")
        
        config_data = load_config(config)
        
        result_data = cancel_task_logic(task_id, config_data)
        
        # Output results based on format
        if output == 'json':
            console.print_json(json.dumps(result_data, indent=2))
        elif output == 'table':
            table = Table(title=f"cancel_task Results")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="magenta")
            
            for key, value in result_data.items():
                table.add_row(str(key), str(value))
            
            console.print(table)
        else:  # plain
            for key, value in result_data.items():
                console.print(f"{key}: {value}")
        
        if verbose:
            console.print(f"[green]✅ cancel_task completed successfully[/green]")
            
    except ValueError as ve:
        console.print(f"[red]❌ cancel_task failed: {str(ve)}[/red]")
        ctx.exit(1)
    except FileNotFoundError:
        console.print(f"[red]❌ Configuration file not found: {config}[/red]")
        ctx.exit(1)
    except Exception as e:
        console.print(f"[red]❌ cancel_task failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)

__all__ = ["cancel_task"]