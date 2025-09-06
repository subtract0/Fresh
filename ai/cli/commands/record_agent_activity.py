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

def validate_config(config):
    required_keys = ['agent_id', 'activity_log_path']
    for key in required_keys:
        if key not in config:
            raise ValueError(f"Missing required config key: {key}")

def log_activity(agent_id: str, activity: str, log_path: str):
    with open(log_path, 'a') as log_file:
        log_file.write(f"{agent_id}: {activity}\n")

@click.command()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--output', '-o', type=click.Choice(['json', 'table', 'plain']), 
              default='table', help='Output format')
@click.option('--config', type=click.Path(exists=True), help='Configuration file')
@click.pass_context
def record_agent_activity(ctx, verbose: bool, output: str, config: Optional[str]):
    """
    record_agent_activity command.
    Records the activity of an agent based on the provided configuration.
    """
    try:
        if verbose:
            console.print(f"[blue]Running record_agent_activity command...[/blue]")
        
        if not config:
            raise ValueError("Configuration file must be provided.")
        
        config_data = load_config(config)
        validate_config(config_data)

        agent_id = config_data['agent_id']
        activity_log_path = config_data['activity_log_path']
        
        # Simulate recording an activity
        activity = "Agent activity recorded successfully."
        log_activity(agent_id, activity, activity_log_path)

        result_data = {
            "feature": "record_agent_activity",
            "status": "success", 
            "message": activity,
            "config_used": config,
            "verbose": verbose
        }
        
        # Output results based on format
        if output == 'json':
            console.print_json(json.dumps(result_data, indent=2))
        elif output == 'table':
            table = Table(title=f"record_agent_activity Results")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="magenta")
            
            for key, value in result_data.items():
                table.add_row(str(key), str(value))
            
            console.print(table)
        else:  # plain
            for key, value in result_data.items():
                console.print(f"{key}: {value}")
        
        if verbose:
            console.print(f"[green]✅ record_agent_activity completed successfully[/green]")
            
    except Exception as e:
        console.print(f"[red]❌ record_agent_activity failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)

__all__ = ["record_agent_activity"]