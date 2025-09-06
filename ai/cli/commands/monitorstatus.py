import click
from typing import Optional
from rich.console import Console
from rich.table import Table
from pathlib import Path
import json
import os

console = Console()

def load_config(config_path: str):
    if config_path and Path(config_path).exists():
        with open(config_path, 'r') as f:
            return json.load(f)
    else:
        raise FileNotFoundError(f"Configuration file not found: {config_path}")

def check_service_status(service_name: str):
    # Simulated service status check
    # In a real implementation, this would check the actual service status
    return {"service": service_name, "status": "running"}

@click.command()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--output', '-o', type=click.Choice(['json', 'table', 'plain']), 
              default='table', help='Output format')
@click.option('--config', type=click.Path(exists=True), help='Configuration file')
@click.pass_context
def monitorstatus(ctx, verbose: bool, output: str, config: Optional[str]):
    """
    MonitorStatus command.
    Checks the status of services defined in the configuration file.
    """
    try:
        if verbose:
            console.print(f"[blue]Running MonitorStatus command...[/blue]")
        
        config_data = load_config(config) if config else {}
        services = config_data.get("services", [])
        
        if not services:
            raise ValueError("No services defined in the configuration.")

        results = []
        for service in services:
            status = check_service_status(service)
            results.append(status)

        result_data = {
            "feature": "MonitorStatus",
            "status": "success",
            "results": results,
            "config_used": config,
            "verbose": verbose
        }
        
        # Output results based on format
        if output == 'json':
            console.print_json(json.dumps(result_data, indent=2))
        elif output == 'table':
            table = Table(title=f"MonitorStatus Results")
            table.add_column("Service", style="cyan")
            table.add_column("Status", style="magenta")
            
            for result in results:
                table.add_row(result["service"], result["status"])
            
            console.print(table)
        else:  # plain
            for result in results:
                console.print(f"{result['service']}: {result['status']}")
        
        if verbose:
            console.print(f"[green]✅ MonitorStatus completed successfully[/green]")
            
    except FileNotFoundError as fnf_error:
        console.print(f"[red]❌ MonitorStatus failed: {str(fnf_error)}[/red]")
        ctx.exit(1)
    except ValueError as ve:
        console.print(f"[red]❌ MonitorStatus failed: {str(ve)}[/red]")
        ctx.exit(1)
    except Exception as e:
        console.print(f"[red]❌ MonitorStatus failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)

# Export command for CLI registration
__all__ = ["monitorstatus"]