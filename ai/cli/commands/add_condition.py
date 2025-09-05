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

def validate_condition(condition: dict):
    required_keys = ['name', 'type', 'value']
    for key in required_keys:
        if key not in condition:
            raise ValueError(f"Missing required condition key: {key}")

@click.command()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--output', '-o', type=click.Choice(['json', 'table', 'plain']), 
              default='table', help='Output format')
@click.option('--config', type=click.Path(exists=True), help='Configuration file')
@click.option('--condition', type=str, help='Condition to add in JSON format')
@click.pass_context
def add_condition(ctx, verbose: bool, output: str, config: Optional[str], condition: Optional[str]):
    """
    Add a new condition to the system.
    
    This command allows you to add a condition based on the provided configuration and condition details.
    """
    try:
        if verbose:
            console.print(f"[blue]Running add_condition command...[/blue]")
        
        if config:
            config_data = load_config(config)
            if verbose:
                console.print(f"[yellow]Loaded configuration: {config_data}[/yellow]")
        else:
            config_data = {}

        if condition:
            condition_data = json.loads(condition)
            validate_condition(condition_data)
        else:
            raise ValueError("Condition must be provided in JSON format.")

        # Simulate adding the condition (this would be replaced with actual logic)
        result_data = {
            "feature": "add_condition",
            "status": "success", 
            "message": "Condition added successfully",
            "condition": condition_data,
            "config_used": config_data,
            "verbose": verbose
        }
        
        # Output results based on format
        if output == 'json':
            console.print_json(json.dumps(result_data, indent=2))
        elif output == 'table':
            table = Table(title=f"add_condition Results")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="magenta")
            
            for key, value in result_data.items():
                table.add_row(str(key), str(value))
            
            console.print(table)
        else:  # plain
            for key, value in result_data.items():
                console.print(f"{key}: {value}")
        
        if verbose:
            console.print(f"[green]✅ add_condition completed successfully[/green]")
            
    except ValueError as ve:
        console.print(f"[red]❌ add_condition failed: {str(ve)}[/red]")
        ctx.exit(1)
    except Exception as e:
        console.print(f"[red]❌ add_condition failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)

__all__ = ["add_condition"]