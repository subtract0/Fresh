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
def save_config(ctx, verbose: bool, output: str, config: Optional[str]):
    """
    save_config command.
    
    Saves the configuration to the specified file format.
    """
    try:
        if verbose:
            console.print(f"[blue]Running save_config command...[/blue]")
        
        if config is None:
            raise ValueError("Configuration file must be specified.")
        
        config_path = Path(config)
        if not config_path.is_file():
            raise FileNotFoundError(f"Configuration file '{config}' does not exist.")
        
        with open(config_path, 'r') as f:
            config_data = json.load(f)

        save_path = config_path.with_suffix('.json')
        with open(save_path, 'w') as f:
            json.dump(config_data, f, indent=2)

        result_data = {
            "feature": "save_config",
            "status": "success", 
            "message": f"Configuration saved to '{save_path}'",
            "config_used": str(config_path),
            "verbose": verbose
        }
        
        # Output results based on format
        if output == 'json':
            console.print_json(json.dumps(result_data, indent=2))
        elif output == 'table':
            table = Table(title=f"save_config Results")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="magenta")
            
            for key, value in result_data.items():
                table.add_row(str(key), str(value))
            
            console.print(table)
        else:  # plain
            for key, value in result_data.items():
                console.print(f"{key}: {value}")
        
        if verbose:
            console.print(f"[green]✅ save_config completed successfully[/green]")
            
    except Exception as e:
        console.print(f"[red]❌ save_config failed: {str(e)}[/red]")
        if verbose:
            console.print_exception()
        ctx.exit(1)


# Export command for CLI registration
__all__ = ["save_config"]