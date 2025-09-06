import click
from typing import Optional
from rich.console import Console
from rich.table import Table
from pathlib import Path
import json
import signal
import os
import sys

console = Console()

# Signal handler function
def handle_signal(signum, frame):
    console.print(f"[yellow]Received signal: {signum}. Exiting gracefully...[/yellow]")
    sys.exit(0)

# Register signal handlers
signal.signal(signal.SIGINT, handle_signal)
signal.signal(signal.SIGTERM, handle_signal)

@click.command()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--output', '-o', type=click.Choice(['json', 'table', 'plain']), 
              default='table', help='Output format')
@click.option('--config', type=click.Path(exists=True), help='Configuration file')
@click.pass_context
def signal_handler(ctx, verbose: bool, output: str, config: Optional[str]):
    """
    signal_handler command.
    
    This command sets up signal handling for graceful termination of the application.
    """
    try:
        if verbose:
            console.print(f"[blue]Running signal_handler command...[/blue]")
        
        # Validate configuration file if provided
        if config:
            config_path = Path(config)
            if not config_path.is_file():
                raise FileNotFoundError(f"Configuration file '{config}' does not exist.")
        
        result_data = {
            "feature": "signal_handler",
            "status": "success", 
            "message": "Signal handler is set up and running.",
            "config_used": config,
            "verbose": verbose
        }
        
        # Output results based on format
        if output == 'json':
            console.print_json(json.dumps(result_data, indent=2))
        elif output == 'table':
            table = Table(title=f"signal_handler Results")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="magenta")
            
            for key, value in result_data.items():
                table.add_row(str(key), str(value))
            
            console.print(table)
        else:  # plain
            for key, value in result_data.items():
                console.print(f"{key}: {value}")
        
        if verbose:
            console.print(f"[green]✅ signal_handler completed successfully[/green]")
            
    except FileNotFoundError as fnf_error:
        console.print(f"[red]❌ Error: {str(fnf_error)}[/red]")
        ctx.exit(1)
    except Exception as e:
        console.print(f"[red]❌ signal_handler failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)

# Export command for CLI registration
__all__ = ["signal_handler"]