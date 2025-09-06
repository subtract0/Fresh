import click
from typing import Optional
from rich.console import Console
from rich.table import Table
from pathlib import Path
import json
import os

console = Console()

def validate_config(config_path: str) -> dict:
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    with open(config_path, 'r') as file:
        return json.load(file)

def add_node_logic(config: dict) -> dict:
    # Simulate adding a node based on the configuration
    node_name = config.get("node_name")
    if not node_name:
        raise ValueError("Node name must be provided in the configuration.")
    
    # Here you would implement the actual logic to add a node
    # For demonstration, we will just return a success message
    return {
        "feature": "add_node",
        "status": "success",
        "message": f"Node '{node_name}' added successfully."
    }

@click.command()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--output', '-o', type=click.Choice(['json', 'table', 'plain']), 
              default='table', help='Output format')
@click.option('--config', type=click.Path(exists=True), help='Configuration file', required=True)
@click.pass_context
def add_node(ctx, verbose: bool, output: str, config: Optional[str]):
    """
    Add a new node based on the provided configuration.
    """
    try:
        if verbose:
            console.print(f"[blue]Running add_node command...[/blue]")
        
        config_data = validate_config(config)
        result_data = add_node_logic(config_data)
        
        # Output results based on format
        if output == 'json':
            console.print_json(json.dumps(result_data, indent=2))
        elif output == 'table':
            table = Table(title=f"add_node Results")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="magenta")
            
            for key, value in result_data.items():
                table.add_row(str(key), str(value))
            
            console.print(table)
        else:  # plain
            for key, value in result_data.items():
                console.print(f"{key}: {value}")
        
        if verbose:
            console.print(f"[green]✅ add_node completed successfully[/green]")
            
    except Exception as e:
        console.print(f"[red]❌ add_node failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)

# Export command for CLI registration
__all__ = ["add_node"]