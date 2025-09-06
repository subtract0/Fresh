import click
from typing import Optional
from rich.console import Console
from rich.table import Table
from pathlib import Path
import json
import os

console = Console()

def load_config(config_path: str):
    if not os.path.isfile(config_path):
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    with open(config_path, 'r') as file:
        return json.load(file)

def validate_config(config):
    required_keys = ['agent_name', 'agent_type', 'parameters']
    for key in required_keys:
        if key not in config:
            raise ValueError(f"Missing required configuration key: {key}")

@click.command()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--output', '-o', type=click.Choice(['json', 'table', 'plain']), 
              default='table', help='Output format')
@click.option('--config', type=click.Path(exists=True), help='Configuration file')
@click.pass_context
def agentconfig(ctx, verbose: bool, output: str, config: Optional[str]):
    """
    AgentConfig command.
    This command configures the agent based on the provided configuration file.
    """
    try:
        if verbose:
            console.print(f"[blue]Running AgentConfig command...[/blue]")
        
        if config:
            config_data = load_config(config)
            validate_config(config_data)
        else:
            raise ValueError("No configuration file provided.")
        
        result_data = {
            "feature": "AgentConfig",
            "status": "success", 
            "message": "Agent configuration loaded successfully",
            "config_used": config_data,
            "verbose": verbose
        }
        
        if output == 'json':
            console.print_json(json.dumps(result_data, indent=2))
        elif output == 'table':
            table = Table(title=f"AgentConfig Results")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="magenta")
            
            for key, value in result_data.items():
                table.add_row(str(key), str(value))
            
            console.print(table)
        else:  # plain
            for key, value in result_data.items():
                console.print(f"{key}: {value}")
        
        if verbose:
            console.print(f"[green]✅ AgentConfig completed successfully[/green]")
            
    except FileNotFoundError as fnf_error:
        console.print(f"[red]❌ AgentConfig failed: {str(fnf_error)}[/red]")
        ctx.exit(1)
    except ValueError as val_error:
        console.print(f"[red]❌ AgentConfig failed: {str(val_error)}[/red]")
        ctx.exit(1)
    except Exception as e:
        console.print(f"[red]❌ AgentConfig failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)

__all__ = ["agentconfig"]