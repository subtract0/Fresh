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
@click.argument('items', nargs=-1)
@click.pass_context
def add(ctx, verbose: bool, output: str, config: Optional[str], items: tuple):
    """
    Add command to add items to a list.
    
    This command takes a list of items and adds them to a specified configuration.
    """
    try:
        if verbose:
            console.print(f"[blue]Running add command...[/blue]")
        
        if not items:
            raise ValueError("No items provided to add.")
        
        if config:
            config_path = Path(config)
            if not config_path.is_file():
                raise FileNotFoundError(f"Configuration file '{config}' does not exist.")
            with open(config_path, 'r') as f:
                config_data = json.load(f)
        else:
            config_data = {}

        if 'items' not in config_data:
            config_data['items'] = []

        config_data['items'].extend(items)

        if config:
            with open(config_path, 'w') as f:
                json.dump(config_data, f, indent=2)

        result_data = {
            "feature": "add",
            "status": "success", 
            "message": f"Added {len(items)} items.",
            "config_used": config,
            "items_added": items,
            "verbose": verbose
        }
        
        # Output results based on format
        if output == 'json':
            console.print_json(json.dumps(result_data, indent=2))
        elif output == 'table':
            table = Table(title=f"Add Results")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="magenta")
            
            for key, value in result_data.items():
                table.add_row(str(key), str(value))
            
            console.print(table)
        else:  # plain
            for key, value in result_data.items():
                console.print(f"{key}: {value}")
        
        if verbose:
            console.print(f"[green]✅ Add completed successfully[/green]")
            
    except Exception as e:
        console.print(f"[red]❌ Add failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)

__all__ = ["add"]