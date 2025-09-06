import click
from typing import Optional
from rich.console import Console
from rich.table import Table
from pathlib import Path
import json
import os

console = Console()

def load_config(config_path: str) -> dict:
    """
    Load configuration from a JSON file.

    Args:
        config_path (str): Path to the configuration file.

    Returns:
        dict: Parsed JSON configuration data.

    Raises:
        FileNotFoundError: If the configuration file does not exist.
        json.JSONDecodeError: If the configuration file is not valid JSON.
    """
    with open(config_path, 'r') as file:
        return json.load(file)

def get_agent_spawner_logic(config: dict) -> dict:
    """
    Retrieve agent spawner details based on the provided configuration.

    Args:
        config (dict): Configuration data.

    Returns:
        dict: Agent spawner details including agent name, spawner type, and status.
    """
    return {
        "agent_name": config.get("agent_name", "default_agent"),
        "spawner_type": config.get("spawner_type", "default_spawner"),
        "status": "active"
    }

@click.command()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--output', '-o', type=click.Choice(['json', 'table', 'plain']), 
              default='table', help='Output format')
@click.option('--config', type=click.Path(exists=True), help='Configuration file')
@click.pass_context
def get_agent_spawner(ctx, verbose: bool, output: str, config: Optional[str]):
    """
    get_agent_spawner command.
    Retrieves agent spawner information based on the provided configuration.

    Args:
        ctx: Click context.
        verbose (bool): Flag to enable verbose output.
        output (str): Desired output format.
        config (Optional[str]): Path to the configuration file.
    """
    try:
        if verbose:
            console.print(f"[blue]Running get_agent_spawner command...[/blue]")
        
        if config is None:
            raise ValueError("Configuration file must be provided.")
        
        config_data = load_config(config)
        
        if verbose:
            console.print(f"[blue]Loaded configuration: {config_data}[/blue]")
        
        result_data = get_agent_spawner_logic(config_data)
        
        # Output results based on format
        if output == 'json':
            console.print_json(json.dumps(result_data, indent=2))
        elif output == 'table':
            table = Table(title=f"get_agent_spawner Results")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="magenta")
            
            for key, value in result_data.items():
                table.add_row(str(key), str(value))
            
            console.print(table)
        else:  # plain
            for key, value in result_data.items():
                console.print(f"{key}: {value}")
        
        if verbose:
            console.print(f"[green]✅ get_agent_spawner completed successfully[/green]")
            
    except FileNotFoundError:
        console.print(f"[red]❌ Configuration file not found: {config}[/red]")
        ctx.exit(1)
    except json.JSONDecodeError:
        console.print(f"[red]❌ Error decoding JSON from configuration file: {config}[/red]")
        ctx.exit(1)
    except ValueError as ve:
        console.print(f"[red]❌ {str(ve)}[/red]")
        ctx.exit(1)
    except Exception as e:
        console.print(f"[red]❌ get_agent_spawner failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)

__all__ = ["get_agent_spawner"]