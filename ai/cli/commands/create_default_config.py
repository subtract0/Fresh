import click
from typing import Optional
from rich.console import Console
from rich.table import Table
from pathlib import Path
import json
import os

console = Console()

DEFAULT_CONFIG = {
    "setting1": "value1",
    "setting2": "value2",
    "setting3": "value3"
}

@click.command()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--output', '-o', type=click.Choice(['json', 'table', 'plain']), 
              default='table', help='Output format')
@click.option('--config', type=click.Path(), help='Configuration file')
@click.pass_context
def create_default_config(ctx, verbose: bool, output: str, config: Optional[str]):
    """
    create_default_config command.
    Generates a default configuration file if one does not exist.
    """
    try:
        if verbose:
            console.print(f"[blue]Running create_default_config command...[/blue]")
        
        if config:
            config_path = Path(config)
            if config_path.exists():
                console.print(f"[yellow]Configuration file already exists: {config}[/yellow]")
                ctx.exit(0)
        else:
            config_path = Path("default_config.json")
        
        with open(config_path, 'w') as config_file:
            json.dump(DEFAULT_CONFIG, config_file, indent=2)
        
        result_data = {
            "feature": "create_default_config",
            "status": "success", 
            "message": f"Default configuration created at {config_path}",
            "config_used": str(config_path),
            "verbose": verbose
        }
        
        # Output results based on format
        if output == 'json':
            console.print_json(json.dumps(result_data, indent=2))
        elif output == 'table':
            table = Table(title=f"create_default_config Results")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="magenta")
            
            for key, value in result_data.items():
                table.add_row(str(key), str(value))
            
            console.print(table)
        else:  # plain
            for key, value in result_data.items():
                console.print(f"{key}: {value}")
        
        if verbose:
            console.print(f"[green]✅ create_default_config completed successfully[/green]")
            
    except Exception as e:
        console.print(f"[red]❌ create_default_config failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)

# Export command for CLI registration
__all__ = ["create_default_config"]