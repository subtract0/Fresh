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
    with open(config_path, 'r') as f:
        return json.load(f)

def perform_emergency_stop(config):
    # Simulate emergency stop logic
    if config.get("emergency_stop_enabled", False):
        return {"status": "success", "message": "Emergency stop initiated."}
    else:
        return {"status": "failure", "message": "Emergency stop not enabled in configuration."}

@click.command()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--output', '-o', type=click.Choice(['json', 'table', 'plain']), 
              default='table', help='Output format')
@click.option('--config', type=click.Path(exists=True), help='Configuration file')
@click.pass_context
def cmd_autonomous_emergency_stop(ctx, verbose: bool, output: str, config: Optional[str]):
    """
    cmd_autonomous_emergency_stop command.
    Initiates an autonomous emergency stop based on the provided configuration.
    """
    try:
        if verbose:
            console.print(f"[blue]Running cmd_autonomous_emergency_stop command...[/blue]")
        
        if config is None:
            raise ValueError("Configuration file must be provided.")
        
        config_data = load_config(config)
        
        result = perform_emergency_stop(config_data)
        
        result_data = {
            "feature": "cmd_autonomous_emergency_stop",
            "status": result["status"],
            "message": result["message"],
            "config_used": config,
            "verbose": verbose
        }
        
        # Output results based on format
        if output == 'json':
            console.print_json(json.dumps(result_data, indent=2))
        elif output == 'table':
            table = Table(title=f"cmd_autonomous_emergency_stop Results")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="magenta")
            
            for key, value in result_data.items():
                table.add_row(str(key), str(value))
            
            console.print(table)
        else:  # plain
            for key, value in result_data.items():
                console.print(f"{key}: {value}")
        
        if verbose:
            console.print(f"[green]✅ cmd_autonomous_emergency_stop completed successfully[/green]")
            
    except Exception as e:
        console.print(f"[red]❌ cmd_autonomous_emergency_stop failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)

__all__ = ["cmd_autonomous_emergency_stop"]