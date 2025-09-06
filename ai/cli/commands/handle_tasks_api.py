import click
from typing import Optional
from rich.console import Console
from rich.table import Table
from pathlib import Path
import json
import requests

console = Console()

@click.command()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--output', '-o', type=click.Choice(['json', 'table', 'plain']), 
              default='table', help='Output format')
@click.option('--config', type=click.Path(exists=True), help='Configuration file')
@click.pass_context
def handle_tasks_api(ctx, verbose: bool, output: str, config: Optional[str]):
    """
    handle_tasks_api command.
    
    This command interacts with the handle tasks API to perform operations
    based on the provided configuration.
    """
    try:
        if verbose:
            console.print(f"[blue]Running handle_tasks_api command...[/blue]")
        
        # Load configuration if provided
        config_data = {}
        if config:
            with open(config, 'r') as f:
                config_data = json.load(f)
                if verbose:
                    console.print(f"[yellow]Loaded configuration: {config_data}[/yellow]")

        # Validate required configuration parameters
        if 'api_url' not in config_data:
            raise ValueError("Configuration must include 'api_url'.")

        # Call the handle tasks API
        response = requests.post(config_data['api_url'], json=config_data.get('payload', {}))
        response.raise_for_status()  # Raise an error for bad responses

        result_data = response.json()
        result_data['feature'] = "handle_tasks_api"
        result_data['status'] = "success"
        result_data['config_used'] = config
        result_data['verbose'] = verbose
        
        # Output results based on format
        if output == 'json':
            console.print_json(json.dumps(result_data, indent=2))
        elif output == 'table':
            table = Table(title=f"handle_tasks_api Results")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="magenta")
            
            for key, value in result_data.items():
                table.add_row(str(key), str(value))
            
            console.print(table)
        else:  # plain
            for key, value in result_data.items():
                console.print(f"{key}: {value}")
        
        if verbose:
            console.print(f"[green]✅ handle_tasks_api completed successfully[/green]")
            
    except requests.exceptions.RequestException as e:
        console.print(f"[red]❌ handle_tasks_api failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)
    except ValueError as ve:
        console.print(f"[red]❌ Configuration error: {str(ve)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)
    except Exception as e:
        console.print(f"[red]❌ handle_tasks_api failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)

# Export command for CLI registration
__all__ = ["handle_tasks_api"]