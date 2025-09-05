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
def get_mcp_discovery(ctx, verbose: bool, output: str, config: Optional[str]):
    """
    get_mcp_discovery command.
    Fetches MCP discovery information from a specified endpoint.
    """
    try:
        if verbose:
            console.print(f"[blue]Running get_mcp_discovery command...[/blue]")
        
        # Load configuration if provided
        endpoint = None
        if config:
            with open(config, 'r') as f:
                config_data = json.load(f)
                endpoint = config_data.get("mcp_endpoint")
                if not endpoint:
                    raise ValueError("Configuration file must contain 'mcp_endpoint' key.")
        else:
            raise ValueError("Configuration file is required.")

        # Fetch MCP discovery data
        response = requests.get(endpoint)
        response.raise_for_status()  # Raise an error for bad responses
        result_data = response.json()

        # Output results based on format
        if output == 'json':
            console.print_json(json.dumps(result_data, indent=2))
        elif output == 'table':
            table = Table(title=f"MCP Discovery Results")
            table.add_column("Key", style="cyan")
            table.add_column("Value", style="magenta")
            
            for key, value in result_data.items():
                table.add_row(str(key), str(value))
            
            console.print(table)
        else:  # plain
            for key, value in result_data.items():
                console.print(f"{key}: {value}")
        
        if verbose:
            console.print(f"[green]✅ get_mcp_discovery completed successfully[/green]")
            
    except requests.exceptions.RequestException as e:
        console.print(f"[red]❌ get_mcp_discovery failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)
    except ValueError as ve:
        console.print(f"[red]❌ Configuration error: {str(ve)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)
    except Exception as e:
        console.print(f"[red]❌ get_mcp_discovery failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)

# Export command for CLI registration
__all__ = ["get_mcp_discovery"]