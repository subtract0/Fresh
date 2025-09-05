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

def clear_emergency(config):
    # Placeholder for actual emergency clearing logic
    # This should interact with the system to clear emergencies based on the config
    return {"status": "success", "message": "Emergency cleared successfully"}

@click.command()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--output', '-o', type=click.Choice(['json', 'table', 'plain']), 
              default='table', help='Output format')
@click.option('--config', type=click.Path(exists=True), help='Configuration file', required=True)
@click.pass_context
def cmd_autonomous_clear_emergency(ctx, verbose: bool, output: str, config: str):
    """
    cmd_autonomous_clear_emergency command.
    Clears any active emergencies based on the provided configuration.
    """
    try:
        if verbose:
            console.print(f"[blue]Running cmd_autonomous_clear_emergency command...[/blue]")
        
        # Load configuration
        config_data = load_config(config)
        
        # Validate configuration
        if 'emergency_threshold' not in config_data:
            raise ValueError("Configuration must include 'emergency_threshold'")

        # Execute the emergency clearing logic
        result = clear_emergency(config_data)
        
        # Prepare result data
        result_data = {
            "feature": "cmd_autonomous_clear_emergency",
            "status": result["status"],
            "message": result["message"],
            "config_used": config,
            "verbose": verbose
        }
        
        # Output results based on format
        if output == 'json':
            console.print_json(json.dumps(result_data, indent=2))
        elif output == 'table':
            table = Table(title=f"cmd_autonomous_clear_emergency Results")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="magenta")
            
            for key, value in result_data.items():
                table.add_row(str(key), str(value))
            
            console.print(table)
        else:  # plain
            for key, value in result_data.items():
                console.print(f"{key}: {value}")
        
        if verbose:
            console.print(f"[green]✅ cmd_autonomous_clear_emergency completed successfully[/green]")
            
    except Exception as e:
        console.print(f"[red]❌ cmd_autonomous_clear_emergency failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)

# Export command for CLI registration
__all__ = ["cmd_autonomous_clear_emergency"]