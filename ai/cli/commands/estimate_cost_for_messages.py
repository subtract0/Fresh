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
    with open(config_path, 'r') as f:
        return json.load(f)

def estimate_cost(messages: list, cost_per_message: float) -> float:
    return len(messages) * cost_per_message

@click.command()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--output', '-o', type=click.Choice(['json', 'table', 'plain']), 
              default='table', help='Output format')
@click.option('--config', type=click.Path(exists=True), help='Configuration file')
@click.pass_context
def estimate_cost_for_messages(ctx, verbose: bool, output: str, config: Optional[str]):
    """
    estimate_cost_for_messages command.
    Estimates the cost for a given set of messages based on configuration.
    """
    try:
        if verbose:
            console.print(f"[blue]Running estimate_cost_for_messages command...[/blue]")
        
        # Load configuration
        config_data = load_config(config) if config else {}
        messages = config_data.get("messages", [])
        cost_per_message = config_data.get("cost_per_message", 0.0)

        if not messages:
            raise ValueError("No messages provided in the configuration.")
        
        total_cost = estimate_cost(messages, cost_per_message)
        
        result_data = {
            "feature": "estimate_cost_for_messages",
            "status": "success", 
            "total_cost": total_cost,
            "config_used": config,
            "verbose": verbose
        }
        
        # Output results based on format
        if output == 'json':
            console.print_json(json.dumps(result_data, indent=2))
        elif output == 'table':
            table = Table(title=f"estimate_cost_for_messages Results")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="magenta")
            
            for key, value in result_data.items():
                table.add_row(str(key), str(value))
            
            console.print(table)
        else:  # plain
            for key, value in result_data.items():
                console.print(f"{key}: {value}")
        
        if verbose:
            console.print(f"[green]✅ estimate_cost_for_messages completed successfully[/green]")
            
    except Exception as e:
        console.print(f"[red]❌ estimate_cost_for_messages failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)

__all__ = ["estimate_cost_for_messages"]