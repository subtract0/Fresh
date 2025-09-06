import click
from typing import Optional
from rich.console import Console
from rich.table import Table
from pathlib import Path
import json
import psutil

console = Console()


@click.command()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--output', '-o', type=click.Choice(['json', 'table', 'plain']), 
              default='table', help='Output format')
@click.option('--config', type=click.Path(exists=True), help='Configuration file')
@click.pass_context
def get_memory_analytics(ctx, verbose: bool, output: str, config: Optional[str]):
    """
    get_memory_analytics command.
    This command retrieves memory usage analytics and patterns.
    """
    try:
        if verbose:
            console.print(f"[blue]Running get_memory_analytics command...[/blue]")
        
        # Load configuration if provided
        config_data = {}
        if config:
            with open(config, 'r') as f:
                config_data = json.load(f)
                if verbose:
                    console.print(f"[yellow]Loaded configuration: {config_data}[/yellow]")

        # Gather memory usage statistics
        memory_info = psutil.virtual_memory()
        memory_usage = {
            "total_memory": memory_info.total,
            "available_memory": memory_info.available,
            "used_memory": memory_info.used,
            "memory_percent": memory_info.percent,
            "swap_total": psutil.swap_memory().total,
            "swap_used": psutil.swap_memory().used,
            "swap_free": psutil.swap_memory().free,
            "swap_percent": psutil.swap_memory().percent,
        }
        
        # Output results based on format
        if output == 'json':
            console.print_json(json.dumps(memory_usage, indent=2))
        elif output == 'table':
            table = Table(title=f"Memory Usage Analytics")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="magenta")
            
            for key, value in memory_usage.items():
                table.add_row(str(key), str(value))
            
            console.print(table)
        else:  # plain
            for key, value in memory_usage.items():
                console.print(f"{key}: {value}")
        
        if verbose:
            console.print(f"[green]✅ get_memory_analytics completed successfully[/green]")
            
    except FileNotFoundError as fnf_error:
        console.print(f"[red]❌ Configuration file not found: {str(fnf_error)}[/red]")
        ctx.exit(1)
    except json.JSONDecodeError as json_error:
        console.print(f"[red]❌ Error decoding JSON from configuration: {str(json_error)}[/red]")
        ctx.exit(1)
    except Exception as e:
        console.print(f"[red]❌ get_memory_analytics failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)


# Export command for CLI registration
__all__ = ["get_memory_analytics"]