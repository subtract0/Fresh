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

def stop_autonomous_feature(config):
    # Simulate stopping an autonomous feature based on the configuration
    if 'feature_name' not in config:
        raise ValueError("Configuration must include 'feature_name'.")
    feature_name = config['feature_name']
    # Here you would add the logic to stop the feature
    return {"feature": feature_name, "status": "stopped"}

@click.command()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--output', '-o', type=click.Choice(['json', 'table', 'plain']), 
              default='table', help='Output format')
@click.option('--config', type=click.Path(exists=True), help='Configuration file', required=True)
@click.pass_context
def cmd_autonomous_stop(ctx, verbose: bool, output: str, config: Optional[str]):
    """
    cmd_autonomous_stop command.
    Stops the autonomous feature based on the provided configuration.
    """
    try:
        if verbose:
            console.print(f"[blue]Running cmd_autonomous_stop command...[/blue]")
        
        # Load configuration
        config_data = load_config(config)
        
        # Stop the autonomous feature
        result = stop_autonomous_feature(config_data)
        
        # Output results based on format
        if output == 'json':
            console.print_json(json.dumps(result, indent=2))
        elif output == 'table':
            table = Table(title=f"cmd_autonomous_stop Results")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="magenta")
            
            for key, value in result.items():
                table.add_row(str(key), str(value))
            
            console.print(table)
        else:  # plain
            for key, value in result.items():
                console.print(f"{key}: {value}")
        
        if verbose:
            console.print(f"[green]✅ cmd_autonomous_stop completed successfully[/green]")
            
    except FileNotFoundError:
        console.print(f"[red]❌ Configuration file not found: {config}[/red]")
        ctx.exit(1)
    except ValueError as ve:
        console.print(f"[red]❌ Value error: {str(ve)}[/red]")
        ctx.exit(1)
    except Exception as e:
        console.print(f"[red]❌ cmd_autonomous_stop failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)

# Export command for CLI registration
__all__ = ["cmd_autonomous_stop"]