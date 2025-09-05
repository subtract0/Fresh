import click
from typing import Optional
from rich.console import Console
from rich.table import Table
from pathlib import Path
import json
import os

console = Console()

def load_config(config_path: str):
    with open(config_path, 'r') as file:
        return json.load(file)

def spawn_new_agent(config):
    # Simulate agent spawning logic
    if 'agent_name' not in config or 'agent_type' not in config:
        raise ValueError("Configuration must include 'agent_name' and 'agent_type'.")
    
    # Here you would implement the actual logic to spawn the agent
    return {
        "agent_name": config['agent_name'],
        "agent_type": config['agent_type'],
        "status": "spawned"
    }

@click.command()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--output', '-o', type=click.Choice(['json', 'table', 'plain']), 
              default='table', help='Output format')
@click.option('--config', type=click.Path(exists=True), help='Configuration file', required=True)
@click.pass_context
def spawn_agent(ctx, verbose: bool, output: str, config: Optional[str]):
    """
    spawn_agent command.
    This command spawns a new agent based on the provided configuration.
    """
    try:
        if verbose:
            console.print(f"[blue]Running spawn_agent command...[/blue]")
        
        # Load configuration
        config_data = load_config(config)
        
        # Spawn the agent
        result_data = spawn_new_agent(config_data)
        
        # Output results based on format
        if output == 'json':
            console.print_json(json.dumps(result_data, indent=2))
        elif output == 'table':
            table = Table(title=f"spawn_agent Results")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="magenta")
            
            for key, value in result_data.items():
                table.add_row(str(key), str(value))
            
            console.print(table)
        else:  # plain
            for key, value in result_data.items():
                console.print(f"{key}: {value}")
        
        if verbose:
            console.print(f"[green]✅ spawn_agent completed successfully[/green]")
            
    except FileNotFoundError:
        console.print(f"[red]❌ Configuration file not found: {config}[/red]")
        ctx.exit(1)
    except json.JSONDecodeError:
        console.print(f"[red]❌ Error decoding JSON from configuration file: {config}[/red]")
        ctx.exit(1)
    except ValueError as ve:
        console.print(f"[red]❌ Configuration error: {str(ve)}[/red]")
        ctx.exit(1)
    except Exception as e:
        console.print(f"[red]❌ spawn_agent failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)

# Export command for CLI registration
__all__ = ["spawn_agent"]