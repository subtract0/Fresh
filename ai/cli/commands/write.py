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
def write(ctx, verbose: bool, output: str, config: Optional[str]):
    """
    Write command to save data to a file with validation and logging.
    """
    try:
        if verbose:
            console.print(f"[blue]Running write command...[/blue]")
        
        if config is None:
            raise ValueError("Configuration file must be provided.")
        
        config_path = Path(config)
        if not config_path.is_file():
            raise FileNotFoundError(f"Configuration file '{config}' does not exist.")
        
        with open(config_path, 'r') as f:
            config_data = json.load(f)
        
        if 'data' not in config_data:
            raise ValueError("Configuration must contain 'data' key.")
        
        output_file = config_data.get('output_file', 'output.json')
        output_path = Path(output_file)
        
        with open(output_path, 'w') as f:
            json.dump(config_data['data'], f, indent=2)
        
        result_data = {
            "feature": "write",
            "status": "success", 
            "message": f"Data written to {output_file}",
            "config_used": config,
            "verbose": verbose
        }
        
        if output == 'json':
            console.print_json(json.dumps(result_data, indent=2))
        elif output == 'table':
            table = Table(title=f"Write Results")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="magenta")
            
            for key, value in result_data.items():
                table.add_row(str(key), str(value))
            
            console.print(table)
        else:  # plain
            for key, value in result_data.items():
                console.print(f"{key}: {value}")
        
        if verbose:
            console.print(f"[green]✅ Write completed successfully[/green]")
            
    except Exception as e:
        console.print(f"[red]❌ Write failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)


# Export command for CLI registration
__all__ = ["write"]