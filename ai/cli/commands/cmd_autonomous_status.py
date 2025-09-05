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

def get_autonomous_status(config):
    # Simulated logic for getting autonomous status
    # In a real implementation, this would interface with the actual system
    return {
        "status": "operational",
        "details": {
            "uptime": "72 hours",
            "last_check": "2023-10-01T12:00:00Z",
            "issues": []
        }
    }

@click.command()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--output', '-o', type=click.Choice(['json', 'table', 'plain']), 
              default='table', help='Output format')
@click.option('--config', type=click.Path(exists=True), help='Configuration file')
@click.pass_context
def cmd_autonomous_status(ctx, verbose: bool, output: str, config: Optional[str]):
    """
    cmd_autonomous_status command.
    Retrieves and displays the status of the autonomous system.
    """
    try:
        if verbose:
            console.print(f"[blue]Running cmd_autonomous_status command...[/blue]")
        
        config_data = load_config(config) if config else {}
        status_data = get_autonomous_status(config_data)
        
        result_data = {
            "feature": "cmd_autonomous_status",
            "status": status_data["status"],
            "details": status_data["details"],
            "config_used": config,
            "verbose": verbose
        }
        
        # Output results based on format
        if output == 'json':
            console.print_json(json.dumps(result_data, indent=2))
        elif output == 'table':
            table = Table(title=f"cmd_autonomous_status Results")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="magenta")
            
            for key, value in result_data.items():
                if isinstance(value, dict):
                    value = json.dumps(value)
                table.add_row(str(key), str(value))
            
            console.print(table)
        else:  # plain
            for key, value in result_data.items():
                if isinstance(value, dict):
                    value = json.dumps(value)
                console.print(f"{key}: {value}")
        
        if verbose:
            console.print(f"[green]✅ cmd_autonomous_status completed successfully[/green]")
            
    except FileNotFoundError as fnf_error:
        console.print(f"[red]❌ {str(fnf_error)}[/red]")
        ctx.exit(1)
    except json.JSONDecodeError as json_error:
        console.print(f"[red]❌ JSON decode error: {str(json_error)}[/red]")
        ctx.exit(1)
    except Exception as e:
        console.print(f"[red]❌ cmd_autonomous_status failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)

# Export command for CLI registration
__all__ = ["cmd_autonomous_status"]