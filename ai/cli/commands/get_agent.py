import click
from typing import Optional
from rich.console import Console
from rich.table import Table
from pathlib import Path
import json
import os

console = Console()

def load_config(config_path: str):
    with open(config_path, 'r') as f:
        return json.load(f)

def get_agent_data(config):
    # Simulate fetching agent data based on the configuration
    # In a real implementation, this would involve API calls or database queries
    return {
        "agent_id": config.get("agent_id", "default_id"),
        "agent_name": config.get("agent_name", "default_name"),
        "status": "active",
        "last_seen": "2023-10-01T12:00:00Z"
    }

@click.command()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--output', '-o', type=click.Choice(['json', 'table', 'plain']), 
              default='table', help='Output format')
@click.option('--config', type=click.Path(exists=True), help='Configuration file')
@click.pass_context
def get_agent(ctx, verbose: bool, output: str, config: Optional[str]):
    """
    get_agent command.
    Fetches agent information based on the provided configuration.
    """
    try:
        if verbose:
            console.print(f"[blue]Running get_agent command...[/blue]")
        
        if config is None:
            console.print(f"[red]❌ Configuration file is required.[/red]")
            ctx.exit(1)

        config_data = load_config(config)
        
        if verbose:
            console.print(f"[blue]Loaded configuration: {config_data}[/blue]")
        
        agent_data = get_agent_data(config_data)
        
        # Output results based on format
        if output == 'json':
            console.print_json(json.dumps(agent_data, indent=2))
        elif output == 'table':
            table = Table(title=f"get_agent Results")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="magenta")
            
            for key, value in agent_data.items():
                table.add_row(str(key), str(value))
            
            console.print(table)
        else:  # plain
            for key, value in agent_data.items():
                console.print(f"{key}: {value}")
        
        if verbose:
            console.print(f"[green]✅ get_agent completed successfully[/green]")
            
    except FileNotFoundError:
        console.print(f"[red]❌ Configuration file not found: {config}[/red]")
        ctx.exit(1)
    except json.JSONDecodeError:
        console.print(f"[red]❌ Error decoding JSON from configuration file.[/red]")
        ctx.exit(1)
    except Exception as e:
        console.print(f"[red]❌ get_agent failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)

# Export command for CLI registration
__all__ = ["get_agent"]