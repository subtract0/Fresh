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

def validate_config(config):
    required_keys = ['context_name', 'context_data']
    for key in required_keys:
        if key not in config:
            raise ValueError(f"Missing required key in config: {key}")

def register_context_logic(context_name: str, context_data: dict):
    # Simulate context registration logic
    # In a real application, this would involve saving to a database or similar
    return {
        "context_name": context_name,
        "context_data": context_data,
        "status": "registered"
    }

@click.command()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--output', '-o', type=click.Choice(['json', 'table', 'plain']), 
              default='table', help='Output format')
@click.option('--config', type=click.Path(exists=True), help='Configuration file')
@click.pass_context
def register_context(ctx, verbose: bool, output: str, config: Optional[str]):
    """
    Register a new context using the provided configuration file.
    """
    try:
        if verbose:
            console.print(f"[blue]Running register_context command...[/blue]")
        
        if not config:
            raise ValueError("Configuration file is required.")
        
        config_data = load_config(config)
        validate_config(config_data)

        context_name = config_data['context_name']
        context_data = config_data['context_data']

        result_data = register_context_logic(context_name, context_data)

        # Output results based on format
        if output == 'json':
            console.print_json(json.dumps(result_data, indent=2))
        elif output == 'table':
            table = Table(title=f"register_context Results")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="magenta")
            
            for key, value in result_data.items():
                table.add_row(str(key), str(value))
            
            console.print(table)
        else:  # plain
            for key, value in result_data.items():
                console.print(f"{key}: {value}")
        
        if verbose:
            console.print(f"[green]✅ register_context completed successfully[/green]")
            
    except Exception as e:
        console.print(f"[red]❌ register_context failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)

__all__ = ["register_context"]