import click
from typing import Optional
from rich.console import Console
from rich.table import Table
from pathlib import Path
import json
import os
import psutil

console = Console()


@click.command()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--output', '-o', type=click.Choice(['json', 'table', 'plain']), 
              default='table', help='Output format')
@click.option('--config', type=click.Path(exists=True), help='Configuration file')
@click.pass_context
def cmd_health(ctx, verbose: bool, output: Optional[str], config: Optional[str]):
    """
    cmd_health command to check the health of the application.
    """
    try:
        if verbose:
            console.print(f"[blue]Running cmd_health command...[/blue]")
        
        # Validate configuration file if provided
        if config:
            if not Path(config).is_file():
                raise FileNotFoundError(f"Configuration file '{config}' does not exist.")
        
        # Gather health metrics
        cpu_usage = psutil.cpu_percent(interval=1)
        memory_info = psutil.virtual_memory()
        disk_info = psutil.disk_usage('/')
        
        result_data = {
            "feature": "cmd_health",
            "status": "healthy", 
            "cpu_usage_percent": cpu_usage,
            "memory_usage_percent": memory_info.percent,
            "disk_usage_percent": disk_info.percent,
            "config_used": config,
            "verbose": verbose
        }
        
        # Output results based on format
        if output == 'json':
            console.print_json(json.dumps(result_data, indent=2))
        elif output == 'table':
            table = Table(title=f"cmd_health Results")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="magenta")
            
            for key, value in result_data.items():
                table.add_row(str(key), str(value))
            
            console.print(table)
        else:  # plain
            for key, value in result_data.items():
                console.print(f"{key}: {value}")
        
        if verbose:
            console.print(f"[green]✅ cmd_health completed successfully[/green]")
            
    except Exception as e:
        console.print(f"[red]❌ cmd_health failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)


# Export command for CLI registration
__all__ = ["cmd_health"]