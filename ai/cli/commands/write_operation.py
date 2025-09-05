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
def write_operation(ctx, verbose: bool, output: str, config: Optional[str]):
    """
    write_operation command.
    
    This command performs a write operation based on the provided configuration.
    """
    try:
        if verbose:
            console.print(f"[blue]Running write_operation command...[/blue]")
        
        # Load configuration if provided
        config_data = {}
        if config:
            with open(config, 'r') as f:
                config_data = json.load(f)
                if verbose:
                    console.print(f"[yellow]Loaded configuration: {config_data}[/yellow]")

        # Validate configuration
        if 'output_path' not in config_data:
            raise ValueError("Configuration must include 'output_path'.")

        output_path = Path(config_data['output_path'])
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Perform write operation
        with open(output_path, 'w') as f:
            f.write(json.dumps(config_data, indent=2))
        
        result_data = {
            "feature": "write_operation",
            "status": "success", 
            "message": f"Data written to {output_path}",
            "config_used": config,
            "verbose": verbose
        }
        
        # Output results based on format
        if output == 'json':
            console.print_json(json.dumps(result_data, indent=2))
        elif output == 'table':
            table = Table(title=f"write_operation Results")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="magenta")
            
            for key, value in result_data.items():
                table.add_row(str(key), str(value))
            
            console.print(table)
        else:  # plain
            for key, value in result_data.items():
                console.print(f"{key}: {value}")
        
        if verbose:
            console.print(f"[green]✅ write_operation completed successfully[/green]")
            
    except Exception as e:
        console.print(f"[red]❌ write_operation failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)

__all__ = ["write_operation"]