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

def process_tasks(config):
    # Simulate task processing based on the configuration
    if 'tasks' not in config:
        raise ValueError("Configuration must contain 'tasks' key.")
    
    results = []
    for task in config['tasks']:
        # Simulate processing each task
        results.append({
            "task": task,
            "status": "completed",
            "details": f"Processed task: {task}"
        })
    return results

@click.command()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--output', '-o', type=click.Choice(['json', 'table', 'plain']), 
              default='table', help='Output format')
@click.option('--config', type=click.Path(exists=True), help='Configuration file', required=True)
@click.pass_context
def handle_tasks_post(ctx, verbose: bool, output: str, config: Optional[str]):
    """
    handle_tasks_post command to process tasks defined in a configuration file.
    """
    try:
        if verbose:
            console.print(f"[blue]Running handle_tasks_post command...[/blue]")
        
        # Load configuration
        config_data = load_config(config)
        
        # Process tasks
        results = process_tasks(config_data)
        
        # Prepare output data
        result_data = {
            "feature": "handle_tasks_post",
            "status": "success", 
            "results": results,
            "config_used": config,
            "verbose": verbose
        }
        
        # Output results based on format
        if output == 'json':
            console.print_json(json.dumps(result_data, indent=2))
        elif output == 'table':
            table = Table(title=f"handle_tasks_post Results")
            table.add_column("Task", style="cyan")
            table.add_column("Status", style="magenta")
            table.add_column("Details", style="green")
            
            for result in results:
                table.add_row(result["task"], result["status"], result["details"])
            
            console.print(table)
        else:  # plain
            for result in results:
                console.print(f"Task: {result['task']}, Status: {result['status']}, Details: {result['details']}")
        
        if verbose:
            console.print(f"[green]✅ handle_tasks_post completed successfully[/green]")
            
    except FileNotFoundError:
        console.print(f"[red]❌ Configuration file not found: {config}[/red]")
        ctx.exit(1)
    except json.JSONDecodeError:
        console.print(f"[red]❌ Error decoding JSON from configuration file: {config}[/red]")
        ctx.exit(1)
    except ValueError as ve:
        console.print(f"[red]❌ Configuration error: {str(ve)}[/red]")
        ctx.exit(1)
    except Exception as e:
        console.print(f"[red]❌ handle_tasks_post failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)

# Export command for CLI registration
__all__ = ["handle_tasks_post"]