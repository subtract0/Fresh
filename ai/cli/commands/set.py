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
@click.pass_context
def set(ctx, verbose: bool, output: str, config: Optional[str]):
    """
    set command.
    
    This command allows you to set configurations based on the provided configuration file.
    """
    try:
        if verbose:
            console.print(f"[blue]Running set command...[/blue]")
        
        if config is None:
            raise ValueError("Configuration file must be provided.")
        
        if not Path(config).is_file():
            raise FileNotFoundError(f"Configuration file '{config}' does not exist.")
        
        with open(config, 'r') as f:
            config_data = json.load(f)

        # Validate configuration data
        if not isinstance(config_data, dict):
            raise ValueError("Configuration data must be a JSON object.")
        
        # Simulate setting configurations (this is where the actual logic would go)
        # For demonstration, we just print the configurations
        result_data = {
            "feature": "set",
            "status": "success", 
            "message": "Configuration set successfully",
            "config_used": config_data,
            "verbose": verbose
        }
        
        # Output results based on format
        if output == 'json':
            console.print_json(json.dumps(result_data, indent=2))
        elif output == 'table':
            table = Table(title=f"set Results")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="magenta")
            
            for key, value in result_data.items():
                table.add_row(str(key), str(value))
            
            console.print(table)
        else:  # plain
            for key, value in result_data.items():
                console.print(f"{key}: {value}")
        
        if verbose:
            console.print(f"[green]✅ set completed successfully[/green]")
            
    except Exception as e:
        console.print(f"[red]❌ set failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)

__all__ = ["set"]