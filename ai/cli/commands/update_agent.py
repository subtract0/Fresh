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

def update_agent_logic(config):
    # Simulate updating agent logic
    if 'agent_id' not in config:
        raise ValueError("Configuration must contain 'agent_id'")
    return {
        "agent_id": config['agent_id'],
        "status": "updated",
        "message": f"Agent {config['agent_id']} updated successfully."
    }

@click.command()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--output', '-o', type=click.Choice(['json', 'table', 'plain']), 
              default='table', help='Output format')
@click.option('--config', type=click.Path(exists=True), help='Configuration file')
@click.pass_context
def update_agent(ctx, verbose: bool, output: str, config: Optional[str]):
    """
    update_agent command.
    Updates the specified agent based on the provided configuration.
    """
    try:
        if verbose:
            console.print(f"[blue]Running update_agent command...[/blue]")
        
        if config is None:
            raise ValueError("Configuration file must be provided.")
        
        config_data = load_config(config)
        result_data = update_agent_logic(config_data)
        
        # Output results based on format
        if output == 'json':
            console.print_json(json.dumps(result_data, indent=2))
        elif output == 'table':
            table = Table(title=f"update_agent Results")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="magenta")
            
            for key, value in result_data.items():
                table.add_row(str(key), str(value))
            
            console.print(table)
        else:  # plain
            for key, value in result_data.items():
                console.print(f"{key}: {value}")
        
        if verbose:
            console.print(f"[green]✅ update_agent completed successfully[/green]")
            
    except FileNotFoundError:
        console.print(f"[red]❌ Configuration file not found: {config}[/red]")
        ctx.exit(1)
    except json.JSONDecodeError:
        console.print(f"[red]❌ Error decoding JSON from configuration file: {config}[/red]")
        ctx.exit(1)
    except ValueError as ve:
        console.print(f"[red]❌ Value error: {str(ve)}[/red]")
        ctx.exit(1)
    except Exception as e:
        console.print(f"[red]❌ update_agent failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)

# Export command for CLI registration
__all__ = ["update_agent"]