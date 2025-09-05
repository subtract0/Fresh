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
def create(ctx, verbose: bool, output: Optional[str], config: Optional[str]):
    """
    Create a new resource based on the provided configuration.
    """
    try:
        if verbose:
            console.print(f"[blue]Running create command...[/blue]")
        
        # Load configuration if provided
        config_data = {}
        if config:
            with open(config, 'r') as f:
                config_data = json.load(f)
        
        # Validate configuration
        if not config_data.get('resource_name'):
            raise ValueError("Configuration must include 'resource_name'.")

        resource_name = config_data['resource_name']
        
        # Simulate resource creation logic
        # Here you would implement the actual logic to create the resource
        # For demonstration, we will just create a directory
        os.makedirs(resource_name, exist_ok=True)

        result_data = {
            "feature": "create",
            "status": "success", 
            "message": f"Resource '{resource_name}' created successfully.",
            "config_used": config,
            "verbose": verbose
        }
        
        # Output results based on format
        if output == 'json':
            console.print_json(json.dumps(result_data, indent=2))
        elif output == 'table':
            table = Table(title=f"Create Results")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="magenta")
            
            for key, value in result_data.items():
                table.add_row(str(key), str(value))
            
            console.print(table)
        else:  # plain
            for key, value in result_data.items():
                console.print(f"{key}: {value}")
        
        if verbose:
            console.print(f"[green]✅ create completed successfully[/green]")
            
    except FileNotFoundError as fnf_error:
        console.print(f"[red]❌ create failed: Configuration file not found: {str(fnf_error)}[/red]")
        ctx.exit(1)
    except ValueError as ve:
        console.print(f"[red]❌ create failed: {str(ve)}[/red]")
        ctx.exit(1)
    except Exception as e:
        console.print(f"[red]❌ create failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)

# Export command for CLI registration
__all__ = ["create"]