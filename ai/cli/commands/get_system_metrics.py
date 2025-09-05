import psutil
import click
from typing import Optional
from rich.console import Console
from rich.table import Table
from pathlib import Path
import json

console = Console()


@click.command()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--output', '-o', type=click.Choice(['json', 'table', 'plain']), 
              default='table', help='Output format')
@click.option('--config', type=click.Path(exists=True), help='Configuration file')
@click.pass_context
def get_system_metrics(ctx, verbose: bool, output: str, config: Optional[str]):
    """
    Get system metrics command.
    
    This command retrieves and displays system metrics such as CPU usage, memory usage,
    disk usage, and network statistics.
    """
    try:
        if verbose:
            console.print(f"[blue]Running get_system_metrics command...[/blue]")
        
        # Gather system metrics
        cpu_usage = psutil.cpu_percent(interval=1)
        memory_info = psutil.virtual_memory()
        disk_info = psutil.disk_usage('/')
        network_info = psutil.net_if_stats()

        result_data = {
            "CPU Usage (%)": cpu_usage,
            "Memory Usage (GB)": memory_info.used / (1024 ** 3),
            "Total Memory (GB)": memory_info.total / (1024 ** 3),
            "Disk Usage (%)": disk_info.percent,
            "Total Disk Space (GB)": disk_info.total / (1024 ** 3),
            "Network Interfaces": {iface: stats.isup for iface, stats in network_info.items()},
            "config_used": config,
            "verbose": verbose
        }
        
        # Output results based on format
        if output == 'json':
            console.print_json(json.dumps(result_data, indent=2))
        elif output == 'table':
            table = Table(title=f"get_system_metrics Results")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="magenta")
            
            for key, value in result_data.items():
                table.add_row(str(key), str(value))
            
            console.print(table)
        else:  # plain
            for key, value in result_data.items():
                console.print(f"{key}: {value}")
        
        if verbose:
            console.print(f"[green]✅ get_system_metrics completed successfully[/green]")
            
    except Exception as e:
        console.print(f"[red]❌ get_system_metrics failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)


# Export command for CLI registration
__all__ = ["get_system_metrics"]