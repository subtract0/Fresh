import click
from typing import Optional
from rich.console import Console
from rich.table import Table
from pathlib import Path
import json
import os

console = Console()

def load_inventory_data(config_path: str):
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    
    with open(config_path, 'r') as file:
        try:
            inventory_data = json.load(file)
        except json.JSONDecodeError as e:
            raise ValueError(f"Error decoding JSON from the configuration file: {str(e)}")
    
    return inventory_data

@click.command()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--output', '-o', type=click.Choice(['json', 'table', 'plain']), 
              default='table', help='Output format')
@click.option('--config', type=click.Path(exists=True), required=True, help='Configuration file')
@click.pass_context
def load_inventory(ctx, verbose: bool, output: str, config: Optional[str]):
    """
    Load inventory command.
    
    This command loads inventory data from a specified configuration file
    and displays it in the requested format.
    """
    try:
        if verbose:
            console.print(f"[blue]Running load_inventory command...[/blue]")
        
        inventory_data = load_inventory_data(config)
        
        # Output results based on format
        if output == 'json':
            console.print_json(json.dumps(inventory_data, indent=2))
        elif output == 'table':
            table = Table(title=f"Inventory Results")
            table.add_column("Item", style="cyan")
            table.add_column("Quantity", style="magenta")
            
            for item, quantity in inventory_data.items():
                table.add_row(str(item), str(quantity))
            
            console.print(table)
        else:  # plain
            for item, quantity in inventory_data.items():
                console.print(f"{item}: {quantity}")
        
        if verbose:
            console.print(f"[green]✅ load_inventory completed successfully[/green]")
            
    except Exception as e:
        console.print(f"[red]❌ load_inventory failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)

# Export command for CLI registration
__all__ = ["load_inventory"]