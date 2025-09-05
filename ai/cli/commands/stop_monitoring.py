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

def stop_monitoring_logic(config):
    # Placeholder for actual stop monitoring logic
    # This should contain the logic to stop monitoring based on the configuration
    if 'monitoring_service' not in config:
        raise ValueError("Configuration must include 'monitoring_service'")
    # Simulate stopping the monitoring service
    return {"status": "stopped", "service": config['monitoring_service']}

@click.command()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--output', '-o', type=click.Choice(['json', 'table', 'plain']), 
              default='table', help='Output format')
@click.option('--config', type=click.Path(exists=True), help='Configuration file', required=True)
@click.pass_context
def stop_monitoring(ctx, verbose: bool, output: str, config: Optional[str]):
    """
    stop_monitoring command.
    Stops the monitoring service based on the provided configuration.
    """
    try:
        if verbose:
            console.print(f"[blue]Running stop_monitoring command...[/blue]")
        
        config_data = load_config(config)
        result = stop_monitoring_logic(config_data)
        
        result_data = {
            "feature": "stop_monitoring",
            "status": "success", 
            "message": "Monitoring service stopped successfully",
            "service": result['service'],
            "verbose": verbose
        }
        
        # Output results based on format
        if output == 'json':
            console.print_json(json.dumps(result_data, indent=2))
        elif output == 'table':
            table = Table(title=f"stop_monitoring Results")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="magenta")
            
            for key, value in result_data.items():
                table.add_row(str(key), str(value))
            
            console.print(table)
        else:  # plain
            for key, value in result_data.items():
                console.print(f"{key}: {value}")
        
        if verbose:
            console.print(f"[green]✅ stop_monitoring completed successfully[/green]")
            
    except FileNotFoundError:
        console.print(f"[red]❌ Configuration file not found: {config}[/red]")
        ctx.exit(1)
    except ValueError as ve:
        console.print(f"[red]❌ Configuration error: {str(ve)}[/red]")
        ctx.exit(1)
    except Exception as e:
        console.print(f"[red]❌ stop_monitoring failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)

# Export command for CLI registration
__all__ = ["stop_monitoring"]