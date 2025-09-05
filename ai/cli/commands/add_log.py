import click
from typing import Optional
from rich.console import Console
from rich.table import Table
from pathlib import Path
import json
import logging

console = Console()
logging.basicConfig(level=logging.INFO)

@click.command()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--output', '-o', type=click.Choice(['json', 'table', 'plain']), 
              default='table', help='Output format')
@click.option('--config', type=click.Path(exists=True), help='Configuration file')
@click.argument('log_message', required=True)
@click.pass_context
def add_log(ctx, verbose: bool, output: str, config: Optional[str], log_message: str):
    """
    Add a log entry to the system.
    
    LOG_MESSAGE: The message to log.
    """
    try:
        if verbose:
            console.print(f"[blue]Running add_log command with message: {log_message}...[/blue]")
        
        # Validate log message
        if not log_message:
            raise ValueError("Log message cannot be empty.")
        
        # Load configuration if provided
        config_data = {}
        if config:
            with open(config, 'r') as f:
                config_data = json.load(f)
        
        # Simulate adding log (this could be a database or file operation)
        logging.info(log_message)
        
        result_data = {
            "feature": "add_log",
            "status": "success", 
            "message": "Log entry added successfully",
            "log_message": log_message,
            "config_used": config_data,
            "verbose": verbose
        }
        
        # Output results based on format
        if output == 'json':
            console.print_json(json.dumps(result_data, indent=2))
        elif output == 'table':
            table = Table(title=f"add_log Results")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="magenta")
            
            for key, value in result_data.items():
                table.add_row(str(key), str(value))
            
            console.print(table)
        else:  # plain
            for key, value in result_data.items():
                console.print(f"{key}: {value}")
        
        if verbose:
            console.print(f"[green]✅ add_log completed successfully[/green]")
            
    except Exception as e:
        console.print(f"[red]❌ add_log failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)

# Export command for CLI registration
__all__ = ["add_log"]