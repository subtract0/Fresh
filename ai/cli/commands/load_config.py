import click
from typing import Optional
from rich.console import Console
from rich.table import Table
from pathlib import Path
import json

console = Console()

def load_configuration(file_path: str):
    with open(file_path, 'r') as file:
        return json.load(file)

@click.command()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--output', '-o', type=click.Choice(['json', 'table', 'plain']), 
              default='table', help='Output format')
@click.option('--config', type=click.Path(exists=True, dir_okay=False, readable=True), 
              required=True, help='Configuration file')
@click.pass_context
def load_config(ctx, verbose: bool, output: str, config: str):
    """
    Load configuration from a specified JSON file and display the results.
    """
    try:
        if verbose:
            console.print(f"[blue]Running load_config command...[/blue]")
        
        # Load the configuration
        config_data = load_configuration(config)

        # Prepare result data
        result_data = {
            "feature": "load_config",
            "status": "success", 
            "config_used": config,
            "config_data": config_data,
            "verbose": verbose
        }
        
        # Output results based on format
        if output == 'json':
            console.print_json(json.dumps(result_data, indent=2))
        elif output == 'table':
            table = Table(title=f"load_config Results")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="magenta")
            
            for key, value in result_data.items():
                if isinstance(value, dict):
                    value = json.dumps(value, indent=2)
                table.add_row(str(key), str(value))
            
            console.print(table)
        else:  # plain
            for key, value in result_data.items():
                if isinstance(value, dict):
                    value = json.dumps(value, indent=2)
                console.print(f"{key}: {value}")
        
        if verbose:
            console.print(f"[green]✅ load_config completed successfully[/green]")
            
    except FileNotFoundError:
        console.print(f"[red]❌ Configuration file not found: {config}[/red]")
        ctx.exit(1)
    except json.JSONDecodeError:
        console.print(f"[red]❌ Failed to parse JSON from configuration file: {config}[/red]")
        ctx.exit(1)
    except Exception as e:
        console.print(f"[red]❌ load_config failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)

# Export command for CLI registration
__all__ = ["load_config"]