import click
from typing import Optional
from rich.console import Console
from rich.table import Table
from pathlib import Path
import json
import os

console = Console()

def load_config(config_path: str) -> dict:
    """
    Load configuration from a JSON file.

    Args:
        config_path (str): Path to the configuration file.

    Returns:
        dict: Loaded configuration data.

    Raises:
        FileNotFoundError: If the configuration file does not exist.
        json.JSONDecodeError: If the configuration file is not valid JSON.
    """
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Configuration file '{config_path}' not found.")
    
    with open(config_path, 'r') as f:
        return json.load(f)

def consolidate_memory(config: dict) -> dict:
    """
    Consolidate memory based on the provided configuration.

    Args:
        config (dict): Configuration data containing memory settings.

    Returns:
        dict: Result of the memory consolidation process.

    Raises:
        ValueError: If 'memory_limit' is not present in the configuration.
    """
    if 'memory_limit' not in config:
        raise ValueError("Configuration must include 'memory_limit'")
    
    memory_limit = config['memory_limit']
    # Simulate memory consolidation process
    return {
        "consolidated_memory": memory_limit * 0.8,  # Example calculation
        "status": "success"
    }

@click.command()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--output', '-o', type=click.Choice(['json', 'table', 'plain']), 
              default='table', help='Output format')
@click.option('--config', type=click.Path(exists=True), help='Configuration file')
@click.pass_context
def memoryconsolidation(ctx, verbose: bool, output: str, config: Optional[str]):
    """
    MemoryConsolidation command.
    Consolidates memory based on the provided configuration.

    Args:
        ctx: Click context.
        verbose (bool): Flag to enable verbose output.
        output (str): Desired output format.
        config (Optional[str]): Path to the configuration file.
    """
    try:
        if verbose:
            console.print(f"[blue]Running MemoryConsolidation command...[/blue]")
        
        if config is None:
            raise ValueError("Configuration file must be provided.")
        
        config_data = load_config(config)
        
        if verbose:
            console.print(f"[yellow]Loaded configuration: {config_data}[/yellow]")
        
        result = consolidate_memory(config_data)
        
        result_data = {
            "feature": "MemoryConsolidation",
            "status": result["status"],
            "consolidated_memory": result["consolidated_memory"],
            "config_used": config,
            "verbose": verbose
        }
        
        # Output results based on format
        if output == 'json':
            console.print_json(json.dumps(result_data, indent=2))
        elif output == 'table':
            table = Table(title=f"MemoryConsolidation Results")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="magenta")
            
            for key, value in result_data.items():
                table.add_row(str(key), str(value))
            
            console.print(table)
        else:  # plain
            for key, value in result_data.items():
                console.print(f"{key}: {value}")
        
        if verbose:
            console.print(f"[green]✅ MemoryConsolidation completed successfully[/green]")
            
    except Exception as e:
        console.print(f"[red]❌ MemoryConsolidation failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)

# Export command for CLI registration
__all__ = ["memoryconsolidation"]