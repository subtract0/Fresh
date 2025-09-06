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

def validate_memory_operation(data):
    if not isinstance(data, dict):
        raise ValueError("Memory operation data must be a dictionary.")
    if 'operation' not in data or 'value' not in data:
        raise ValueError("Memory operation must include 'operation' and 'value' keys.")

def perform_memory_operation(operation: str, value: str):
    # Simulated memory operation logic
    if operation == "store":
        # Here you would implement the logic to store the value in memory
        return {"status": "success", "message": f"Stored value: {value}"}
    elif operation == "retrieve":
        # Here you would implement the logic to retrieve the value from memory
        return {"status": "success", "message": f"Retrieved value: {value}"}
    else:
        raise ValueError("Unsupported operation. Use 'store' or 'retrieve'.")

@click.command()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--output', '-o', type=click.Choice(['json', 'table', 'plain']), 
              default='table', help='Output format')
@click.option('--config', type=click.Path(exists=True), help='Configuration file')
@click.pass_context
def record_memory_operation(ctx, verbose: bool, output: str, config: Optional[str]):
    """
    record_memory_operation command.
    This command performs memory operations based on the provided configuration.
    """
    try:
        if verbose:
            console.print(f"[blue]Running record_memory_operation command...[/blue]")
        
        if config:
            config_data = load_config(config)
            validate_memory_operation(config_data)
            operation = config_data['operation']
            value = config_data['value']
        else:
            raise ValueError("Configuration file is required.")

        result = perform_memory_operation(operation, value)
        
        # Output results based on format
        result_data = {
            "feature": "record_memory_operation",
            "status": result['status'], 
            "message": result['message'],
            "config_used": config,
            "verbose": verbose
        }
        
        if output == 'json':
            console.print_json(json.dumps(result_data, indent=2))
        elif output == 'table':
            table = Table(title=f"record_memory_operation Results")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="magenta")
            
            for key, value in result_data.items():
                table.add_row(str(key), str(value))
            
            console.print(table)
        else:  # plain
            for key, value in result_data.items():
                console.print(f"{key}: {value}")
        
        if verbose:
            console.print(f"[green]✅ record_memory_operation completed successfully[/green]")
            
    except Exception as e:
        console.print(f"[red]❌ record_memory_operation failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)

# Export command for CLI registration
__all__ = ["record_memory_operation"]