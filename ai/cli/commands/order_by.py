import click
from typing import Optional, List, Dict, Any
from rich.console import Console
from rich.table import Table
from pathlib import Path
import json
import yaml

console = Console()

def load_config(config_path: str) -> Dict[str, Any]:
    with open(config_path, 'r') as file:
        return yaml.safe_load(file)

def order_data(data: List[Dict[str, Any]], key: str, reverse: bool = False) -> List[Dict[str, Any]]:
    return sorted(data, key=lambda x: x.get(key), reverse=reverse)

@click.command()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--output', '-o', type=click.Choice(['json', 'table', 'plain']), 
              default='table', help='Output format')
@click.option('--config', type=click.Path(exists=True), help='Configuration file')
@click.option('--key', required=True, help='Key to order by')
@click.option('--reverse', is_flag=True, help='Order in descending order')
@click.pass_context
def order_by(ctx, verbose: bool, output: str, config: Optional[str], key: str, reverse: bool):
    """
    order_by command.
    
    Orders a list of items based on a specified key.
    """
    try:
        if verbose:
            console.print(f"[blue]Running order_by command...[/blue]")
        
        # Load configuration if provided
        config_data = {}
        if config:
            config_data = load_config(config)
            if verbose:
                console.print(f"[yellow]Loaded configuration from {config}[/yellow]")

        # Sample data for demonstration purposes
        data = config_data.get('data', [])
        if not isinstance(data, list):
            raise ValueError("Data in configuration must be a list.")

        # Perform ordering
        ordered_data = order_data(data, key, reverse)

        # Prepare result data
        result_data = {
            "feature": "order_by",
            "status": "success", 
            "ordered_data": ordered_data,
            "config_used": config,
            "verbose": verbose
        }
        
        # Output results based on format
        if output == 'json':
            console.print_json(json.dumps(result_data, indent=2))
        elif output == 'table':
            table = Table(title=f"order_by Results")
            table.add_column("Index", style="cyan")
            for item in ordered_data:
                table.add_row(str(ordered_data.index(item)), str(item))
            console.print(table)
        else:  # plain
            for index, item in enumerate(ordered_data):
                console.print(f"{index}: {item}")
        
        if verbose:
            console.print(f"[green]✅ order_by completed successfully[/green]")
            
    except Exception as e:
        console.print(f"[red]❌ order_by failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)

__all__ = ["order_by"]