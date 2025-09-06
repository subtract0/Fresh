import click
from typing import Optional
from rich.console import Console
from rich.table import Table
from pathlib import Path
import json
import os

console = Console()


@click.command()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--output', '-o', type=click.Choice(['json', 'table', 'plain']), 
              default='table', help='Output format')
@click.option('--config', type=click.Path(exists=True), help='Configuration file')
@click.pass_context
def load_env_file(ctx, verbose: bool, output: str, config: Optional[str]):
    """
    Load environment variables from a specified configuration file.
    """
    try:
        if verbose:
            console.print(f"[blue]Running load_env_file command...[/blue]")
        
        if config is None:
            raise ValueError("Configuration file must be specified.")
        
        config_path = Path(config)
        if not config_path.is_file():
            raise FileNotFoundError(f"Configuration file '{config}' does not exist.")
        
        with open(config_path) as f:
            env_vars = json.load(f)
        
        for key, value in env_vars.items():
            os.environ[key] = str(value)
        
        result_data = {
            "feature": "load_env_file",
            "status": "success", 
            "message": "Environment variables loaded successfully",
            "config_used": config,
            "verbose": verbose,
            "loaded_variables": list(env_vars.keys())
        }
        
        if output == 'json':
            console.print_json(json.dumps(result_data, indent=2))
        elif output == 'table':
            table = Table(title=f"load_env_file Results")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="magenta")
            
            for key, value in result_data.items():
                table.add_row(str(key), str(value))
            
            console.print(table)
        else:  # plain
            for key, value in result_data.items():
                console.print(f"{key}: {value}")
        
        if verbose:
            console.print(f"[green]✅ load_env_file completed successfully[/green]")
            
    except Exception as e:
        console.print(f"[red]❌ load_env_file failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)


# Export command for CLI registration
__all__ = ["load_env_file"]