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

def validate_limit_config(config):
    if 'limit' not in config:
        raise ValueError("Configuration must include 'limit' key.")
    if not isinstance(config['limit'], (int, float)):
        raise ValueError("'limit' must be a number.")

@click.command()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--output', '-o', type=click.Choice(['json', 'table', 'plain']), 
              default='table', help='Output format')
@click.option('--config', type=click.Path(exists=True), help='Configuration file')
@click.pass_context
def limit(ctx, verbose: bool, output: str, config: Optional[str]):
    """
    limit command.
    This command sets a limit based on the provided configuration.
    """
    try:
        if verbose:
            console.print(f"[blue]Running limit command...[/blue]")
        
        limit_value = None
        
        if config:
            config_data = load_config(config)
            validate_limit_config(config_data)
            limit_value = config_data['limit']
            if verbose:
                console.print(f"[yellow]Loaded limit value: {limit_value}[/yellow]")
        else:
            raise ValueError("Configuration file is required.")
        
        result_data = {
            "feature": "limit",
            "status": "success", 
            "limit_value": limit_value,
            "config_used": config,
            "verbose": verbose
        }
        
        # Output results based on format
        if output == 'json':
            console.print_json(json.dumps(result_data, indent=2))
        elif output == 'table':
            table = Table(title=f"Limit Results")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="magenta")
            
            for key, value in result_data.items():
                table.add_row(str(key), str(value))
            
            console.print(table)
        else:  # plain
            for key, value in result_data.items():
                console.print(f"{key}: {value}")
        
        if verbose:
            console.print(f"[green]✅ limit completed successfully[/green]")
            
    except Exception as e:
        console.print(f"[red]❌ limit failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)

__all__ = ["limit"]