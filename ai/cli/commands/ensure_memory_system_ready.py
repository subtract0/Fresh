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

def check_memory_system(config):
    # Simulated check for memory system readiness
    if 'memory_system' not in config:
        raise ValueError("Configuration must include 'memory_system' settings.")
    return {"status": "ready", "details": "Memory system is operational."}

@click.command()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--output', '-o', type=click.Choice(['json', 'table', 'plain']), 
              default='table', help='Output format')
@click.option('--config', type=click.Path(exists=True), help='Configuration file', required=True)
@click.pass_context
def ensure_memory_system_ready(ctx, verbose: bool, output: str, config: str):
    """
    ensure_memory_system_ready command.
    Checks if the memory system is ready based on the provided configuration.
    """
    try:
        if verbose:
            console.print(f"[blue]Running ensure_memory_system_ready command...[/blue]")
        
        # Load configuration
        config_data = load_config(config)
        
        # Check memory system readiness
        result = check_memory_system(config_data)
        
        result_data = {
            "feature": "ensure_memory_system_ready",
            "status": result["status"], 
            "message": result["details"],
            "config_used": config,
            "verbose": verbose
        }
        
        # Output results based on format
        if output == 'json':
            console.print_json(json.dumps(result_data, indent=2))
        elif output == 'table':
            table = Table(title=f"ensure_memory_system_ready Results")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="magenta")
            
            for key, value in result_data.items():
                table.add_row(str(key), str(value))
            
            console.print(table)
        else:  # plain
            for key, value in result_data.items():
                console.print(f"{key}: {value}")
        
        if verbose:
            console.print(f"[green]✅ ensure_memory_system_ready completed successfully[/green]")
            
    except FileNotFoundError:
        console.print(f"[red]❌ Configuration file not found: {config}[/red]")
        ctx.exit(1)
    except ValueError as ve:
        console.print(f"[red]❌ Configuration error: {str(ve)}[/red]")
        ctx.exit(1)
    except Exception as e:
        console.print(f"[red]❌ ensure_memory_system_ready failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)

# Export command for CLI registration
__all__ = ["ensure_memory_system_ready"]