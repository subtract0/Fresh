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

def get_agent_status(config):
    # Simulated logic for getting agent status
    return {
        "agent_id": config.get("agent_id", "unknown"),
        "status": "active",
        "last_check": "2023-10-01T12:00:00Z",
        "details": "Agent is running smoothly."
    }

@click.command()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--output', '-o', type=click.Choice(['json', 'table', 'plain']), 
              default='table', help='Output format')
@click.option('--config', type=click.Path(exists=True), help='Configuration file')
@click.pass_context
def agentstatus(ctx, verbose: bool, output: str, config: Optional[str]):
    """
    AgentStatus command.
    Retrieves the status of the agent based on the provided configuration.
    """
    try:
        if verbose:
            console.print(f"[blue]Running AgentStatus command...[/blue]")
        
        if config is None:
            raise ValueError("Configuration file must be provided.")
        
        config_data = load_config(config)
        agent_status = get_agent_status(config_data)
        
        # Output results based on format
        if output == 'json':
            console.print_json(json.dumps(agent_status, indent=2))
        elif output == 'table':
            table = Table(title=f"AgentStatus Results")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="magenta")
            
            for key, value in agent_status.items():
                table.add_row(str(key), str(value))
            
            console.print(table)
        else:  # plain
            for key, value in agent_status.items():
                console.print(f"{key}: {value}")
        
        if verbose:
            console.print(f"[green]✅ AgentStatus completed successfully[/green]")
            
    except FileNotFoundError as fnf_error:
        console.print(f"[red]❌ Error: {str(fnf_error)}[/red]")
        ctx.exit(1)
    except ValueError as val_error:
        console.print(f"[red]❌ Error: {str(val_error)}[/red]")
        ctx.exit(1)
    except Exception as e:
        console.print(f"[red]❌ AgentStatus failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)

# Export command for CLI registration
__all__ = ["agentstatus"]