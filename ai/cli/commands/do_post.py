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
def do_post(ctx, verbose: bool, output: Optional[str], config: Optional[str]):
    """
    do_POST command.
    
    This command sends a POST request to a specified endpoint with data from a configuration file.
    """
    try:
        if verbose:
            console.print(f"[blue]Running do_POST command...[/blue]")
        
        if config is None:
            raise ValueError("Configuration file must be provided.")
        
        with open(config, 'r') as f:
            config_data = json.load(f)
        
        url = config_data.get("url")
        data = config_data.get("data", {})
        
        if not url:
            raise ValueError("URL must be specified in the configuration file.")
        
        response = requests.post(url, json=data)
        response.raise_for_status()
        
        result_data = {
            "feature": "do_POST",
            "status": "success", 
            "response": response.json(),
            "config_used": config,
            "verbose": verbose
        }
        
        # Output results based on format
        if output == 'json':
            console.print_json(json.dumps(result_data, indent=2))
        elif output == 'table':
            table = Table(title=f"do_POST Results")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="magenta")
            
            for key, value in result_data.items():
                table.add_row(str(key), str(value))
            
            console.print(table)
        else:  # plain
            for key, value in result_data.items():
                console.print(f"{key}: {value}")
        
        if verbose:
            console.print(f"[green]✅ do_POST completed successfully[/green]")
            
    except requests.exceptions.RequestException as e:
        console.print(f"[red]❌ do_POST failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)
    except ValueError as ve:
        console.print(f"[red]❌ Configuration error: {str(ve)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)
    except Exception as e:
        console.print(f"[red]❌ do_POST failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)


# Export command for CLI registration
__all__ = ["do_post"]