import click
from typing import Optional
from rich.console import Console
from rich.table import Table
from pathlib import Path
import json
import os

console = Console()

def load_config(config_path: str):
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    with open(config_path, 'r') as file:
        return json.load(file)

def perform_spawned_agent_logic(config):
    # Simulate some processing based on the configuration
    if 'agent_name' not in config:
        raise ValueError("Configuration must include 'agent_name'")
    return {
        "agent_name": config['agent_name'],
        "status": "success",
        "details": "SpawnedAgent executed successfully."
    }

@click.command()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--output', '-o', type=click.Choice(['json', 'table', 'plain']), 
              default='table', help='Output format')
@click.option('--config', type=click.Path(exists=True), help='Configuration file')
@click.pass_context
def spawnedagent(ctx, verbose: bool, output: str, config: Optional[str]):
    """
    SpawnedAgent command.
    This command spawns an agent based on the provided configuration.
    """
    try:
        if verbose:
            console.print(f"[blue]Running SpawnedAgent command...[/blue]")
        
        if config:
            config_data = load_config(config)
        else:
            raise ValueError("Configuration file must be provided.")

        result_data = perform_spawned_agent_logic(config_data)
        
        # Output results based on format
        if output == 'json':
            console.print_json(json.dumps(result_data, indent=2))
        elif output == 'table':
            table = Table(title=f"SpawnedAgent Results")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="magenta")
            
            for key, value in result_data.items():
                table.add_row(str(key), str(value))
            
            console.print(table)
        else:  # plain
            for key, value in result_data.items():
                console.print(f"{key}: {value}")
        
        if verbose:
            console.print(f"[green]✅ SpawnedAgent completed successfully[/green]")
            
    except FileNotFoundError as fnf_error:
        console.print(f"[red]❌ SpawnedAgent failed: {str(fnf_error)}[/red]")
        ctx.exit(1)
    except ValueError as val_error:
        console.print(f"[red]❌ SpawnedAgent failed: {str(val_error)}[/red]")
        ctx.exit(1)
    except Exception as e:
        console.print(f"[red]❌ SpawnedAgent failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)

__all__ = ["spawnedagent"]