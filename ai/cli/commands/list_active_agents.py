import click
from typing import Optional
from rich.console import Console
from rich.table import Table
from pathlib import Path
import json
import os

console = Console()

def get_active_agents(config_path: Optional[str]):
    if config_path:
        if not Path(config_path).exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        with open(config_path, 'r') as f:
            config = json.load(f)
    else:
        config = {}

    # Simulated logic to retrieve active agents
    active_agents = config.get("active_agents", [])
    return active_agents

@click.command()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--output', '-o', type=click.Choice(['json', 'table', 'plain']), 
              default='table', help='Output format')
@click.option('--config', type=click.Path(exists=True), help='Configuration file')
@click.pass_context
def list_active_agents(ctx, verbose: bool, output: str, config: Optional[str]):
    """
    list_active_agents command.
    Lists all active agents based on the provided configuration.
    """
    try:
        if verbose:
            console.print(f"[blue]Running list_active_agents command...[/blue]")
        
        active_agents = get_active_agents(config)
        
        if not active_agents:
            result_data = {
                "feature": "list_active_agents",
                "status": "success", 
                "message": "No active agents found.",
                "config_used": config,
                "verbose": verbose
            }
        else:
            result_data = {
                "feature": "list_active_agents",
                "status": "success", 
                "active_agents": active_agents,
                "config_used": config,
                "verbose": verbose
            }
        
        # Output results based on format
        if output == 'json':
            console.print_json(json.dumps(result_data, indent=2))
        elif output == 'table':
            table = Table(title=f"list_active_agents Results")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="magenta")
            
            for key, value in result_data.items():
                if isinstance(value, list):
                    value = ', '.join(value)
                table.add_row(str(key), str(value))
            
            console.print(table)
        else:  # plain
            for key, value in result_data.items():
                if isinstance(value, list):
                    value = ', '.join(value)
                console.print(f"{key}: {value}")
        
        if verbose:
            console.print(f"[green]✅ list_active_agents completed successfully[/green]")
            
    except FileNotFoundError as fnf_error:
        console.print(f"[red]❌ list_active_agents failed: {str(fnf_error)}[/red]")
        ctx.exit(1)
    except json.JSONDecodeError as json_error:
        console.print(f"[red]❌ JSON decode error: {str(json_error)}[/red]")
        ctx.exit(1)
    except Exception as e:
        console.print(f"[red]❌ list_active_agents failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)

# Export command for CLI registration
__all__ = ["list_active_agents"]