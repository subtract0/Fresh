import click
from typing import Optional
from rich.console import Console
from rich.table import Table
from pathlib import Path
import json
import yaml

console = Console()

def load_config(config_path: str):
    with open(config_path, 'r') as file:
        return yaml.safe_load(file)

def add_numbers(numbers):
    return sum(numbers)

@click.command()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--output', '-o', type=click.Choice(['json', 'table', 'plain']), 
              default='table', help='Output format')
@click.option('--config', type=click.Path(exists=True), help='Configuration file')
@click.pass_context
def add_loop(ctx, verbose: bool, output: str, config: Optional[str]):
    """
    add_loop command to sum numbers from a configuration file or command line.
    """
    try:
        if verbose:
            console.print(f"[blue]Running add_loop command...[/blue]")
        
        numbers = []
        
        if config:
            config_data = load_config(config)
            if 'numbers' in config_data:
                numbers = config_data['numbers']
            else:
                raise ValueError("Configuration file must contain a 'numbers' key with a list of numbers.")
        else:
            raise ValueError("No configuration file provided. Please provide a valid config file.")

        if not all(isinstance(num, (int, float)) for num in numbers):
            raise ValueError("All items in the numbers list must be integers or floats.")

        result = add_numbers(numbers)
        
        result_data = {
            "feature": "add_loop",
            "status": "success", 
            "result": result,
            "config_used": config,
            "verbose": verbose
        }
        
        # Output results based on format
        if output == 'json':
            console.print_json(json.dumps(result_data, indent=2))
        elif output == 'table':
            table = Table(title=f"add_loop Results")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="magenta")
            
            for key, value in result_data.items():
                table.add_row(str(key), str(value))
            
            console.print(table)
        else:  # plain
            for key, value in result_data.items():
                console.print(f"{key}: {value}")
        
        if verbose:
            console.print(f"[green]✅ add_loop completed successfully[/green]")
            
    except Exception as e:
        console.print(f"[red]❌ add_loop failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)

# Export command for CLI registration
__all__ = ["add_loop"]